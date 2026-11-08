from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth_helpers import (
    format_user_profile,
    set_refresh_cookie,
    validate_strong_password,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_signup_ticket,
    get_password_hash,
    hash_token,
)
from app.models.session import Session
from app.models.user import User
from app.models.wallet import TokenWallet
from app.schemas.auth import GoogleCompleteRequest, TokenResponse
from app.schemas.common import APIResponse

google_signup_router = APIRouter()


async def exchange_google_code(client, code: str) -> dict:
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    t_res = await client.post("https://oauth2.googleapis.com/token", data=data)
    if t_res.status_code != 200:
        raise ValueError("Pertukaran token Google gagal")
    u_res = await client.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {t_res.json().get('access_token')}"},
    )
    if u_res.status_code != 200:
        raise ValueError("Gagal mengambil profil Google")
    return u_res.json()


async def create_google_session(
    db: AsyncSession,
    user: User,
    client_tag: str,
    ip_addr: Optional[str] = None,
) -> tuple[str, str]:
    access_token = create_access_token(subject=str(user.id), role=user.role)
    refresh_token = create_refresh_token(subject=str(user.id))
    sess = Session(
        user_id=user.id,
        refresh_token_hash=hash_token(refresh_token),
        user_agent=client_tag,
        ip_address=ip_addr,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(sess)
    await db.commit()
    return access_token, refresh_token


@google_signup_router.post("/google/complete", response_model=APIResponse[TokenResponse])
async def google_complete(
    req: GoogleCompleteRequest,
    request: Request = None,
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    ticket_payload = decode_signup_ticket(req.ticket)
    if not ticket_payload or ticket_payload.get("purpose") != "google_signup":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tiket pendaftaran tidak valid atau telah kedaluwarsa",
        )

    ticket_email = ticket_payload.get("email", "").lower().strip()
    if not ticket_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tiket pendaftaran tidak berisi email yang valid",
        )

    existing_user = (
        await db.execute(select(User).where(User.email == ticket_email))
    ).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered in the system",
        )

    clean_name = req.full_name.strip()
    if len(clean_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama lengkap minimal 2 karakter.",
        )

    validate_strong_password(req.password)

    new_user = User(
        full_name=clean_name,
        email=ticket_email,
        password_hash=get_password_hash(req.password),
        role="FREE",
        is_active=True,
    )
    db.add(new_user)
    await db.flush()

    wallet = TokenWallet(user_id=new_user.id, balance=5, ai_trial_remaining=3)
    db.add(wallet)
    await db.flush()

    ip_addr = request.client.host if request and request.client else None
    access_token, refresh_token = await create_google_session(
        db, new_user, "Google-SSO-Complete", ip_addr
    )
    await db.refresh(new_user)

    if response is not None:
        set_refresh_cookie(response, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return APIResponse(
        message="Pendaftaran akun Google berhasil diselesaikan",
        data=TokenResponse(
            access_token=access_token,
            user=format_user_profile(new_user, 5),
        ),
    )
