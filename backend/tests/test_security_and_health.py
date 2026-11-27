from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core import health_checks
from app.core.rate_limiter import (
    RateLimiter,
    enforce_rate_limit,
    extract_client_ip,
    match_rate_rule,
)
from app.main import app


def _fake_request(method: str, path: str, headers: dict | None = None, host: str = "10.0.0.5"):
    norm_headers = {k.lower(): v for k, v in (headers or {}).items()}
    return SimpleNamespace(
        method=method,
        url=SimpleNamespace(path=path),
        headers=norm_headers,
        client=SimpleNamespace(host=host),
    )


def test_rate_limiter_memory_fallback_enforces_limit():
    limiter = RateLimiter(redis_url="redis://127.0.0.1:65432/0")
    for _ in range(3):
        allowed, retry_after = limiter.check("login:1.2.3.4", limit=3, window_s=60)
        assert allowed is True
        assert retry_after == 0

    blocked, retry_after = limiter.check("login:1.2.3.4", limit=3, window_s=60)
    assert blocked is False
    assert retry_after > 0


def test_match_rate_rule_mutating_vs_get():
    assert match_rate_rule("/api/v1/auth/login", "POST") == (15, 60)
    assert match_rate_rule("/api/v1/auth/forgot-password", "post") == (10, 60)
    assert match_rate_rule("/api/v1/auth/reset-password", "POST") == (10, 60)
    assert match_rate_rule("/api/v1/auth/google/verify", "POST") == (20, 60)
    assert match_rate_rule("/api/v1/documents/upload", "POST") == (20, 60)
    assert match_rate_rule("/api/v1/chat/sessions", "POST") == (30, 60)
    assert match_rate_rule("/api/v1/auth/me", "GET") is None
    assert match_rate_rule("/api/v1/auth/login", "GET") is None


def test_extract_client_ip_x_forwarded_for():
    req = _fake_request(
        "POST",
        "/api/v1/auth/login",
        headers={"X-Forwarded-For": " 203.0.113.42 , 10.0.0.1 "},
        host="127.0.0.1",
    )
    assert extract_client_ip(req) == "203.0.113.42"

    req_direct = _fake_request("POST", "/api/v1/auth/login", host="192.168.1.9")
    assert extract_client_ip(req_direct) == "192.168.1.9"


def test_enforce_rate_limit_returns_429_when_forced():
    limiter = RateLimiter(redis_url="")
    req = _fake_request("POST", "/api/v1/auth/forgot-password", host="198.51.100.7")
    for _ in range(10):
        assert enforce_rate_limit(req, limiter=limiter, force=True) is None
    resp = enforce_rate_limit(req, limiter=limiter, force=True)
    assert resp is not None
    assert resp.status_code == 429
    assert int(resp.headers["Retry-After"]) > 0


def test_health_endpoint_healthy_and_degraded_no_secret_leak():
    client = TestClient(app)

    with patch("app.main.check_system_health", return_value=(True, {"postgres": "ok", "redis": "ok"})):
        res_ok = client.get("/health")
    assert res_ok.status_code == 200
    body_ok = res_ok.json()
    assert body_ok["status"] == "healthy"
    assert body_ok["dependencies"] == {"postgres": "ok", "redis": "ok"}

    with patch(
        "app.main.check_system_health",
        return_value=(False, {"postgres": "unavailable", "redis": "ok"}),
    ):
        res_err = client.get("/health")
    assert res_err.status_code == 503
    body_err = res_err.json()
    assert body_err["status"] == "degraded"
    assert body_err["dependencies"] == {"postgres": "unavailable", "redis": "ok"}
    raw_text = res_err.text.lower()
    assert "postgresql://" not in raw_text
    assert "redis://" not in raw_text
    assert "password" not in raw_text


def test_check_system_health_masks_connection_errors():
    with (
        patch.object(health_checks.sync_engine, "connect", side_effect=RuntimeError("postgresql://user:secret@host/db")),
        patch.object(health_checks.redis, "from_url", side_effect=RuntimeError("redis://:secret@host:6379/0")),
    ):
        all_ok, deps = health_checks.check_system_health()
    assert all_ok is False
    assert deps == {"postgres": "unavailable", "redis": "unavailable"}
