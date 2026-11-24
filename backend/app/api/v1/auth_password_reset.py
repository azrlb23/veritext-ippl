import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.v1.auth_helpers import validate_strong_password
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_password_hash, hash_token
from app.models.password_reset import PasswordReset
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.common import APIResponse
from app.services.auth_security import (
    check_otp_attempts,
    clear_otp_attempts,
    handle_otp_failure,
)
from app.services.upload_limits import enforce_rate_limit

reset_router = APIRouter()


@reset_router.post("/forgot-password", response_model=APIResponse[dict])
async def forgot_password(
    req: ForgotPasswordRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    email_clean = req.email.lower().strip()
    if request is not None:
        ip_addr = request.client.host if request.client else "unknown"
        await enforce_rate_limit(
            f"{email_clean}:{ip_addr}",
            "auth_forgot",
            limit=5,
            detail="Terlalu banyak permintaan reset kata sandi. Silakan coba lagi nanti.",
        )
    res = await db.execute(select(User).where(User.email == email_clean))
    user = res.scalar_one_or_none()

    if user:
        await db.execute(
            update(PasswordReset)
            .where(PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None))
            .values(used_at=datetime.now(timezone.utc))
        )
        otp_code = f"{secrets.randbelow(1_000_000):06d}"
        token_hashed = hash_token(f"{email_clean}:{otp_code}")
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db.add(PasswordReset(user_id=user.id, token_hash=token_hashed, expires_at=expires_at))
        await db.commit()
        await clear_otp_attempts(email_clean)

        reset_url = f"{settings.FRONTEND_URL}/reset-password?otp={otp_code}&email={quote(email_clean)}"
        import app.api.v1.auth as auth_mod

        send_email_fn = getattr(auth_mod, "send_password_reset_email", None)
        if send_email_fn is not None:
            try:
                send_email_fn(to_email=user.email, reset_url=reset_url, user_name=user.full_name, otp_code=otp_code)
            except TypeError:
                send_email_fn(to_email=user.email, reset_url=reset_url, user_name=user.full_name)

    return APIResponse(
        message="Jika email terdaftar, tautan pemulihan kata sandi telah dikirimkan (berlaku 1 jam).",
        data={},
    )


@reset_router.post("/reset-password", response_model=APIResponse[dict])
async def reset_password(
    req: ResetPasswordRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    if request is not None:
        ip_addr = request.client.host if request.client else "unknown"
        await enforce_rate_limit(
            ip_addr, "auth_reset", limit=10,
            detail="Terlalu banyak percobaan reset kata sandi. Silakan coba lagi nanti.",
        )
    validate_strong_password(req.new_password)

    email_clean = req.email.lower().strip() if req.email else ""
    if req.otp and email_clean:
        await check_otp_attempts(email_clean)
        cond = PasswordReset.token_hash == hash_token(f"{email_clean}:{req.otp.strip()}")
    elif req.token:
        cond = PasswordReset.token_hash == hash_token(req.token)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token atau kode OTP wajib diisi")

    reset_entry = (await db.execute(select(PasswordReset).where(cond))).scalar_one_or_none()
    if not reset_entry:
        if req.otp and email_clean:
            await handle_otp_failure(db, email_clean)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token")
    if reset_entry.is_used:
        if req.otp and email_clean:
            await handle_otp_failure(db, email_clean)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset token has already been used")

    now = datetime.now(timezone.utc)
    exp = reset_entry.expires_at if reset_entry.expires_at.tzinfo else reset_entry.expires_at.replace(tzinfo=timezone.utc)
    if exp < now:
        if req.otp and email_clean:
            await handle_otp_failure(db, email_clean)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset token has expired")

    user = await db.get(User, reset_entry.user_id)
    if not user:
        user = (await db.execute(select(User).where(User.id == reset_entry.user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated user account not found")

    user.password_hash = get_password_hash(req.new_password)
    user.failed_login_count = 0
    user.lockout_until = None
    reset_entry.is_used = True

    await db.execute(delete(Session).where(Session.user_id == user.id))
    await db.commit()
    if email_clean:
        await clear_otp_attempts(email_clean)

    return APIResponse(message="Password reset successfully. You can now login.", data={})


@reset_router.post("/logout-all", response_model=APIResponse[dict])
async def logout_all(
    response: Response = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(delete(Session).where(Session.user_id == current_user.id))
    await db.commit()
    if response is not None:
        response.delete_cookie(key="refresh_token")
    return APIResponse(message="Semua sesi perangkat telah diakhiri.", data={})
