import secrets
import sys
from typing import Optional
from urllib.parse import quote

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth_google_signup import create_google_session, exchange_google_code
from app.api.v1.auth_helpers import format_user_profile, get_user_wallet_balance, set_refresh_cookie
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_signup_ticket
from app.models.user import User
from app.schemas.auth import GoogleVerifyRequest, TokenResponse
from app.schemas.common import APIResponse

google_router = APIRouter()


def _get_httpx():
    mod = sys.modules.get("app.api.v1.auth")
    return getattr(mod, "httpx", httpx) if mod else httpx


def _redirect_err(msg: str) -> Response:
    resp = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": f"{settings.FRONTEND_URL}/login?oauth_error={quote(msg)}"})
    resp.delete_cookie(key="g_oauth_state")
    return resp


@google_router.get("/google/login")
async def google_login():
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_ID.strip():
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Google OAuth belum dikonfigurasi di server.")
    state = secrets.token_urlsafe(16)
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={quote(settings.GOOGLE_REDIRECT_URI, safe='')}&response_type=code&"
        f"scope={quote('openid email profile', safe='')}&access_type=offline&prompt=select_account&state={state}"
    )
    is_prod = getattr(settings, "ENVIRONMENT", "").lower() == "production"
    resp = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": url})
    resp.set_cookie(key="g_oauth_state", value=state, httponly=True, samesite="lax", secure=is_prod, max_age=600)
    return resp


@google_router.get("/google/callback")
async def google_callback(
    code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None,
    request: Request = None, db: AsyncSession = Depends(get_db),
):
    cookie_state = request.cookies.get("g_oauth_state") if request and hasattr(request, "cookies") else None
    if error or not code:
        return _redirect_err(error or "Otorisasi Google dibatalkan oleh pengguna.")
    if not state or not cookie_state or state != cookie_state:
        return _redirect_err("Validasi state CSRF gagal")

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
    if user:
        if not user.is_active:
            return _redirect_err("Akun Anda telah dinonaktifkan")
        ip_addr = request.client.host if request and request.client else None
        access_token, refresh_token = await create_google_session(db, user, "Google-SSO-Client", ip_addr)
        target = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}&user_name={quote(user.full_name)}&email={quote(user.email)}"
        resp = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": target})
        resp.delete_cookie(key="g_oauth_state")
        set_refresh_cookie(resp, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return resp

    ticket = create_signup_ticket(email=email, name=full_name)
    resp = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": f"{settings.FRONTEND_URL}/onboarding?ticket={quote(ticket)}"})
    resp.delete_cookie(key="g_oauth_state")
    return resp


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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audience token Google tidak cocok")
    if data.get("email_verified") not in ("true", True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email Google belum diverifikasi")

    email = data.get("email", "").lower().strip()
    full_name = data.get("name") or (email.split("@")[0] if "@" in email else "Pengguna Google")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email tidak tersedia pada token Google")

    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        ticket = create_signup_ticket(email=email, name=full_name)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "SIGNUP_REQUIRED", "signup_ticket": ticket})

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akun Anda dinonaktifkan")

    ip_addr = request.client.host if request and request.client else None
    access_token, refresh_token = await create_google_session(db, user, "Google-Identity-Services", ip_addr)
    if response is not None:
        set_refresh_cookie(response, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS)
    balance = await get_user_wallet_balance(db, user.id)
    return APIResponse(message="Berhasil masuk dengan akun Google", data=TokenResponse(access_token=access_token, user=format_user_profile(user, balance)))
