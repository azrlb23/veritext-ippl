from __future__ import annotations

import os
import threading
import time
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
import redis

from app.core.config import settings

RATE_RULES: tuple[tuple[str, int, int], ...] = (
    ("/api/v1/auth/login", 15, 60),
    ("/api/v1/auth/register", 15, 60),
    ("/api/v1/auth/forgot-password", 10, 60),
    ("/api/v1/auth/reset-password", 10, 60),
    ("/api/v1/auth/google/", 20, 60),
    ("/api/v1/documents/upload", 20, 60),
    ("/api/v1/chat", 30, 60),
)
_MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def extract_client_ip(request: Request) -> str:
    """Safely extract client IP from X-Forwarded-For or socket client."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        first_hop = forwarded.split(",")[0].strip()
        if first_hop:
            return first_hop
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def match_rate_rule(path: str, method: str) -> Optional[tuple[int, int]]:
    """Return (limit, window_s) for mutating requests matching RATE_RULES."""
    if method.upper() not in _MUTATING_METHODS:
        return None
    for prefix, limit, window_s in RATE_RULES:
        if path.startswith(prefix):
            return limit, window_s
    return None


class RateLimiter:
    """Fixed-window rate limiter backed by Redis with thread-safe memory fallback."""

    def __init__(self, redis_url: Optional[str] = None) -> None:
        self._redis_url = redis_url if redis_url is not None else settings.REDIS_URL
        self._lock = threading.Lock()
        self._memory_store: dict[str, tuple[int, float]] = {}

    def _check_memory(self, key: str, limit: int, window_s: int) -> tuple[bool, int]:
        now = time.monotonic()
        with self._lock:
            count, reset_at = self._memory_store.get(key, (0, 0.0))
            if now >= reset_at:
                count, reset_at = 0, now + window_s
            count += 1
            self._memory_store[key] = (count, reset_at)
            if count > limit:
                return False, max(1, int(reset_at - now) + 1)
            return True, 0

    def check(self, key: str, limit: int, window_s: int) -> tuple[bool, int]:
        """Return (allowed, retry_after_s) using Redis or in-memory fallback."""
        if not self._redis_url:
            return self._check_memory(key, limit, window_s)
        client = None
        try:
            client = redis.from_url(self._redis_url, socket_connect_timeout=0.5, socket_timeout=0.5)
            redis_key = f"rl:{key}"
            count = int(client.incr(redis_key))
            if count == 1:
                client.expire(redis_key, window_s)
            if count > limit:
                ttl = int(client.ttl(redis_key) or 0)
                if ttl <= 0:
                    client.expire(redis_key, window_s)
                    ttl = window_s
                return False, max(1, ttl)
            return True, 0
        except Exception:
            return self._check_memory(key, limit, window_s)
        finally:
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass


rate_limiter = RateLimiter()


def enforce_rate_limit(
    request: Request, limiter: Optional[RateLimiter] = None, force: bool = False
) -> Optional[JSONResponse]:
    """Check rate limit for incoming request; return HTTP 429 JSONResponse if exceeded."""
    if os.getenv("PYTEST_CURRENT_TEST") and not force:
        return None
    rule = match_rate_rule(request.url.path, request.method)
    if rule is None:
        return None
    limit, window_s = rule
    key = f"{request.method.upper()}:{request.url.path}:{extract_client_ip(request)}"
    allowed, retry_after = (limiter or rate_limiter).check(key, limit, window_s)
    if not allowed:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(retry_after)},
            content={"detail": "Too many requests. Please try again later."},
        )
    return None
