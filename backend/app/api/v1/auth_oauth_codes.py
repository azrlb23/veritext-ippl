from __future__ import annotations

import json
import logging
import secrets
import time
from collections import OrderedDict

from app.core.config import settings
from app.core.security import hash_token

logger = logging.getLogger(__name__)

OAUTH_CODE_TTL_S = 60
_LOCAL_OAUTH_CODES: OrderedDict[str, tuple[dict[str, str], float]] = OrderedDict()


def _prune_local_codes(now: float) -> None:
    expired = [k for k, (_, exp) in _LOCAL_OAUTH_CODES.items() if exp <= now]
    for k in expired:
        _LOCAL_OAUTH_CODES.pop(k, None)
    while len(_LOCAL_OAUTH_CODES) > 500:
        _LOCAL_OAUTH_CODES.popitem(last=False)


async def store_oauth_exchange_code(user_id: str, refresh_token: str) -> str:
    """Menyimpan kode pertukaran OAuth sekali pakai berumur singkat (60 detik)."""
    code = secrets.token_urlsafe(32)
    key = f"oauth_code:{hash_token(code)}"
    payload = json.dumps({"user_id": user_id, "refresh_token": refresh_token})
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=0.3, socket_timeout=0.3)
        try:
            await client.set(key, payload, ex=OAUTH_CODE_TTL_S)
            return code
        finally:
            await client.aclose()
    except Exception as err:  # noqa: BLE001
        logger.debug("Redis tidak tersedia untuk oauth_code, gunakan fallback memori: %s", err)

    now = time.time()
    _prune_local_codes(now)
    _LOCAL_OAUTH_CODES[key] = ({"user_id": user_id, "refresh_token": refresh_token}, now + OAUTH_CODE_TTL_S)
    return code


async def consume_oauth_exchange_code(code: str) -> dict[str, str] | None:
    """Mengambil dan langsung menghapus kode pertukaran OAuth (sekali pakai)."""
    if not code or not code.strip():
        return None
    key = f"oauth_code:{hash_token(code.strip())}"
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=0.3, socket_timeout=0.3)
        try:
            raw = await client.getdel(key)
            if raw:
                return json.loads(raw)
        finally:
            await client.aclose()
    except Exception as err:  # noqa: BLE001
        logger.debug("Redis tidak tersedia untuk consume oauth_code, cek fallback memori: %s", err)

    now = time.time()
    _prune_local_codes(now)
    item = _LOCAL_OAUTH_CODES.pop(key, None)
    if item and item[1] > now:
        return item[0]
    return None
