from datetime import datetime, timezone
from typing import Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditTask, AuditReport
from app.models.document import Document
from app.models.wallet import TokenWallet, TokenTransaction
from app.schemas.audit import AuditStartRequest


class AuditService:
    @staticmethod
    async def create_audit_task(
        db: AsyncSession, user_id: uuid.UUID, req: AuditStartRequest
    ) -> AuditTask:
        # Check document ownership and readiness
        doc_stmt = select(Document).where(Document.id == req.document_id, Document.user_id == user_id)
        doc_res = await db.execute(doc_stmt)
        document = doc_res.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied",
            )

        # Check and debit user token wallet
        wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == user_id)
        wallet_res = await db.execute(wallet_stmt)
        wallet = wallet_res.scalar_one_or_none()

        token_cost = 1 if req.audit_depth == "TIER1_ONLY" else 2
        if not wallet or wallet.balance < token_cost:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient token balance. This audit requires {token_cost} token(s). Current balance: {wallet.balance if wallet else 0}",
            )

        # Deduct tokens
        wallet.balance -= token_cost

        # Create audit task
        task = AuditTask(
            document_id=document.id,
            user_id=user_id,
            audit_depth=req.audit_depth,
            status="QUEUED",
            progress_pct=0,
            current_stage="INITIALIZING",
        )
        db.add(task)
        await db.flush()

        # Record wallet transaction
        tx = TokenTransaction(
            wallet_id=wallet.id,
            transaction_type="DEBIT_AUDIT",
            amount=-token_cost,
            balance_after=wallet.balance,
            reference_id=task.id,
            note=f"Audit execution for document {document.original_filename}",
        )
        db.add(tx)

        # Dispatch Celery worker task asynchronously
        try:
            from app.workers.tasks import preprocess_and_audit
            celery_res = preprocess_and_audit.delay(str(task.id), str(document.id))
            task.celery_task_id = celery_res.id
        except Exception:
            # Fallback if celery is not connected in current test run
            task.celery_task_id = f"simulated-{uuid.uuid4().hex}"
            try:
                import threading
                from app.workers.tasks import execute_audit_pipeline
                from app.core.database import SyncSessionLocal

                def _bg_run(t_id=str(task.id), d_id=str(document.id)):
                    s = SyncSessionLocal()
                    try:
                        execute_audit_pipeline(s, t_id, d_id)
                    finally:
                        s.close()

                threading.Thread(target=_bg_run, daemon=True).start()
            except Exception:
                pass

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_task_status(
        db: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID
    ) -> AuditTask:
        from sqlalchemy.orm import selectinload
        stmt = (
            select(AuditTask)
            .options(selectinload(AuditTask.document), selectinload(AuditTask.report))
            .where(AuditTask.id == task_id, AuditTask.user_id == user_id)
        )
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit task not found",
            )
        return task

    @staticmethod
    async def cancel_task(
        db: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        stmt = select(AuditTask).where(AuditTask.id == task_id, AuditTask.user_id == user_id)
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit task not found")

        if task.status not in ("QUEUED", "PROCESSING"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel task in '{task.status}' state",
            )

        task.status = "CANCELLED"
        task.completed_at = datetime.now(timezone.utc)

        # Attempt revoke in Celery
        if task.celery_task_id:
            try:
                from app.workers.celery_app import celery_app
                celery_app.control.revoke(task.celery_task_id, terminate=True)
            except Exception:
                pass

        await db.commit()
        return True

    @staticmethod
    def execute_audit_sync(task_id: uuid.UUID, document_id: uuid.UUID, db_session=None):
        """Directly executes the 4-tier audit pipeline synchronously."""
        from app.workers.tasks import execute_audit_pipeline
        from app.core.database import get_sync_db
        if db_session:
            return execute_audit_pipeline(db_session, str(task_id), str(document_id))
        else:
            with get_sync_db() as sync_db:
                return execute_audit_pipeline(sync_db, str(task_id), str(document_id))
