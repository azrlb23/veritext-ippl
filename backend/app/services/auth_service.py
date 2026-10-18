from datetime import datetime, timezone
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
        stmt = select(User).where(User.email == req.email.lower().strip())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is currently inactive or suspended",
            )

        access_token = create_access_token(subject=str(user.id), role=user.role)
        from app.core.security import create_refresh_token
        refresh_token = create_refresh_token(subject=str(user.id))

        # Store session
        from datetime import timedelta
        from app.core.config import settings
        session_obj = Session(
            user_id=user.id,
            refresh_token_hash=hash_token(refresh_token),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(session_obj)
        await db.commit()

        return user, access_token, refresh_token
