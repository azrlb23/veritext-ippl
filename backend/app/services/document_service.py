from __future__ import annotations

import contextlib
import os
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.audit import AuditTask
from app.models.document import Document
from app.models.wallet import TokenTransaction, TokenWallet
from app.services.document_validator import validate_file, write_upload_stream


class DocumentService:
    validate_file = staticmethod(validate_file)
    _write_upload_stream = staticmethod(write_upload_stream)

    @staticmethod
    async def save_uploaded_file(db: AsyncSession, user_id: uuid.UUID, file: UploadFile) -> Document:
        validate_file(file)
        stored_fn, file_size, sha256 = await write_upload_stream(
            file, "File is empty (0 bytes). Please upload a valid document."
        )
        doc = Document(
            user_id=user_id,
            original_filename=file.filename or "document.txt",
            stored_filename=stored_fn,
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
        db: AsyncSession, user_id: uuid.UUID, file: UploadFile, audit_depth: str = "FULL"
    ) -> tuple[Document, AuditTask]:
        validate_file(file)
        token_cost = 1 if audit_depth == "TIER1_ONLY" else 2
        wallet = (await db.execute(select(TokenWallet).where(TokenWallet.user_id == user_id).with_for_update())).scalar_one_or_none()

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

        stored_fn, file_size, sha256 = await write_upload_stream(
            file, "Berkas naskah kosong (0 bytes). Silakan unggah dokumen yang valid."
        )
        doc = Document(
            user_id=user_id,
            original_filename=file.filename or "document.txt",
            stored_filename=stored_fn,
            file_size_bytes=file_size,
            mime_type=file.content_type or "application/octet-stream",
            sha256_hash=sha256,
            status="READY",
        )
        db.add(doc)
        await db.flush()

        task = AuditTask(
            document_id=doc.id, user_id=user_id, audit_depth=audit_depth, status="QUEUED", progress_pct=0, current_stage="INITIALIZING"
        )
        db.add(task)
        await db.flush()

        tx = TokenTransaction(
            wallet_id=wallet.id, transaction_type="DEBIT_AUDIT", amount=-token_cost,
            balance_after=wallet.balance, reference_id=task.id, note=f"Audit execution for document {doc.original_filename}",
        )
        db.add(tx)

        with contextlib.suppress(Exception):
            from app.workers.celery_app import celery_app
            from app.workers.tasks import preprocess_and_audit
            inspect = celery_app.control.inspect(timeout=0.3)
            active_workers = inspect.ping() if inspect else None
            if active_workers:
                celery_res = preprocess_and_audit.delay(str(task.id), str(doc.id))
                task.celery_task_id = celery_res.id
            else:
                with contextlib.suppress(Exception):
                    celery_res = preprocess_and_audit.delay(str(task.id), str(doc.id))
                    task.celery_task_id = celery_res.id

        await db.commit()
        await db.refresh(doc)
        await db.refresh(task)
        return doc, task

    @staticmethod
    async def delete_document(db: AsyncSession, doc: Document) -> None:
        if doc.stored_filename:
            file_path = os.path.join(settings.UPLOAD_DIR, doc.stored_filename)
            if os.path.exists(file_path):
                with contextlib.suppress(OSError):
                    os.remove(file_path)

        doc.status = "DELETED"
        doc.deleted_at = datetime.now(timezone.utc)  # noqa: UP017
        await db.commit()
