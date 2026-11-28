from __future__ import annotations

import contextlib
import logging
import threading

from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)
_BUSY_DETAIL = "Permintaan AI sebelumnya masih diproses. Tunggu sebentar sebelum mengirim permintaan baru."
_LOCAL_LOCK = threading.Lock()
_LOCAL_SLOTS: dict[str, int] = {}


@contextlib.asynccontextmanager
async def ai_user_slot(user_id, limit: int = 2):
    """Membatasi permintaan AI serentak per pengguna (Redis dengan fallback memori lokal)."""
    key = f"ai_slot:{user_id}"
    client = None
    using_redis = False

    if settings.REDIS_URL:
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=0.3, socket_timeout=0.3)
            count = await client.incr(key)
            if count == 1:
                await client.expire(key, 60)
            if count > limit:
                await client.decr(key)
                raise HTTPException(status_code=429, detail=_BUSY_DETAIL)
            using_redis = True
        except HTTPException:
            if client is not None:
                with contextlib.suppress(Exception):
                    await client.aclose()
            raise
        except Exception as err:  # noqa: BLE001
            logger.debug("Redis ai_user_slot tidak tersedia, gunakan slot lokal: %s", err)
            if client is not None:
                with contextlib.suppress(Exception):
                    await client.aclose()
            client = None

    if not using_redis:
        with _LOCAL_LOCK:
            cur = _LOCAL_SLOTS.get(key, 0) + 1
            if cur > limit:
                raise HTTPException(status_code=429, detail=_BUSY_DETAIL)
            _LOCAL_SLOTS[key] = cur

    try:
        yield
    finally:
        if using_redis and client is not None:
            try:
                rem = await client.decr(key)
                if rem <= 0:
                    await client.delete(key)
            except Exception as err:  # noqa: BLE001
                logger.debug("Gagal melepas slot Redis ai_user_slot: %s", err)
            finally:
                with contextlib.suppress(Exception):
                    await client.aclose()
        else:
            with _LOCAL_LOCK:
                cur = _LOCAL_SLOTS.get(key, 0) - 1
                if cur <= 0:
                    _LOCAL_SLOTS.pop(key, None)
                else:
                    _LOCAL_SLOTS[key] = cur
