import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.models.session import Session
from app.models.user import User
from app.models.wallet import TokenWallet
from app.schemas.auth import (
    ChangePasswordRequest,
    UserProfileResponse,
    UserProfileUpdate,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

helpers_router = APIRouter()


def validate_strong_password(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Kata sandi minimal harus 8 karakter.")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Kata sandi harus mengandung minimal 1 huruf kapital (A-Z).")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Kata sandi harus mengandung minimal 1 huruf kecil (a-z).")
    if not re.search(r"\d", password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Kata sandi harus mengandung minimal 1 angka (0-9).")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_+=\[\]\\/`~]", password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Kata sandi harus mengandung minimal 1 karakter khusus / simbol.")


def format_user_profile(user: User, balance: int = 0) -> UserProfileResponse:
    return UserProfileResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at or datetime.now(timezone.utc),  # noqa: UP017
        token_balance=balance,
    )


def set_refresh_cookie(response: Response, refresh_token: str, days: int = 7) -> None:
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, samesite="lax", secure=False, max_age=days * 24 * 3600
    )


async def get_user_wallet_balance(db: AsyncSession, user_id) -> int:
    stmt = select(TokenWallet).where(TokenWallet.user_id == user_id)
    res = await db.execute(stmt)
    wallet = res.scalar_one_or_none()
    return wallet.balance if wallet else 0


@helpers_router.patch("/profile", response_model=APIResponse[UserProfileResponse])
async def update_profile(
    req: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.full_name is not None:
        current_user.full_name = req.full_name
    await db.commit()
    await db.refresh(current_user)
    balance = await get_user_wallet_balance(db, current_user.id)
    return APIResponse(message="Profile updated", data=format_user_profile(current_user, balance))


@helpers_router.patch("/change-password", response_model=APIResponse[dict])
@helpers_router.post("/change-password", response_model=APIResponse[dict])
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    current_user.password_hash = get_password_hash(req.new_password)
    await db.execute(delete(Session).where(Session.user_id == current_user.id))
    await db.commit()
    return APIResponse(message="Password changed successfully", data={})


@helpers_router.delete("/me", response_model=APIResponse[dict])
async def delete_own_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await AuthService.delete_user_account(db, current_user)
    response.delete_cookie(key="refresh_token")
    msg = "Akun dan seluruh data pribadi naskah Anda telah dihapus secara permanen"
    return APIResponse(message=msg, data={})


delete_my_account = delete_own_account


