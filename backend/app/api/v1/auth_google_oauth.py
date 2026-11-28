from datetime import datetime, timedelta, timezone
import secrets
import sys
from urllib.parse import quote
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth_google_signup import create_google_session, exchange_google_code
from app.api.v1.auth_helpers import format_user_profile, get_user_wallet_info, set_refresh_cookie
from app.api.v1.auth_oauth_codes import (
    bind_oauth_state_cookie, clear_oauth_state_cookie, consume_oauth_exchange_code,
    store_oauth_exchange_code, verify_oauth_state_cookie,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limiter import extract_client_ip
from app.core.security import create_access_token, create_oauth_state, create_signup_ticket, hash_token, verify_oauth_state
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.schemas.auth import GoogleExchangeRequest, GoogleVerifyRequest, TokenResponse
from app.schemas.common import APIResponse

google_router = APIRouter()


def _get_httpx():
    return getattr(sys.modules.get("app.api.v1.auth"), "httpx", httpx)


def _require_google_id() -> None:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_ID.strip():
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Google OAuth belum dikonfigurasi di server.")


def _redirect(url: str) -> Response:
    resp = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": url})
    clear_oauth_state_cookie(resp)
    return resp


def _redirect_err(msg: str) -> Response:
    return _redirect(f"{settings.FRONTEND_URL}/login?oauth_error={quote(msg)}")


async def _oauth_token_response(
    db: AsyncSession, user: User, access_token: str, refresh_token: str, response: Response | None,
) -> APIResponse[TokenResponse]:
    if response is not None:
        set_refresh_cookie(response, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS)
    bal, trial, chat = await get_user_wallet_info(db, user.id)
    profile = format_user_profile(user, bal or 0, trial or 0, chat or 0)
    return APIResponse(message="Berhasil masuk dengan akun Google", data=TokenResponse(access_token=access_token, user=profile))


@google_router.get("/google/login")
async def google_login(intent: str = "login"):
    _require_google_id()
    state = create_oauth_state(intent if intent in ("login", "reset") else "login")
    params = f"client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={quote(settings.GOOGLE_REDIRECT_URI, safe='')}&response_type=code&scope={quote('openid email profile', safe='')}&access_type=offline&prompt=select_account&state={state}"
    resp = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": f"https://accounts.google.com/o/oauth2/v2/auth?{params}"})
    bind_oauth_state_cookie(resp, state)
    return resp


@google_router.get("/google/callback")
async def google_callback(
    code: str | None = None, state: str | None = None, error: str | None = None,
    request: Request = None, db: AsyncSession = Depends(get_db),
):
    if error or not code:
        return _redirect_err(error or "Otorisasi Google dibatalkan oleh pengguna.")
    state_data = verify_oauth_state(state or "")
    if not verify_oauth_state_cookie(request, state) or not state_data:
        return _redirect_err("Sesi autentikasi Google kedaluwarsa. Silakan coba lagi.")
    try:
        async with _get_httpx().AsyncClient(timeout=10.0) as client:
            u_info = await exchange_google_code(client, code)
            if not u_info.get("verified_email"):
                return _redirect_err("Email Google belum diverifikasi")
            email = u_info.get("email", "").lower().strip()
            full_name = u_info.get("name") or (email.split("@")[0] if "@" in email else "Pengguna Google")
    except ValueError as e:
        return _redirect_err(str(e))
    except Exception:
        return _redirect_err("Koneksi ke Google gagal")
    if not email:
        return _redirect_err("Email tidak ditemukan")

    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if state_data.get("intent") == "reset":
        if not user or not user.is_active:
            return _redirect_err("Akun dengan email Google ini tidak ditemukan atau nonaktif.")
        now = datetime.now(timezone.utc)
        await db.execute(update(PasswordReset).where(PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None)).values(used_at=now))
        raw_token = secrets.token_urlsafe(32)
        db.add(PasswordReset(user_id=user.id, token_hash=hash_token(raw_token), expires_at=now + timedelta(hours=1)))
        await db.commit()
        return _redirect(f"{settings.FRONTEND_URL}/reset-password?token={raw_token}")
    if user:
        if not user.is_active:
            return _redirect_err("Akun Anda telah dinonaktifkan")
        _, rt = await create_google_session(db, user, "Google-SSO-Client", extract_client_ip(request) if request else None)
        one_time_code = await store_oauth_exchange_code(str(user.id), rt)
        return _redirect(f"{settings.FRONTEND_URL}/auth/callback?code={quote(one_time_code)}")
    return _redirect(f"{settings.FRONTEND_URL}/onboarding?ticket={quote(create_signup_ticket(email=email, name=full_name))}")


@google_router.post("/google/exchange", response_model=APIResponse[TokenResponse])
async def google_exchange_code(req: GoogleExchangeRequest, response: Response = None, db: AsyncSession = Depends(get_db)):
    payload = await consume_oauth_exchange_code(req.code)
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kode otorisasi Google tidak valid atau kedaluwarsa")
    user = await db.get(User, uuid.UUID(payload["user_id"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akun pengguna tidak ditemukan atau dinonaktifkan")
    return await _oauth_token_response(db, user, create_access_token(subject=str(user.id), role=user.role), payload["refresh_token"], response)


@google_router.post("/google/verify", response_model=APIResponse[TokenResponse])
async def google_verify_token(req: GoogleVerifyRequest, request: Request = None, response: Response = None, db: AsyncSession = Depends(get_db)):
    _require_google_id()
    try:
        async with _get_httpx().AsyncClient(timeout=10.0) as client:
            res = await client.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": req.credential})
        if res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID Token Google tidak valid")
        data = res.json()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gagal memvalidasi token Google")
    if data.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Audience token Google tidak cocok")
    if data.get("email_verified") not in ("true", True):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email Google belum diverifikasi")
    email = data.get("email", "").lower().strip()
    full_name = data.get("name") or (email.split("@")[0] if "@" in email else "Pengguna Google")
    if not email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email tidak tersedia pada token Google")
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_409_CONFLICT, {"code": "SIGNUP_REQUIRED", "signup_ticket": create_signup_ticket(email=email, name=full_name)})
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Akun Anda dinonaktifkan")
    at, rt = await create_google_session(db, user, "Google-Identity-Services", extract_client_ip(request) if request else None)
    return await _oauth_token_response(db, user, at, rt, response)
