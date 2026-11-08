from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.models.session import Session
from app.models.user import User
from app.models.wallet import TokenWallet
from app.schemas.auth import UserLoginRequest, UserRegisterRequest
from app.services.auth_session_helper import purge_user_account


class AuthService:
    delete_user_account = staticmethod(purge_user_account)

    @staticmethod
    async def register_user(
        db: AsyncSession, req: UserRegisterRequest, user_agent: str | None = None, ip_address: str | None = None
    ) -> tuple[User, str, str]:
        stmt = select(User).where(User.email == req.email.lower().strip())
        if (await db.execute(stmt)).scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered in the system")

        hashed = get_password_hash(req.password)
        new_user = User(
            full_name=req.full_name, email=req.email.lower().strip(),
            password_hash=hashed, role="FREE", is_active=True,
        )
        db.add(new_user)
        await db.flush()

        wallet = TokenWallet(user_id=new_user.id, balance=5)
        db.add(wallet)
        await db.flush()

        access_token = create_access_token(subject=str(new_user.id), role=new_user.role)
        refresh_token = create_refresh_token(subject=str(new_user.id))

        session_obj = Session(
            user_id=new_user.id,
            refresh_token_hash=hash_token(refresh_token),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),  # noqa: UP017
        )
        db.add(session_obj)
        await db.commit()
        await db.refresh(new_user)
        return new_user, access_token, refresh_token

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, req: UserLoginRequest, user_agent: str | None = None, ip_address: str | None = None
    ) -> tuple[User, str, str]:
        email_clean = req.email.lower().strip()
        user = (await db.execute(select(User).where(User.email == email_clean))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        now = datetime.now(timezone.utc)  # noqa: UP017
        if user.lockout_until:
            lockout_time = user.lockout_until if user.lockout_until.tzinfo else user.lockout_until.replace(tzinfo=timezone.utc)  # noqa: UP017
            if lockout_time > now:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Account is temporarily locked due to multiple failed login attempts. Please try again later.",
                )
            user.failed_login_count = 0
            user.lockout_until = None

        if not verify_password(req.password, user.password_hash):
            user.failed_login_count = (user.failed_login_count or 0) + 1
            if user.failed_login_count >= 5:
                user.lockout_until = now + timedelta(minutes=15)
            await db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is currently inactive or suspended")

        user.failed_login_count = 0
        user.lockout_until = None

        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = create_refresh_token(subject=str(user.id))

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
