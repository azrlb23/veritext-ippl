from datetime import datetime, timedelta, timezone
import logging
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
import app.api.v1.auth_google_oauth as _google_mod
import app.api.v1.auth_google_signup as _google_signup_mod
import app.api.v1.auth_helpers as _helpers_mod
import app.api.v1.auth_password_reset as _reset_mod
from app.core.config import settings
from app.core.database import get_db
from app.core.email import send_password_reset_email
from app.core.rate_limiter import extract_client_ip
from app.core.security import create_access_token, create_refresh_token, hash_token
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLoginRequest, UserProfileResponse, UserRegisterRequest
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.services.upload_limits import enforce_rate_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

validate_strong_password = _helpers_mod.validate_strong_password
update_profile = _helpers_mod.update_profile
change_password = _helpers_mod.change_password
google_complete = _google_signup_mod.google_complete
delete_own_account = _helpers_mod.delete_own_account
delete_my_account = _helpers_mod.delete_my_account
format_user_profile = _helpers_mod.format_user_profile
get_user_wallet_balance = _helpers_mod.get_user_wallet_balance
set_refresh_cookie = _helpers_mod.set_refresh_cookie
forgot_password = _reset_mod.forgot_password
reset_password = _reset_mod.reset_password
logout_all = _reset_mod.logout_all
google_login = _google_mod.google_login
google_callback = _google_mod.google_callback
google_verify_token = _google_mod.google_verify_token


@router.post("/register", response_model=APIResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    ip_addr = extract_client_ip(request)
    user, access_token, refresh_token = await AuthService.register_user(db, req, user_agent=request.headers.get("user-agent"), ip_address=ip_addr)
    set_refresh_cookie(response, refresh_token, 7)
    return APIResponse(message="User account registered successfully. 5 trial tokens granted.", data=TokenResponse(access_token=access_token, user=format_user_profile(user, 5, 3, 0)))


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(req: UserLoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    ip_addr = extract_client_ip(request)
    await enforce_rate_limit(
        f"{req.email.lower().strip()}:{ip_addr or 'unknown'}",
        "auth_login",
        limit=10,
        detail="Terlalu banyak percobaan masuk. Silakan coba lagi dalam 1 menit.",
    )
    user, access_token, refresh_token = await AuthService.authenticate_user(db, req, user_agent=request.headers.get("user-agent"), ip_address=ip_addr)
    set_refresh_cookie(response, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS if req.remember_me else None)
    bal, trial, chat = await _helpers_mod.get_user_wallet_info(db, user.id)
    return APIResponse(message="Login successful", data=TokenResponse(access_token=access_token, user=format_user_profile(user, bal, trial, chat)))


@router.post("/logout", response_model=APIResponse[dict])
async def logout(response: Response, refresh_token: str = Cookie(None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if refresh_token:
        hashed = hash_token(refresh_token)
        res = await db.execute(select(Session).where(Session.refresh_token_hash == hashed))
        session_obj = res.scalar_one_or_none()
        if session_obj:
            await db.delete(session_obj)
            await db.commit()
    _helpers_mod.clear_refresh_cookie(response)
    return APIResponse(message="Logged out successfully", data={})


@router.post("/refresh", response_model=APIResponse[dict])
async def refresh_token_endpoint(
    request: Request = None, response: Response = None, refresh_token: Optional[str] = Cookie(None), db: AsyncSession = Depends(get_db),
):
    token = refresh_token
    if not token and request is not None and not hasattr(request, "dependency"):
        try:
            token = request.headers.get("x-refresh-token") or request.cookies.get("refresh_token")
            if not token:
                body_data = await request.json()
                if isinstance(body_data, dict):
                    token = body_data.get("refresh_token")
        except Exception:
            pass
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token cookie missing")

    hashed = hash_token(token)
    res = await db.execute(select(Session).where(Session.refresh_token_hash == hashed).with_for_update())
    sess = res.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or revoked refresh token")

    now = datetime.now(timezone.utc)
    if sess.expires_at is not None:
        sess_exp = sess.expires_at if sess.expires_at.tzinfo else sess.expires_at.replace(tzinfo=timezone.utc)
        if sess_exp < now:
            await db.delete(sess)
            await db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired")

    user = await db.get(User, sess.user_id)
    if not user:
        res_u = await db.execute(select(User).where(User.id == sess.user_id))
        user = res_u.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    new_access_token = create_access_token(subject=str(user.id), role=user.role)
    new_refresh_token = create_refresh_token(subject=str(user.id))
    sess.refresh_token_hash = hash_token(new_refresh_token)
    sess.expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await db.commit()

    if response is not None:
        set_refresh_cookie(response, new_refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return APIResponse(message="Token refreshed successfully", data={"access_token": new_access_token})


@router.get("/me", response_model=APIResponse[UserProfileResponse])
async def get_current_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    bal, trial, chat = await _helpers_mod.get_user_wallet_info(db, current_user.id)
    return APIResponse(message="Profile retrieved", data=format_user_profile(current_user, bal, trial, chat))


get_me = get_current_profile

router.include_router(_helpers_mod.helpers_router)
router.include_router(_reset_mod.reset_router)
router.include_router(_google_mod.google_router)
router.include_router(_google_signup_mod.google_signup_router)

__all__ = [
    "router", "register", "login", "logout", "refresh_token_endpoint", "get_current_profile", "get_me",
    "validate_strong_password", "send_password_reset_email", "forgot_password", "reset_password", "logout_all",
    "google_login", "google_callback", "google_verify_token", "google_complete", "update_profile", "change_password",
    "delete_own_account", "delete_my_account", "httpx",
]
