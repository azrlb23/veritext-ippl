import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import HTTPException, Response
import jwt

from app.api.deps import require_role
from app.api.v1 import auth as auth_router
from app.api.v1.auth_helpers import set_refresh_cookie
from app.core.config import settings
from app.core.security import create_oauth_state, decode_access_token, get_password_hash, hash_token
from app.engine.web_cache import BoundedTTLCache
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, GoogleExchangeRequest, ResetPasswordRequest


class _Result:
    def __init__(self, items=None):
        self._items = items or []

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None


class _MockDB:
    def __init__(self, exec_fn=None, get_fn=None):
        self._exec_fn = exec_fn
        self._get_fn = get_fn
        self.added, self.executed = [], []
        self.committed = False

    async def execute(self, stmt):
        self.executed.append(stmt)
        return self._exec_fn(stmt) if self._exec_fn else _Result()

    async def get(self, entity, ident):
        return self._get_fn(entity, ident) if self._get_fn else None

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def flush(self):
        pass


class TestAuditSecurityAndRobustnessFixes(unittest.IsolatedAsyncioTestCase):
    async def test_reset_password_rejects_raw_token_hash_and_weak_password(self):
        raw = "real_secret_token_32chars_long_1234"
        hashed = hash_token(raw)
        entry = PasswordReset(
            id=uuid.uuid4(), user_id=uuid.uuid4(), token_hash=hashed,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db = _MockDB(exec_fn=lambda s: _Result([]))
        with self.assertRaises(HTTPException) as ctx_raw:
            await auth_router.reset_password(req=ResetPasswordRequest(token=hashed, new_password="StrongPass#2026"), db=db)
        self.assertEqual(ctx_raw.exception.status_code, 400)

        with self.assertRaises(HTTPException) as ctx_weak:
            await auth_router.reset_password(req=ResetPasswordRequest(token=raw, new_password="weakpassword"), db=db)
        self.assertEqual(ctx_weak.exception.status_code, 400)

    async def test_otp_brute_force_locks_after_5_failures(self):
        email = f"brute-{uuid.uuid4().hex[:8]}@kampus.ac.id"
        user = User(id=uuid.uuid4(), full_name="U", email=email, role="FREE", is_active=True, password_hash="x")
        db = _MockDB(exec_fn=lambda s: _Result([]))
        for i in range(4):
            with self.assertRaises(HTTPException) as ctx:
                await auth_router.reset_password(req=ResetPasswordRequest(email=email, otp="000000", new_password="StrongPass#2026"), db=db)
            self.assertEqual(ctx.exception.status_code, 400)
        def exec_fn(stmt):
            if "FROM users" in str(stmt):
                return _Result([user])
            return _Result([])

        db_user = _MockDB(exec_fn=exec_fn)
        with self.assertRaises(HTTPException) as ctx_lock:
            await auth_router.reset_password(req=ResetPasswordRequest(email=email, otp="000000", new_password="StrongPass#2026"), db=db_user)
        self.assertEqual(ctx_lock.exception.status_code, 429)

    async def test_change_password_enforces_strong_password(self):
        user = User(id=uuid.uuid4(), full_name="U", email="u@k.ac.id", role="FREE", is_active=True, password_hash=get_password_hash("OldPass#2026"))
        with self.assertRaises(HTTPException) as ctx:
            await auth_router.change_password(req=ChangePasswordRequest(old_password="OldPass#2026", new_password="onlylowercase"), current_user=user, db=_MockDB())
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_google_exchange_code_is_one_time_only(self):
        from app.api.v1.auth_oauth_codes import store_oauth_exchange_code
        user = User(id=uuid.uuid4(), full_name="G User", email="g@k.ac.id", role="FREE", is_active=True, created_at=datetime.now(timezone.utc))
        code = await store_oauth_exchange_code(str(user.id), "refresh_tok_xyz")
        db = _MockDB(exec_fn=lambda s: _Result([]), get_fn=lambda e, i: user)
        resp = Response()
        res = await auth_router._google_mod.google_exchange_code(req=GoogleExchangeRequest(code=code), response=resp, db=db)
        self.assertTrue(res.data.access_token)
        self.assertIn("refresh_token=refresh_tok_xyz", resp.headers.get("set-cookie", ""))
        with self.assertRaises(HTTPException) as ctx_reuse:
            await auth_router._google_mod.google_exchange_code(req=GoogleExchangeRequest(code=code), response=Response(), db=db)
        self.assertEqual(ctx_reuse.exception.status_code, 400)

    async def test_decode_access_token_requires_type_access_and_strict_require_role(self):
        non_access = jwt.encode({"sub": str(uuid.uuid4()), "type": "refresh"}, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        self.assertIsNone(decode_access_token(non_access))
        self.assertIsNone(decode_access_token(create_oauth_state("login")))

        checker = require_role("FREE", "PREMIUM")
        admin = User(id=uuid.uuid4(), full_name="A", email="a@k.ac.id", role="ADMIN", is_active=True)
        with self.assertRaises(HTTPException) as ctx:
            await checker(current_user=admin)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_set_refresh_cookie_secure_in_production_and_bounded_cache(self):
        resp = Response()
        with patch.object(settings, "ENVIRONMENT", "production"):
            set_refresh_cookie(resp, "tok", 7)
        self.assertIn("Secure", resp.headers.get("set-cookie", ""))

        cache: BoundedTTLCache[str] = BoundedTTLCache(max_size=2, ttl_s=60)
        cache.set("a", "1")
        cache.set("b", "2")
        cache.get("a")
        cache.set("c", "3")
        self.assertFalse("b" in cache)
        self.assertTrue("a" in cache and "c" in cache)
