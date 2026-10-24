from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security import get_password_hash, verify_password, create_access_token, hash_token
from app.models.user import User
from app.models.session import Session
from app.models.wallet import TokenWallet
from app.schemas.auth import UserRegisterRequest, UserLoginRequest


class AuthService:
    @staticmethod
    async def register_user(
        db: AsyncSession, req: UserRegisterRequest, user_agent: Optional[str] = None, ip_address: Optional[str] = None
    ) -> tuple[User, str, str]:
        # Check existing email
        stmt = select(User).where(User.email == req.email.lower().strip())
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered in the system",
            )

        hashed = get_password_hash(req.password)
        new_user = User(
            full_name=req.full_name,
            email=req.email.lower().strip(),
            institution=req.institution,
            password_hash=hashed,
            role="TRIAL",
            is_active=True,
        )
        db.add(new_user)
        await db.flush()

        # Initialize trial token wallet with 5 free trial tokens
        wallet = TokenWallet(user_id=new_user.id, balance=5)
        db.add(wallet)
        await db.flush()

        from app.core.security import create_refresh_token
        access_token = create_access_token(subject=str(new_user.id), role=new_user.role)
        refresh_token = create_refresh_token(subject=str(new_user.id))

        from datetime import timedelta
        from app.core.config import settings
        session_obj = Session(
            user_id=new_user.id,
            refresh_token_hash=hash_token(refresh_token),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(session_obj)
        await db.commit()
        await db.refresh(new_user)
        return new_user, access_token, refresh_token

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, req: UserLoginRequest, user_agent: Optional[str] = None, ip_address: Optional[str] = None
    ) -> tuple[User, str, str]:
        email_clean = req.email.lower().strip()
        stmt = select(User).where(User.email == email_clean)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        now = datetime.now(timezone.utc)
        if user.lockout_until:
            lockout_time = user.lockout_until if user.lockout_until.tzinfo else user.lockout_until.replace(tzinfo=timezone.utc)
            if lockout_time > now:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Account is temporarily locked due to multiple failed login attempts. Please try again later.",
                )
            else:
                user.failed_login_count = 0
                user.lockout_until = None

        if not verify_password(req.password, user.password_hash):
            user.failed_login_count = (user.failed_login_count or 0) + 1
            if user.failed_login_count >= 5:
                user.lockout_until = now + timedelta(minutes=15)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is currently inactive or suspended",
            )

        # Successful authentication: reset lockout and failed count
        user.failed_login_count = 0
        user.lockout_until = None

        access_token = create_access_token(subject=str(user.id), role=user.role)
        from app.core.security import create_refresh_token
        refresh_token = create_refresh_token(subject=str(user.id))

        # Store session
        from app.core.config import settings
        session_obj = Session(
            user_id=user.id,
            refresh_token_hash=hash_token(refresh_token),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(session_obj)
        await db.commit()

        return user, access_token, refresh_token

    @staticmethod
    async def delete_user_account(db: AsyncSession, user: User) -> None:
        """
        Deletes a user account and purges all personal data & files in compliance with
        UU PDP No. 27/2022 Pasal 8 (Right to Erasure) and prevents FK constraint 500 errors.
        Also enforces admin self-lockout protection.
        """
        import os
        from sqlalchemy import delete, func, select, update
        from app.core.config import settings
        from app.models.audit import AuditReport, AuditSentence, AuditTask
        from app.models.audit_log import AuditLog
        from app.models.corpus import CorpusDocument
        from app.models.document import Document
        from app.models.invoice import Invoice
        from app.models.password_reset import PasswordReset
        from app.models.session import Session
        from app.models.wallet import TokenTransaction, TokenWallet

        # 1. Admin self-lockout protection: Cannot delete the last active administrator
        if user.role == "ADMIN" and user.is_active:
            admin_count_stmt = select(func.count(User.id)).where(User.role == "ADMIN", User.is_active == True)
            active_admins = (await db.execute(admin_count_stmt)).scalar() or 0
            if active_admins <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate or delete the last active administrator",
                )

        # 2. Purge physical files on disk for user's documents
        doc_stmt = select(Document).where(Document.user_id == user.id)
        docs_res = await db.execute(doc_stmt)
        user_docs = docs_res.scalars().all() if hasattr(docs_res, "scalars") else []
        user_doc_ids = [getattr(d, "id", None) for d in user_docs if getattr(d, "id", None) is not None]
        for doc in user_docs:
            stored_fn = getattr(doc, "stored_filename", None)
            if stored_fn:
                file_path = os.path.join(settings.UPLOAD_DIR, stored_fn)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass

        # 3. Clean up audit tasks and child records
        if user_doc_ids:
            task_stmt = select(AuditTask).where((AuditTask.user_id == user.id) | (AuditTask.document_id.in_(user_doc_ids)))
        else:
            task_stmt = select(AuditTask).where(AuditTask.user_id == user.id)
        task_res = await db.execute(task_stmt)
        user_tasks = task_res.scalars().all() if hasattr(task_res, "scalars") else []
        task_ids = [getattr(t, "id", None) for t in user_tasks if getattr(t, "id", None) is not None]
        if task_ids:
            await db.execute(delete(AuditReport).where(AuditReport.audit_task_id.in_(task_ids)))
            await db.execute(delete(AuditSentence).where(AuditSentence.audit_task_id.in_(task_ids)))
            await db.execute(delete(AuditTask).where(AuditTask.id.in_(task_ids)))

        # 4. Clean up Documents
        await db.execute(delete(Document).where(Document.user_id == user.id))

        # 5. Clean up Sessions
        await db.execute(delete(Session).where(Session.user_id == user.id))

        # 6. Clean up PasswordReset
        try:
            await db.execute(delete(PasswordReset).where(PasswordReset.user_id == user.id))
        except Exception:
            pass

        # 7. Clean up Invoices
        try:
            await db.execute(delete(Invoice).where(Invoice.user_id == user.id))
        except Exception:
            pass

        # 8. Clean up TokenWallet and TokenTransaction
        wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == user.id)
        wallet_res = await db.execute(wallet_stmt)
        wallets = wallet_res.scalars().all() if hasattr(wallet_res, "scalars") else []
        if not wallets and hasattr(wallet_res, "scalar_one_or_none"):
            single_w = wallet_res.scalar_one_or_none()
            if single_w:
                wallets = [single_w]
        wallet_ids = [getattr(w, "id", None) for w in wallets if getattr(w, "id", None) is not None]
        if wallet_ids:
            await db.execute(delete(TokenTransaction).where(TokenTransaction.wallet_id.in_(wallet_ids)))
        for w in wallets:
            if w:
                await db.delete(w)

        # 9. Anonymize Corpus Documents (preserve institutional corpus while removing contributor identity)
        try:
            await db.execute(update(CorpusDocument).where(CorpusDocument.uploaded_by == user.id).values(uploaded_by=None))
        except Exception:
            pass

        # 10. Anonymize AuditLogs (preserve non-repudiation forensic record with actor_id = NULL)
        await db.execute(update(AuditLog).where(AuditLog.actor_id == user.id).values(actor_id=None))

        # 11. Delete User entity
        await db.delete(user)
        await db.commit()

