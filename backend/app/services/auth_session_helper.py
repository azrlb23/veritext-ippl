from __future__ import annotations

import contextlib
import os

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.audit import AuditReport, AuditSentence, AuditTask
from app.models.audit_log import AuditLog
from app.models.corpus import CorpusDocument
from app.models.document import Document
from app.models.invoice import Invoice
from app.models.password_reset import PasswordReset
from app.models.session import Session
from app.models.user import User
from app.models.wallet import TokenTransaction, TokenWallet


async def purge_user_account(db: AsyncSession, user: User) -> None:
    if user.role == "ADMIN" and user.is_active:
        admin_count_stmt = select(func.count(User.id)).where(User.role == "ADMIN", User.is_active == True)
        active_admins = (await db.execute(admin_count_stmt)).scalar() or 0
        if active_admins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate or delete the last active administrator",
            )

    doc_stmt = select(Document).where(Document.user_id == user.id)
    docs_res = await db.execute(doc_stmt)
    user_docs = docs_res.scalars().all() if hasattr(docs_res, "scalars") else []
    user_doc_ids = [getattr(d, "id", None) for d in user_docs if getattr(d, "id", None) is not None and isinstance(d, Document)]
    for doc in user_docs:
        stored_fn = getattr(doc, "stored_filename", None)
        if stored_fn:
            file_path = os.path.join(settings.UPLOAD_DIR, stored_fn)
            if os.path.exists(file_path):
                with contextlib.suppress(OSError):
                    os.remove(file_path)

    if user_doc_ids:
        task_stmt = select(AuditTask).where((AuditTask.user_id == user.id) | (AuditTask.document_id.in_(user_doc_ids)))
    else:
        task_stmt = select(AuditTask).where(AuditTask.user_id == user.id)
    task_res = await db.execute(task_stmt)
    user_tasks = task_res.scalars().all() if hasattr(task_res, "scalars") else []
    task_ids = [getattr(t, "id", None) for t in user_tasks if getattr(t, "id", None) is not None and isinstance(t, AuditTask)]

    if task_ids:
        await db.execute(delete(AuditReport).where(AuditReport.audit_task_id.in_(task_ids)))
        await db.execute(delete(AuditSentence).where(AuditSentence.audit_task_id.in_(task_ids)))
        await db.execute(delete(AuditTask).where(AuditTask.id.in_(task_ids)))

    await db.execute(delete(Document).where(Document.user_id == user.id))
    await db.execute(delete(Session).where(Session.user_id == user.id))

    with contextlib.suppress(Exception):
        await db.execute(delete(PasswordReset).where(PasswordReset.user_id == user.id))

    with contextlib.suppress(Exception):
        await db.execute(delete(Invoice).where(Invoice.user_id == user.id))

    wallet_res = await db.execute(select(TokenWallet).where(TokenWallet.user_id == user.id))
    wallets = wallet_res.scalars().all() if hasattr(wallet_res, "scalars") else []
    if not wallets and hasattr(wallet_res, "scalar_one_or_none"):
        single_w = wallet_res.scalar_one_or_none()
        if single_w:
            wallets = [single_w]
    wallet_ids = [getattr(w, "id", None) for w in wallets if getattr(w, "id", None) is not None and isinstance(w, TokenWallet)]
    if wallet_ids:
        await db.execute(delete(TokenTransaction).where(TokenTransaction.wallet_id.in_(wallet_ids)))
    for w in wallets:
        if w and isinstance(w, TokenWallet):
            await db.delete(w)

    with contextlib.suppress(Exception):
        await db.execute(update(CorpusDocument).where(CorpusDocument.uploaded_by == user.id).values(uploaded_by=None))

    await db.execute(update(AuditLog).where(AuditLog.actor_id == user.id).values(actor_id=None))
    await db.delete(user)
    await db.commit()
