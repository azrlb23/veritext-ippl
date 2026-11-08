from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse
from unittest.mock import MagicMock, patch
import uuid

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.api.v1 import auth as auth_router
from app.core.config import settings
from app.core.security import (
    create_signup_ticket,
    decode_signup_ticket,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.models.password_reset import PasswordReset
from app.models.session import Session
from app.models.user import User
from app.models.wallet import TokenWallet
from app.schemas.auth import (
    ForgotPasswordRequest,
    GoogleCompleteRequest,
    GoogleVerifyRequest,
    ResetPasswordRequest,
    UserLoginRequest,
)


class MockQueryResult:
    def __init__(self, items=None, scalar_val=None):
        self._items = items if items is not None else []
        self._scalar_val = scalar_val

    def scalar_one_or_none(self):
        if self._scalar_val is not None:
            return self._scalar_val
        return self._items[0] if self._items else None


class MockAsyncSession:
    def __init__(self, execute_handler=None, get_handler=None):
        self.execute_handler = execute_handler
        self.get_handler = get_handler
        self.added = []
        self.deleted = []
        self.committed = False

    async def execute(self, statement):
        if self.execute_handler:
            return self.execute_handler(statement)
        return MockQueryResult([])

    def add(self, item):
        self.added.append(item)

    async def flush(self):
        for item in self.added:
            if hasattr(item, "id") and getattr(item, "id") is None:
                item.id = uuid.uuid4()

    async def commit(self):
        self.committed = True

    async def refresh(self, item):
        pass

    async def delete(self, item):
        self.deleted.append(item)

    async def get(self, entity, ident):
        if self.get_handler:
            return self.get_handler(entity, ident)
        return None


class TestGoogleOAuthAndResetPassword(unittest.IsolatedAsyncioTestCase):
    """Pengujian Unit & Integrasi Google OAuth 2.0 & Alur Pemulihan Kata Sandi."""

    # =========================================================================
    # 1. TEST SUITE: Alur Lupa Sandi & Reset Kata Sandi
    # =========================================================================

    async def test_forgot_password_zero_leakage_and_dispatches_email(self):
        """POST /auth/forgot-password sukses tanpa membocorkan token di body response (OWASP Zero-Leak)."""
        user = User(
            id=uuid.uuid4(),
            email="siti@kampus.ac.id",
            full_name="Siti Mahasiswa",
            password_hash=get_password_hash("VeriText#2026"),
            role="FREE",
            is_active=True,
        )

        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([user]))

        with patch("app.api.v1.auth.send_password_reset_email") as mock_email:
            req = ForgotPasswordRequest(email="siti@kampus.ac.id")
            resp = await auth_router.forgot_password(req=req, db=mock_db)

        self.assertTrue(resp.success)
        self.assertEqual(resp.data, {})
        mock_email.assert_called_once()
        added_resets = [r for r in mock_db.added if isinstance(r, PasswordReset)]
        self.assertEqual(len(added_resets), 1)
        self.assertIsNotNone(added_resets[0].token_hash)
        self.assertFalse(added_resets[0].is_used)

    async def test_reset_password_full_lifecycle_and_session_revocation(self):
        """Memverifikasi reset kata sandi, perubahan hash, dan pembatalan sesi lama."""
        user = User(
            id=uuid.uuid4(),
            email="siti@kampus.ac.id",
            full_name="Siti Mahasiswa",
            password_hash=get_password_hash("OldPassword#123"),
            role="FREE",
            is_active=True,
        )

        raw_token = "secure_reset_token_64_characters_long_random_value!"
        reset_entry = PasswordReset(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        mock_db = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([reset_entry]),
            get_handler=lambda e, ident: user,
        )

        req = ResetPasswordRequest(token=raw_token, new_password="NewSecurePass#2026")
        resp = await auth_router.reset_password(req=req, db=mock_db)

        self.assertTrue(resp.success)
        self.assertTrue(verify_password("NewSecurePass#2026", user.password_hash))
        self.assertFalse(verify_password("OldPassword#123", user.password_hash))
        self.assertTrue(reset_entry.is_used)

    async def test_reset_password_expired_token_rejected(self):
        """Token reset yang telah kedaluwarsa harus ditolak dengan HTTP 400."""
        user = User(
            id=uuid.uuid4(),
            email="siti@kampus.ac.id",
            full_name="Siti Mahasiswa",
            password_hash=get_password_hash("OldPassword#123"),
            role="FREE",
            is_active=True,
        )

        raw_token = "expired_token_value_random!"
        expired_entry = PasswordReset(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        )

        mock_db = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([expired_entry]),
            get_handler=lambda e, ident: user,
        )

        req = ResetPasswordRequest(token=raw_token, new_password="NewSecurePass#2026")
        with self.assertRaises(HTTPException) as ctx:
            await auth_router.reset_password(req=req, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expired", ctx.exception.detail.lower())

    async def test_reset_password_reused_token_rejected(self):
        """Token reset yang sudah pernah digunakan harus ditolak (Anti-replay)."""
        user = User(
            id=uuid.uuid4(),
            email="siti@kampus.ac.id",
            full_name="Siti Mahasiswa",
            password_hash=get_password_hash("OldPassword#123"),
            role="FREE",
            is_active=True,
        )

        raw_token = "already_used_token_value!"
        used_entry = PasswordReset(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            used_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )

        mock_db = MockAsyncSession(
            execute_handler=lambda s: MockQueryResult([used_entry]),
            get_handler=lambda e, ident: user,
        )

        req = ResetPasswordRequest(token=raw_token, new_password="NewSecurePass#2026")
        with self.assertRaises(HTTPException) as ctx:
            await auth_router.reset_password(req=req, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been used", ctx.exception.detail)

    # =========================================================================
    # 2. TEST SUITE: Google OAuth 2.0 Endpoints
    # =========================================================================

    async def test_google_login_redirect_and_sets_cookie(self):
        """GET /auth/google/login mengarahkan ke Google OAuth dan memasang cookie CSRF state."""
        resp = await auth_router.google_login()
        self.assertEqual(resp.status_code, status.HTTP_307_TEMPORARY_REDIRECT)
        self.assertIn("Location", resp.headers)
        location = resp.headers["Location"]
        self.assertIn("accounts.google.com", location)
        self.assertIn("set-cookie", resp.headers)
        self.assertIn("g_oauth_state=", resp.headers["set-cookie"])

    async def test_google_login_503_when_client_id_empty(self):
        """GET /auth/google/login mengembalikan 503 jika GOOGLE_CLIENT_ID kosong."""
        with patch.object(settings, "GOOGLE_CLIENT_ID", ""):
            with self.assertRaises(HTTPException) as ctx:
                await auth_router.google_login()
            self.assertEqual(ctx.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    async def test_google_callback_state_mismatch_rejected(self):
        """GET /auth/google/callback menolak permintaan jika state query tidak cocok dengan cookie."""
        mock_req = MagicMock()
        mock_req.cookies = {"g_oauth_state": "expected_state_abc"}
        mock_db = MockAsyncSession()

        resp = await auth_router.google_callback(
            code="mock_code",
            state="tampered_state_xyz",
            request=mock_req,
            db=mock_db,
        )
        self.assertEqual(resp.status_code, status.HTTP_307_TEMPORARY_REDIRECT)
        location = resp.headers.get("Location", "")
        self.assertIn("/login?oauth_error=", location)
        self.assertIn("state", location.lower())

    async def test_google_callback_missing_state_cookie_rejected(self):
        """GET /auth/google/callback menolak jika cookie g_oauth_state tidak ada."""
        mock_req = MagicMock()
        mock_req.cookies = {}
        mock_db = MockAsyncSession()

        resp = await auth_router.google_callback(
            code="mock_code",
            state="some_state",
            request=mock_req,
            db=mock_db,
        )
        self.assertEqual(resp.status_code, status.HTTP_307_TEMPORARY_REDIRECT)
        self.assertIn("/login?oauth_error=", resp.headers.get("Location", ""))

    async def test_google_callback_unverified_email_rejected(self):
        """GET /auth/google/callback menolak email yang verified_email=False dari Google."""
        mock_req = MagicMock()
        mock_req.cookies = {"g_oauth_state": "matching_state"}
        mock_db = MockAsyncSession()

        token_resp = MagicMock(status_code=200)
        token_resp.json.return_value = {"access_token": "valid_token"}

        userinfo_resp = MagicMock(status_code=200)
        userinfo_resp.json.return_value = {
            "email": "unverified@kampus.ac.id",
            "name": "Unverified User",
            "verified_email": False,
        }

        with patch("httpx.AsyncClient.post", return_value=token_resp), patch(
            "httpx.AsyncClient.get", return_value=userinfo_resp
        ):
            resp = await auth_router.google_callback(
                code="valid_code",
                state="matching_state",
                request=mock_req,
                db=mock_db,
            )

        self.assertEqual(resp.status_code, status.HTTP_307_TEMPORARY_REDIRECT)
        self.assertIn("belum", resp.headers.get("Location", ""))

    async def test_google_callback_existing_user_creates_session_no_is_new_user(self):
        """GET /auth/google/callback untuk user terdaftar membuat sesi dan tidak menyertakan is_new_user."""
        existing_user = User(
            id=uuid.uuid4(),
            full_name="Mahasiswa Terdaftar",
            email="existing@kampus.ac.id",
            role="FREE",
            is_active=True,
            password_hash="hashed",
            created_at=datetime.now(timezone.utc),
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult(scalar_val=existing_user))
        mock_req = MagicMock()
        mock_req.cookies = {"g_oauth_state": "matching_state"}
        mock_req.client.host = "127.0.0.1"

        token_resp = MagicMock(status_code=200)
        token_resp.json.return_value = {"access_token": "valid_token"}
        userinfo_resp = MagicMock(status_code=200)
        userinfo_resp.json.return_value = {
            "email": "existing@kampus.ac.id",
            "name": "Mahasiswa Terdaftar",
            "verified_email": True,
        }

        with patch("httpx.AsyncClient.post", return_value=token_resp), patch(
            "httpx.AsyncClient.get", return_value=userinfo_resp
        ):
            resp = await auth_router.google_callback(
                code="google_code",
                state="matching_state",
                request=mock_req,
                db=mock_db,
            )

        self.assertEqual(resp.status_code, status.HTTP_307_TEMPORARY_REDIRECT)
        location = resp.headers.get("Location", "")
        self.assertIn("/auth/callback", location)
        self.assertIn("token=", location)
        self.assertNotIn("is_new_user", location)
        added_sessions = [s for s in mock_db.added if isinstance(s, Session)]
        self.assertEqual(len(added_sessions), 1)

    async def test_google_callback_new_user_redirects_onboarding_without_db_creation(self):
        """GET /auth/google/callback untuk user baru membuat ticket signup dan TIDAK membuat user di DB."""
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        mock_req = MagicMock()
        mock_req.cookies = {"g_oauth_state": "matching_state"}
        mock_req.client.host = "127.0.0.1"

        token_resp = MagicMock(status_code=200)
        token_resp.json.return_value = {"access_token": "valid_token"}
        userinfo_resp = MagicMock(status_code=200)
        userinfo_resp.json.return_value = {
            "email": "new.student@kampus.ac.id",
            "name": "New Student",
            "verified_email": True,
        }

        with patch("httpx.AsyncClient.post", return_value=token_resp), patch(
            "httpx.AsyncClient.get", return_value=userinfo_resp
        ):
            resp = await auth_router.google_callback(
                code="google_code",
                state="matching_state",
                request=mock_req,
                db=mock_db,
            )

        self.assertEqual(resp.status_code, status.HTTP_307_TEMPORARY_REDIRECT)
        location = resp.headers.get("Location", "")
        self.assertIn("/onboarding?ticket=", location)

        parsed = urlparse(location)
        qs = parse_qs(parsed.query)
        ticket = qs["ticket"][0]
        payload = decode_signup_ticket(ticket)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["email"], "new.student@kampus.ac.id")
        self.assertEqual(payload["name"], "New Student")
        self.assertEqual(payload["purpose"], "google_signup")

        # Invarian penting: TIDAK ADA user atau wallet yang dibuat di DB saat callback
        self.assertEqual(len(mock_db.added), 0)

    # =========================================================================
    # 3. TEST SUITE: Google Verify Token (POST /google/verify)
    # =========================================================================

    async def test_google_verify_existing_user_returns_session(self):
        """POST /auth/google/verify untuk user terdaftar mengembalikan access token sesi."""
        existing_user = User(
            id=uuid.uuid4(),
            full_name="Verified Google Student",
            email="verified.google.user@kampus.ac.id",
            role="FREE",
            is_active=True,
            password_hash="hashed",
            created_at=datetime.now(timezone.utc),
        )
        mock_google_tokeninfo = {
            "email": "verified.google.user@kampus.ac.id",
            "name": "Verified Google Student",
            "aud": settings.GOOGLE_CLIENT_ID,
            "email_verified": "true",
        }

        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = mock_google_tokeninfo

        wallet = TokenWallet(user_id=existing_user.id, balance=5)

        def db_handler(statement):
            stmt_text = str(statement)
            if "token_wallets" in stmt_text:
                return MockQueryResult([wallet])
            return MockQueryResult([existing_user])

        mock_db = MockAsyncSession(execute_handler=db_handler)
        mock_req = MagicMock()
        mock_req.client.host = "127.0.0.1"
        mock_resp_obj = MagicMock()

        req = GoogleVerifyRequest(credential="mock-valid-google-id-token-jwt-string")

        with patch("httpx.AsyncClient.get", return_value=mock_resp):
            api_resp = await auth_router.google_verify_token(
                req=req,
                request=mock_req,
                response=mock_resp_obj,
                db=mock_db,
            )

        self.assertTrue(api_resp.success)
        self.assertIsNotNone(api_resp.data.access_token)
        self.assertEqual(api_resp.data.user.email, "verified.google.user@kampus.ac.id")

    async def test_google_verify_new_user_returns_409_with_signup_ticket(self):
        """POST /auth/google/verify untuk email baru mengembalikan 409 SIGNUP_REQUIRED dan ticket."""
        mock_google_tokeninfo = {
            "email": "fresh.user@kampus.ac.id",
            "name": "Fresh Google User",
            "aud": settings.GOOGLE_CLIENT_ID,
            "email_verified": True,
        }

        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = mock_google_tokeninfo
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        mock_req = MagicMock()
        mock_resp_obj = MagicMock()

        req = GoogleVerifyRequest(credential="mock-valid-google-id-token")

        with patch("httpx.AsyncClient.get", return_value=mock_resp):
            with self.assertRaises(HTTPException) as ctx:
                await auth_router.google_verify_token(
                    req=req,
                    request=mock_req,
                    response=mock_resp_obj,
                    db=mock_db,
                )

        self.assertEqual(ctx.exception.status_code, status.HTTP_409_CONFLICT)
        detail = ctx.exception.detail
        self.assertIsInstance(detail, dict)
        self.assertEqual(detail.get("code"), "SIGNUP_REQUIRED")
        ticket = detail.get("signup_ticket")
        self.assertIsNotNone(ticket)
        payload = decode_signup_ticket(ticket)
        self.assertEqual(payload["email"], "fresh.user@kampus.ac.id")
        self.assertEqual(payload["purpose"], "google_signup")

    async def test_google_verify_invalid_aud_rejected(self):
        """POST /auth/google/verify menolak ID token dengan audience yang tidak cocok."""
        mock_google_tokeninfo = {
            "email": "student@kampus.ac.id",
            "aud": "attacker_google_client_id.apps.googleusercontent.com",
            "email_verified": True,
        }
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = mock_google_tokeninfo
        mock_db = MockAsyncSession()

        req = GoogleVerifyRequest(credential="mock-token-wrong-aud")

        with patch("httpx.AsyncClient.get", return_value=mock_resp):
            with self.assertRaises(HTTPException) as ctx:
                await auth_router.google_verify_token(req=req, db=mock_db)
            self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Audience", ctx.exception.detail)

    async def test_google_verify_unverified_email_rejected(self):
        """POST /auth/google/verify menolak ID token jika email belum diverifikasi Google."""
        mock_google_tokeninfo = {
            "email": "student@kampus.ac.id",
            "aud": settings.GOOGLE_CLIENT_ID,
            "email_verified": False,
        }
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = mock_google_tokeninfo
        mock_db = MockAsyncSession()

        req = GoogleVerifyRequest(credential="mock-token-unverified")

        with patch("httpx.AsyncClient.get", return_value=mock_resp):
            with self.assertRaises(HTTPException) as ctx:
                await auth_router.google_verify_token(req=req, db=mock_db)
            self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("belum diverifikasi", ctx.exception.detail)

    # =========================================================================
    # 4. TEST SUITE: Google Complete Registration (POST /auth/google/complete)
    # =========================================================================

    async def test_google_complete_creates_free_user_and_5_tokens(self):
        """POST /auth/google/complete membuat akun FREE dengan saldo 5 token dan sesi aktif."""
        ticket = create_signup_ticket(email="complete.user@kampus.ac.id", name="Complete Student")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))
        mock_req = MagicMock()
        mock_req.client.host = "127.0.0.1"
        mock_resp_obj = MagicMock()

        req = GoogleCompleteRequest(
            ticket=ticket,
            full_name="Complete Student",
            password="SandiKuat@2026!",
        )

        resp = await auth_router.google_complete(
            req=req,
            request=mock_req,
            response=mock_resp_obj,
            db=mock_db,
        )

        self.assertTrue(resp.success)
        self.assertEqual(resp.data.user.email, "complete.user@kampus.ac.id")
        self.assertEqual(resp.data.user.role, "FREE")
        self.assertEqual(resp.data.user.token_balance, 5)

        # Verifikasi objek User & TokenWallet & Session tersimpan di database
        added_users = [u for u in mock_db.added if isinstance(u, User)]
        self.assertEqual(len(added_users), 1)
        self.assertEqual(added_users[0].email, "complete.user@kampus.ac.id")

        added_wallets = [w for w in mock_db.added if isinstance(w, TokenWallet)]
        self.assertEqual(len(added_wallets), 1)
        self.assertEqual(added_wallets[0].balance, 5)
        self.assertEqual(added_wallets[0].ai_trial_remaining, 3)

        added_sessions = [s for s in mock_db.added if isinstance(s, Session)]
        self.assertEqual(len(added_sessions), 1)
        self.assertTrue(mock_db.committed)

    async def test_google_complete_invalid_or_expired_ticket_rejected(self):
        """POST /auth/google/complete menolak tiket yang tidak valid atau salah tujuan."""
        mock_db = MockAsyncSession()
        req_invalid = GoogleCompleteRequest(
            ticket="completely_invalid_jwt_string",
            full_name="Test User",
            password="SandiKuat@2026!",
        )

        with self.assertRaises(HTTPException) as ctx:
            await auth_router.google_complete(req=req_invalid, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_google_complete_already_registered_email_rejected(self):
        """POST /auth/google/complete menolak jika email tiket sudah terdaftar di sistem (409 Conflict)."""
        existing_user = User(
            id=uuid.uuid4(),
            email="already.registered@kampus.ac.id",
            full_name="Already Registered",
            role="FREE",
            is_active=True,
        )
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult(scalar_val=existing_user))
        ticket = create_signup_ticket(email="already.registered@kampus.ac.id", name="Already Registered")

        req = GoogleCompleteRequest(
            ticket=ticket,
            full_name="Already Registered",
            password="SandiKuat@2026!",
        )

        with self.assertRaises(HTTPException) as ctx:
            await auth_router.google_complete(req=req, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_409_CONFLICT)

    async def test_google_complete_weak_password_rejected(self):
        """POST /auth/google/complete menolak kata sandi yang lemah."""
        ticket = create_signup_ticket(email="user@kampus.ac.id", name="User")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))

        req_weak = GoogleCompleteRequest(
            ticket=ticket,
            full_name="User Valid",
            password="weakpassword",
        )

        with self.assertRaises(HTTPException) as ctx:
            await auth_router.google_complete(req=req_weak, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_google_complete_short_name_rejected(self):
        """POST /auth/google/complete memvalidasi panjang nama lengkap minimal 2 karakter."""
        ticket = create_signup_ticket(email="user@kampus.ac.id", name="User")
        mock_db = MockAsyncSession(execute_handler=lambda s: MockQueryResult([]))

        req_short_name = GoogleCompleteRequest(
            ticket=ticket,
            full_name="  A  ",
            password="SandiKuat@2026!",
        )

        with self.assertRaises(HTTPException) as ctx:
            await auth_router.google_complete(req=req_short_name, db=mock_db)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)

    # =========================================================================
    # 5. TEST SUITE: Email-Only Login (Alias Reverted)
    # =========================================================================

    def test_login_schema_rejects_alias_requires_valid_email(self):
        """UserLoginRequest menolak login dengan alias non-email dan mewajibkan EmailStr valid."""
        for alias in ["azrlb1", "azrlb2", "azrlb3", "admin_alias"]:
            with self.assertRaises(ValidationError):
                UserLoginRequest(email=alias, password="AnyPassword123!")

        valid_req = UserLoginRequest(email="azrielalbian23@gmail.com", password="AnyPassword123!")
        self.assertEqual(valid_req.email, "azrielalbian23@gmail.com")
