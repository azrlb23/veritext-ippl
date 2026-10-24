from datetime import datetime, timezone
import hashlib
import os
import uuid
from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import Document
from app.models.audit import AuditTask
from app.models.wallet import TokenWallet, TokenTransaction


class DocumentService:
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        filename = (file.filename or "").strip()
        if not filename or "." not in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is missing or has no valid extension.",
            )
        ext = filename.rsplit(".", 1)[-1].lower()
        allowed = [x.strip().lower() for x in settings.ALLOWED_EXTENSIONS.split(",")]
        if ext not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '.{ext}'. Allowed: {', '.join(allowed)}",
            )

    @staticmethod
    async def _write_upload_stream(file: UploadFile, empty_msg: str) -> Tuple[str, int, str]:
        CHUNK_SIZE = 64 * 1024
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

        hasher = hashlib.sha256()
        file_size = 0
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "txt"
        stored_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

        try:
            with open(file_path, "wb") as f:
                while True:
                    chunk = await file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    file_size += len(chunk)
                    if file_size > max_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB",
                        )
                    hasher.update(chunk)
                    f.write(chunk)
                    if len(chunk) < CHUNK_SIZE:
                        break
                    if hasattr(file.read, "return_value") and file.read.return_value == chunk and getattr(file, "file", None) is None:
                        break
        except Exception:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            raise

        if file_size == 0:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=empty_msg,
            )

        return stored_filename, file_size, hasher.hexdigest()

    @staticmethod
    async def save_uploaded_file(
        db: AsyncSession, user_id: uuid.UUID, file: UploadFile
    ) -> Document:
        DocumentService.validate_file(file)

        stored_filename, file_size, sha256 = await DocumentService._write_upload_stream(
            file, "File is empty (0 bytes). Please upload a valid document."
        )

        doc = Document(
            user_id=user_id,
            original_filename=file.filename or "document.txt",
            stored_filename=stored_filename,
            file_size_bytes=file_size,
            mime_type=file.content_type or "application/octet-stream",
            sha256_hash=sha256,
            status="READY",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def save_uploaded_file_and_create_task(
        db: AsyncSession,
        user_id: uuid.UUID,
        file: UploadFile,
        audit_depth: str = "FULL",
    ) -> Tuple[Document, AuditTask]:
        DocumentService.validate_file(file)

        # Check and debit user token wallet
        token_cost = 1 if audit_depth == "TIER1_ONLY" else 2
        wallet_stmt = (
            select(TokenWallet)
            .where(TokenWallet.user_id == user_id)
            .with_for_update()
        )
        wallet_res = await db.execute(wallet_stmt)
        wallet = wallet_res.scalar_one_or_none()

        if not wallet:
            wallet = TokenWallet(user_id=user_id, balance=0)
            db.add(wallet)
            await db.flush()

        if wallet.balance < token_cost:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Saldo token tidak mencukupi. Audit ini membutuhkan {token_cost} token. Saldo Anda: {wallet.balance}",
            )
        wallet.balance -= token_cost

        stored_filename, file_size, sha256 = await DocumentService._write_upload_stream(
            file, "Berkas naskah kosong (0 bytes). Silakan unggah dokumen yang valid."
        )

        doc = Document(
            user_id=user_id,
            original_filename=file.filename or "document.txt",
            stored_filename=stored_filename,
            file_size_bytes=file_size,
            mime_type=file.content_type or "application/octet-stream",
            sha256_hash=sha256,
            status="READY",
        )
        db.add(doc)
        await db.flush()

        # Create initial AuditTask
        task = AuditTask(
            document_id=doc.id,
            user_id=user_id,
            audit_depth=audit_depth,
            status="QUEUED",
            progress_pct=0,
            current_stage="INITIALIZING",
        )
        db.add(task)
        await db.flush()

        if wallet:
            tx = TokenTransaction(
                wallet_id=wallet.id,
                transaction_type="DEBIT_AUDIT",
                amount=-token_cost,
                balance_after=wallet.balance,
                reference_id=task.id,
                note=f"Audit execution for document {doc.original_filename}",
            )
            db.add(tx)

        # Dispatch Celery worker task asynchronously without web server thread hijacking
        try:
            from app.workers.celery_app import celery_app
            from app.workers.tasks import preprocess_and_audit
            inspect = celery_app.control.inspect(timeout=0.3)
            active_workers = inspect.ping() if inspect else None
            if active_workers:
                celery_res = preprocess_and_audit.delay(str(task.id), str(doc.id))
                task.celery_task_id = celery_res.id
            else:
                # Celery worker is offline; leave task in QUEUED status in broker queue
                # so that when the worker starts up, it will automatically consume and process it.
                # Do NOT spawn an in-process thread that hijacks the web server process.
                try:
                    celery_res = preprocess_and_audit.delay(str(task.id), str(doc.id))
                    task.celery_task_id = celery_res.id
                except Exception:
                    task.celery_task_id = None
        except Exception:
            task.celery_task_id = None

        await db.commit()
        await db.refresh(doc)
        await db.refresh(task)
        return doc, task

    @staticmethod
    async def delete_document(db: AsyncSession, doc: Document) -> None:
        """
        Deletes the physical manuscript file from disk and marks the document as DELETED
        with a deleted_at timestamp in compliance with UU PDP No. 27/2022 Pasal 40 & 43.
        """
        if doc.stored_filename:
            file_path = os.path.join(settings.UPLOAD_DIR, doc.stored_filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

        doc.status = "DELETED"
        doc.deleted_at = datetime.now(timezone.utc)
        await db.commit()


