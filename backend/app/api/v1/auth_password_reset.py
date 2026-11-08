import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_password_hash, hash_token
from app.models.password_reset import PasswordReset
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.common import APIResponse

reset_router = APIRouter()


@reset_router.post("/forgot-password", response_model=APIResponse[dict])
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    email_clean = req.email.lower().strip()
    stmt = select(User).where(User.email == email_clean)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if user:
        raw_token = secrets.token_urlsafe(32)
        token_hashed = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        reset_obj = PasswordReset(
            user_id=user.id,
            token_hash=token_hashed,
            expires_at=expires_at,
        )
        db.add(reset_obj)
        await db.commit()

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
        import app.api.v1.auth as auth_mod
        send_email_fn = getattr(auth_mod, "send_password_reset_email", None)
        if send_email_fn is not None:
            send_email_fn(to_email=user.email, reset_url=reset_url, user_name=user.full_name)

    return APIResponse(
        message="Jika email terdaftar, tautan pemulihan kata sandi telah dikirimkan (berlaku 1 jam).",
        data={},
    )


@reset_router.post("/reset-password", response_model=APIResponse[dict])
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    token_hashed = hash_token(req.token)
    stmt = select(PasswordReset).where(
        (PasswordReset.token_hash == token_hashed) | (PasswordReset.token_hash == req.token)
    )
    res = await db.execute(stmt)
    reset_entry = res.scalar_one_or_none()

    if not reset_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )

    if reset_entry.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has already been used",
        )

    now = datetime.now(timezone.utc)
    exp = reset_entry.expires_at if reset_entry.expires_at.tzinfo else reset_entry.expires_at.replace(tzinfo=timezone.utc)
    if exp < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired",
        )

    user = await db.get(User, reset_entry.user_id)
    if not user:
        stmt_u = select(User).where(User.id == reset_entry.user_id)
        res_u = await db.execute(stmt_u)
        user = res_u.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated user account not found",
        )

    user.password_hash = get_password_hash(req.new_password)
    user.failed_login_count = 0
    user.lockout_until = None
    reset_entry.is_used = True

    await db.execute(delete(Session).where(Session.user_id == user.id))
    await db.commit()

    return APIResponse(message="Password reset successfully. You can now login.", data={})
