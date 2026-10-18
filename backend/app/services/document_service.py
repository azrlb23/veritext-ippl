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
    async def save_uploaded_file(
        db: AsyncSession, user_id: uuid.UUID, file: UploadFile
    ) -> Document:
        DocumentService.validate_file(file)

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty (0 bytes). Please upload a valid document.",
            )

        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB",
            )

        # Calculate sha256
        sha256 = hashlib.sha256(content).hexdigest()

        # Prepare safe unique filename
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "txt"
        stored_filename = f"{uuid.uuid4().hex}.{ext}"

        # Ensure upload dir exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

        with open(file_path, "wb") as f:
            f.write(content)

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

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Berkas naskah kosong (0 bytes). Silakan unggah dokumen yang valid.",
            )

        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB",
            )

        # Check and debit user token wallet
        token_cost = 1 if audit_depth == "TIER1_ONLY" else 2
        wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == user_id)
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

        # Calculate sha256
        sha256 = hashlib.sha256(content).hexdigest()

        # Prepare safe unique filename
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "txt"
        stored_filename = f"{uuid.uuid4().hex}.{ext}"

        # Ensure upload dir exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

        with open(file_path, "wb") as f:
            f.write(content)

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

        # Dispatch Celery worker task asynchronously
        try:
            from app.workers.tasks import preprocess_and_audit
            celery_res = preprocess_and_audit.delay(str(task.id), str(doc.id))
            task.celery_task_id = celery_res.id
        except Exception:
            task.celery_task_id = f"simulated-{uuid.uuid4().hex}"
            # Graceful local execution fallback so 4-tier engine executes even without active Celery worker
            try:
                import threading
                from app.workers.tasks import execute_audit_pipeline
                from app.core.database import SyncSessionLocal

                def _bg_run(t_id=str(task.id), d_id=str(doc.id)):
                    s = SyncSessionLocal()
                    try:
                        execute_audit_pipeline(s, t_id, d_id)
                    finally:
                        s.close()

                threading.Thread(target=_bg_run, daemon=True).start()
            except Exception:
                pass

        await db.commit()
        await db.refresh(doc)
        await db.refresh(task)
        return doc, task
