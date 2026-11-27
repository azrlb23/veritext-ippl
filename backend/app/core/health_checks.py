from __future__ import annotations

import redis
from sqlalchemy import text

from app.core.config import settings
from app.core.database import sync_engine


def _check_postgres() -> str:
    """Verify PostgreSQL connectivity via a lightweight SELECT 1 probe."""
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "unavailable"


def _check_redis() -> str:
    """Verify Redis connectivity via PING with short timeouts."""
    client = None
    try:
        client = redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
        )
        if client.ping():
            return "ok"
        return "unavailable"
    except Exception:
        return "unavailable"
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass


def check_system_health() -> tuple[bool, dict[str, str]]:
    """Run live dependency checks without leaking credentials or traces."""
    deps = {
        "postgres": _check_postgres(),
        "redis": _check_redis(),
    }
    all_ok = all(state == "ok" for state in deps.values())
    return all_ok, deps
