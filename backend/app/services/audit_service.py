from __future__ import annotations

import contextlib
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditTask
from app.models.document import Document
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.audit import AuditStartRequest
from app.services.token_pricing import compute_audit_cost, ensure_within_plan
from app.services.upload_charging import debit_wallet
from app.services.word_counter import document_word_count


class AuditService:
    @staticmethod
    async def create_audit_task(
        db: AsyncSession, user_id: uuid.UUID, req: AuditStartRequest, user_role: str | None = None
    ) -> AuditTask:
        doc = (await db.execute(select(Document).where(Document.id == req.document_id, Document.user_id == user_id))).scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or access denied")
        if doc.status == "DELETED" or doc.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot audit a deleted document")

        words = document_word_count(doc)
        ensure_within_plan(user_role, words)
        token_cost = compute_audit_cost(words)
        wallet = await debit_wallet(db, user_id, token_cost)
        task = AuditTask(
            document_id=doc.id, user_id=user_id, audit_depth=req.audit_depth, status="QUEUED", progress_pct=0, current_stage="INITIALIZING"
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
        await db.refresh(task)
        return task

    @staticmethod
    async def get_task_status(db: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID) -> AuditTask:
        stmt = (
            select(AuditTask)
            .options(selectinload(AuditTask.document), selectinload(AuditTask.report))
            .where(AuditTask.id == task_id, AuditTask.user_id == user_id)
        )
        task = (await db.execute(stmt)).scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit task not found")
        return task

    @staticmethod
    async def cancel_task(db: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = select(AuditTask).where(AuditTask.id == task_id, AuditTask.user_id == user_id)
        task = (await db.execute(stmt)).scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit task not found")
        if task.status not in ("QUEUED", "PROCESSING"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel task in '{task.status}' state")

        task.status = "CANCELLED"
        task.completed_at = datetime.now(timezone.utc)  # noqa: UP017

        if task.celery_task_id:
            with contextlib.suppress(Exception):
                from app.workers.celery_app import celery_app
                celery_app.control.revoke(task.celery_task_id, terminate=True)

        wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == user_id).with_for_update()
        wallet = (await db.execute(wallet_stmt)).scalar_one_or_none()
        refund_amount = 1 if getattr(task, "audit_depth", "FULL") == "TIER1_ONLY" else 2
        if wallet:
            wallet.balance += refund_amount
            tx = TokenTransaction(
                wallet_id=wallet.id, transaction_type="CREDIT_REFUND", amount=refund_amount,
                balance_after=wallet.balance, reference_id=task.id, note=f"Automatic refund for cancelled audit task {task.id}",
            )
            db.add(tx)

        await db.commit()
        return True

    @staticmethod
    def execute_audit_sync(task_id: uuid.UUID, document_id: uuid.UUID, db_session=None):
        from app.core.database import get_sync_db
        from app.workers.tasks import execute_audit_pipeline
        if db_session:
            return execute_audit_pipeline(db_session, str(task_id), str(document_id))
        with get_sync_db() as sync_db:
            return execute_audit_pipeline(sync_db, str(task_id), str(document_id))
