from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import MagicMock, patch
import uuid

from fastapi import HTTPException, status

from app.api.v1 import auth as auth_router
from app.core.security import (
    create_oauth_state,
    get_password_hash,
    hash_token,
    verify_oauth_state,
    verify_password,
)
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest


class _Result:
    def __init__(self, items=None):
        self._items = items or []

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None


class _MockDB:
    def __init__(self, execute_fn=None, get_fn=None):
        self.execute_fn = execute_fn
        self.get_fn = get_fn
        self.added = []
        self.executed = []
        self.committed = False

    async def execute(self, stmt):
        self.executed.append(stmt)
        return self.execute_fn(stmt) if self.execute_fn else _Result([])

    def add(self, item):
        self.added.append(item)

    async def commit(self):
        self.committed = True

    async def get(self, entity, ident):
        return self.get_fn(entity, ident) if self.get_fn else None


class TestAuthAccountUpgrades(unittest.IsolatedAsyncioTestCase):
    def test_oauth_state_jwt_valid_invalid_and_reset_intent(self):
        login_state = create_oauth_state("login")
        reset_state = create_oauth_state("reset")
        self.assertEqual(verify_oauth_state(login_state)["intent"], "login")
        self.assertEqual(verify_oauth_state(reset_state)["intent"], "reset")
        self.assertIsNone(verify_oauth_state(""))
        self.assertIsNone(verify_oauth_state("not.a.valid.jwt"))

    async def test_google_callback_reset_intent_redirects_to_reset_password(self):
        user = User(
            id=uuid.uuid4(), full_name="Reset User", email="reset@kampus.ac.id",
            role="FREE", is_active=True, password_hash=get_password_hash("OldPass#123"),
        )
        db = _MockDB(execute_fn=lambda s: _Result([user]))
        token_resp = MagicMock(status_code=200)
        token_resp.json.return_value = {"access_token": "tok"}
        info_resp = MagicMock(status_code=200)
        info_resp.json.return_value = {"email": "reset@kampus.ac.id", "name": "Reset User", "verified_email": True}

        reset_state = create_oauth_state("reset")
        mock_req = MagicMock()
        mock_req.cookies = {"vt_oauth_state": reset_state}
        with patch("httpx.AsyncClient.post", return_value=token_resp), patch("httpx.AsyncClient.get", return_value=info_resp):
            resp = await auth_router.google_callback(code="c", state=reset_state, request=mock_req, db=db)

        self.assertEqual(resp.status_code, status.HTTP_307_TEMPORARY_REDIRECT)
        self.assertIn("/reset-password?token=", resp.headers.get("Location", ""))
        self.assertTrue(any("update" in str(s).lower() and "password_resets" in str(s).lower() for s in db.executed))
        self.assertEqual(len([x for x in db.added if isinstance(x, PasswordReset)]), 1)
        self.assertTrue(db.committed)

    async def test_forgot_and_reset_password_with_otp_and_token_compat(self):
        user = User(
            id=uuid.uuid4(), full_name="OTP User", email="otp@kampus.ac.id",
            role="FREE", is_active=True, password_hash=get_password_hash("OldPass#123"),
        )
        captured = {}

        def fake_email(**kwargs):
            captured.update(kwargs)

        db_forgot = _MockDB(execute_fn=lambda s: _Result([user]))
        with patch("app.api.v1.auth.send_password_reset_email", side_effect=fake_email):
            resp = await auth_router.forgot_password(req=ForgotPasswordRequest(email="otp@kampus.ac.id"), db=db_forgot)

        self.assertTrue(resp.success)
        otp = captured["otp_code"]
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
        self.assertIn(f"otp={otp}", captured["reset_url"])

        entry = PasswordReset(
            id=uuid.uuid4(), user_id=user.id,
            token_hash=hash_token(f"otp@kampus.ac.id:{otp}"),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db_reset = _MockDB(execute_fn=lambda s: _Result([entry]), get_fn=lambda e, i: user)
        req_otp = ResetPasswordRequest(email="otp@kampus.ac.id", otp=otp, new_password="NewOtpPass#2026")
        res_otp = await auth_router.reset_password(req=req_otp, db=db_reset)
        self.assertTrue(res_otp.success)
        self.assertTrue(verify_password("NewOtpPass#2026", user.password_hash))
        self.assertTrue(entry.is_used)

        tok_entry = PasswordReset(
            id=uuid.uuid4(), user_id=user.id, token_hash=hash_token("tok_abc"),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db_tok = _MockDB(execute_fn=lambda s: _Result([tok_entry]), get_fn=lambda e, i: user)
        res_tok = await auth_router.reset_password(req=ResetPasswordRequest(token="tok_abc", new_password="NewTokPass#2026"), db=db_tok)
        self.assertTrue(res_tok.success)
        self.assertTrue(verify_password("NewTokPass#2026", user.password_hash))

        with self.assertRaises(HTTPException) as ctx:
            await auth_router.reset_password(req=ResetPasswordRequest(new_password="AnyPass#2026"), db=db_tok)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_logout_all_revokes_all_sessions_and_clears_cookie(self):
        user = User(id=uuid.uuid4(), full_name="Sess User", email="sess@kampus.ac.id", role="FREE", is_active=True)
        db = _MockDB()
        mock_resp = MagicMock()
        res = await auth_router.logout_all(response=mock_resp, current_user=user, db=db)
        self.assertTrue(res.success)
        self.assertEqual(res.message, "Semua sesi perangkat telah diakhiri.")
        self.assertTrue(db.committed)
        self.assertEqual(len(db.executed), 1)
        mock_resp.delete_cookie.assert_called_once()
        self.assertEqual(mock_resp.delete_cookie.call_args.kwargs.get("key"), "refresh_token")
