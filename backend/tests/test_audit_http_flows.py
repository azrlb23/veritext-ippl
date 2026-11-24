import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.api.v1.auth_oauth_codes import store_oauth_exchange_code
from app.core.database import get_db
from app.core.security import hash_token
from app.main import app
from app.models.session import Session
from app.models.user import User


class _Result:
    def __init__(self, items=None):
        self._items = items or []

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None


class _FakeDB:
    def __init__(self, exec_fn=None, get_fn=None):
        self._exec_fn = exec_fn
        self._get_fn = get_fn
        self.committed = False

    async def execute(self, stmt):
        return self._exec_fn(stmt) if self._exec_fn else _Result()

    async def get(self, entity, ident):
        return self._get_fn(entity, ident) if self._get_fn else None

    async def commit(self):
        self.committed = True

    async def delete(self, obj):
        pass


def test_http_rate_limit_login_and_forgot_password_returns_429():
    db = _FakeDB()

    async def _override_db():
        yield db

    app.dependency_overrides[get_db] = _override_db
    try:
        client = TestClient(app)
        with patch("app.api.v1.auth.enforce_rate_limit", new=AsyncMock()) as rl_login:
            from fastapi import HTTPException

            rl_login.side_effect = HTTPException(status_code=429, detail="Too many login attempts")
            resp = client.post("/api/v1/auth/login", json={"email": "u@kampus.ac.id", "password": "Password1!"})
            assert resp.status_code == 429
            rl_login.assert_awaited_once()

        with patch("app.api.v1.auth_password_reset.enforce_rate_limit", new=AsyncMock()) as rl_forgot:
            from fastapi import HTTPException

            rl_forgot.side_effect = HTTPException(status_code=429, detail="Too many reset requests")
            resp2 = client.post("/api/v1/auth/forgot-password", json={"email": "u@kampus.ac.id"})
            assert resp2.status_code == 429
            rl_forgot.assert_awaited_once()
    finally:
        app.dependency_overrides.pop(get_db, None)


async def test_http_google_exchange_sets_cookie_and_refresh_rotates_without_json_refresh_token():
    user = User(
        id=uuid.uuid4(), full_name="OAuth User", email="oauth@kampus.ac.id",
        role="FREE", is_active=True, created_at=datetime.now(timezone.utc),
    )
    raw_refresh = "refresh_cookie_secret_1234567890"
    sess = Session(
        id=uuid.uuid4(), user_id=user.id,
        refresh_token_hash=hash_token(raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    code = await store_oauth_exchange_code(str(user.id), raw_refresh)

    def exec_fn(stmt):
        s = str(stmt)
        if "FROM sessions" in s:
            return _Result([sess])
        return _Result([])

    db = _FakeDB(exec_fn=exec_fn, get_fn=lambda e, i: user if i == user.id else None)

    async def _override_db():
        yield db

    app.dependency_overrides[get_db] = _override_db
    try:
        client = TestClient(app)
        ex_resp = client.post("/api/v1/auth/google/exchange", json={"code": code})
        assert ex_resp.status_code == 200
        ex_data = ex_resp.json()["data"]
        assert ex_data["access_token"]
        assert "refresh_token" not in ex_data
        assert client.cookies.get("refresh_token") == raw_refresh

        ref_resp = client.post("/api/v1/auth/refresh")
        assert ref_resp.status_code == 200
        ref_data = ref_resp.json()["data"]
        assert ref_data["access_token"]
        assert "refresh_token" not in ref_data
        assert client.cookies.get("refresh_token") != raw_refresh
    finally:
        app.dependency_overrides.pop(get_db, None)
