from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, hash_token, create_refresh_token
from app.models.user import User
from app.models.session import Session
from app.models.password_reset import PasswordReset
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserProfileResponse,
    TokenResponse,
    UserProfileUpdate,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
async def register(
    req: UserRegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    user, access_token, refresh_token = await AuthService.register_user(
        db, req, user_agent=user_agent, ip_address=ip_addr
    )

    # Set HttpOnly refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=7 * 24 * 3600,
    )

    return APIResponse(
        message="User account registered successfully. 5 trial tokens granted.",
        data=TokenResponse(
            access_token=access_token,
            user=UserProfileResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                institution=user.institution,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                token_balance=5,
            ),
        ),
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    req: UserLoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    user, access_token, refresh_token = await AuthService.authenticate_user(
        db, req, user_agent=user_agent, ip_address=ip_addr
    )

    # Set HttpOnly refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,  # True in production HTTPS
        max_age=7 * 24 * 3600,
    )

    # Fetch token wallet balance
    from app.models.wallet import TokenWallet
    wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == user.id)
    wallet_res = await db.execute(wallet_stmt)
    wallet = wallet_res.scalar_one_or_none()
    balance = wallet.balance if wallet else 0

    return APIResponse(
        message="Login successful",
        data=TokenResponse(
            access_token=access_token,
            user=UserProfileResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                institution=user.institution,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                token_balance=balance,
            ),
        ),
    )


@router.post("/logout", response_model=APIResponse[dict])
async def logout(
    response: Response,
    refresh_token: str = Cookie(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if refresh_token:
        # Revoke session
        hashed = hash_token(refresh_token)
        stmt = select(Session).where(Session.refresh_token_hash == hashed)
        res = await db.execute(stmt)
        session_obj = res.scalar_one_or_none()
        if session_obj:
            await db.delete(session_obj)
            await db.commit()

    response.delete_cookie(key="refresh_token")
    return APIResponse(message="Logged out successfully", data={})


@router.post("/refresh", response_model=APIResponse[dict])
async def refresh_token_endpoint(
    response: Response = None,
    refresh_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cookie missing",
        )

    hashed = hash_token(refresh_token)
    stmt = select(Session).where(Session.refresh_token_hash == hashed)
    res = await db.execute(stmt)
    sess = res.scalar_one_or_none()

    if not sess:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token",
        )

    # Validate expiration
    now = datetime.now(timezone.utc)
    if sess.expires_at is not None:
        sess_exp = sess.expires_at if sess.expires_at.tzinfo else sess.expires_at.replace(tzinfo=timezone.utc)
        if sess_exp < now:
            await db.delete(sess)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

    # Fetch user
    user = await db.get(User, sess.user_id)
    if not user:
        stmt_u = select(User).where(User.id == sess.user_id)
        res_u = await db.execute(stmt_u)
        user = res_u.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    new_access_token = create_access_token(subject=str(user.id), role=user.role)
    new_refresh_token = create_refresh_token(subject=str(user.id))

    # Refresh token rotation: update session hash and expiration
    sess.refresh_token_hash = hash_token(new_refresh_token)
    sess.expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await db.commit()

    if response is not None:
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        )

    return APIResponse(
        message="Token refreshed successfully",
        data={
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        },
    )


@router.post("/forgot-password", response_model=APIResponse[dict])
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    email_clean = req.email.lower().strip()
    stmt = select(User).where(User.email == email_clean)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    raw_token = None
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

    return APIResponse(
        message="If this email is registered, a password reset link has been dispatched.",
        data={"reset_token": raw_token} if raw_token else {},
    )


@router.post("/reset-password", response_model=APIResponse[dict])
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

    # Revoke all active sessions for this user
    await db.execute(delete(Session).where(Session.user_id == user.id))
    await db.commit()

    return APIResponse(message="Password reset successfully. You can now login.", data={})


@router.get("/me", response_model=APIResponse[UserProfileResponse])
async def get_current_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.wallet import TokenWallet
    wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == current_user.id)
    wallet_res = await db.execute(wallet_stmt)
    wallet = wallet_res.scalar_one_or_none()
    balance = wallet.balance if wallet else 0

    return APIResponse(
        message="Profile retrieved",
        data=UserProfileResponse(
            id=current_user.id,
            full_name=current_user.full_name,
            email=current_user.email,
            institution=current_user.institution,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            token_balance=balance,
        ),
    )


@router.patch("/profile", response_model=APIResponse[UserProfileResponse])
async def update_profile(
    req: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.full_name is not None:
        current_user.full_name = req.full_name
    if req.institution is not None:
        current_user.institution = req.institution

    await db.commit()
    await db.refresh(current_user)

    from app.models.wallet import TokenWallet
    wallet_stmt = select(TokenWallet).where(TokenWallet.user_id == current_user.id)
    wallet_res = await db.execute(wallet_stmt)
    wallet = wallet_res.scalar_one_or_none()
    balance = wallet.balance if wallet else 0

    return APIResponse(
        message="Profile updated",
        data=UserProfileResponse(
            id=current_user.id,
            full_name=current_user.full_name,
            email=current_user.email,
            institution=current_user.institution,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            token_balance=balance,
        ),
    )


@router.patch("/change-password", response_model=APIResponse[dict])
@router.post("/change-password", response_model=APIResponse[dict])
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    current_user.password_hash = get_password_hash(req.new_password)
    # Revoke all active sessions for this user to enforce fresh authentication
    await db.execute(delete(Session).where(Session.user_id == current_user.id))
    await db.commit()
    return APIResponse(message="Password changed successfully", data={})


@router.delete("/me", response_model=APIResponse[dict])
async def delete_own_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await AuthService.delete_user_account(db, current_user)
    response.delete_cookie(key="refresh_token")
    return APIResponse(
        message="Akun dan seluruh data pribadi naskah Anda telah dihapus secara permanen sesuai UU PDP No. 27/2022 Pasal 8",
        data={},
    )

