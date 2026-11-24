from datetime import datetime, timedelta, timezone
import secrets
import sys
from typing import Optional
from urllib.parse import quote
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth_google_signup import create_google_session, exchange_google_code
from app.api.v1.auth_helpers import format_user_profile, get_user_wallet_balance, set_refresh_cookie
from app.api.v1.auth_oauth_codes import consume_oauth_exchange_code, store_oauth_exchange_code
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_oauth_state, create_signup_ticket, hash_token, verify_oauth_state
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.schemas.auth import GoogleExchangeRequest, GoogleVerifyRequest, TokenResponse
from app.schemas.common import APIResponse

google_router = APIRouter()


def _get_httpx():
    mod = sys.modules.get("app.api.v1.auth")
    return getattr(mod, "httpx", httpx) if mod else httpx


def _redirect_err(msg: str) -> Response:
    return Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": f"{settings.FRONTEND_URL}/login?oauth_error={quote(msg)}"})


@google_router.get("/google/login")
async def google_login(intent: str = "login"):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_ID.strip():
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Google OAuth belum dikonfigurasi di server.")
    safe_intent = intent if intent in ("login", "reset") else "login"
    state = create_oauth_state(safe_intent)
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={quote(settings.GOOGLE_REDIRECT_URI, safe='')}&response_type=code&"
        f"scope={quote('openid email profile', safe='')}&access_type=offline&prompt=select_account&state={state}"
    )
    return Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": url})


@google_router.get("/google/callback")
async def google_callback(
    code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None,
    request: Request = None, db: AsyncSession = Depends(get_db),
):
    if error or not code:
        return _redirect_err(error or "Otorisasi Google dibatalkan oleh pengguna.")
    state_data = verify_oauth_state(state or "")
    if not state_data:
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
        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db.add(PasswordReset(user_id=user.id, token_hash=hash_token(raw_token), expires_at=expires_at))
        await db.commit()
        return Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"})

    if user:
        if not user.is_active:
            return _redirect_err("Akun Anda telah dinonaktifkan")
        ip_addr = request.client.host if request and request.client else None
        _, refresh_token = await create_google_session(db, user, "Google-SSO-Client", ip_addr)
        one_time_code = await store_oauth_exchange_code(str(user.id), refresh_token)
        target = f"{settings.FRONTEND_URL}/auth/callback?code={quote(one_time_code)}"
        return Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": target})

    ticket = create_signup_ticket(email=email, name=full_name)
    return Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": f"{settings.FRONTEND_URL}/onboarding?ticket={quote(ticket)}"})


@google_router.post("/google/exchange", response_model=APIResponse[TokenResponse])
async def google_exchange_code(
    req: GoogleExchangeRequest, response: Response = None, db: AsyncSession = Depends(get_db),
):
    payload = await consume_oauth_exchange_code(req.code)
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kode otorisasi Google tidak valid atau kedaluwarsa")
    user = await db.get(User, uuid.UUID(payload["user_id"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akun pengguna tidak ditemukan atau dinonaktifkan")
    access_token = create_access_token(subject=str(user.id), role=user.role)
    if response is not None:
        set_refresh_cookie(response, payload["refresh_token"], settings.REFRESH_TOKEN_EXPIRE_DAYS)
    balance = await get_user_wallet_balance(db, user.id)
    return APIResponse(message="Berhasil masuk dengan akun Google", data=TokenResponse(access_token=access_token, user=format_user_profile(user, balance)))


@google_router.post("/google/verify", response_model=APIResponse[TokenResponse])
async def google_verify_token(
    req: GoogleVerifyRequest, request: Request = None, response: Response = None, db: AsyncSession = Depends(get_db),
):
    try:
        async with _get_httpx().AsyncClient(timeout=10.0) as client:
            res = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={req.credential}")
        if res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID Token Google tidak valid")
        data = res.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Gagal memvalidasi token Google: {exc}")

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

    ip_addr = request.client.host if request and request.client else None
    access_token, refresh_token = await create_google_session(db, user, "Google-Identity-Services", ip_addr)
    if response is not None:
        set_refresh_cookie(response, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS)
    balance = await get_user_wallet_balance(db, user.id)
    return APIResponse(message="Berhasil masuk dengan akun Google", data=TokenResponse(access_token=access_token, user=format_user_profile(user, balance)))
