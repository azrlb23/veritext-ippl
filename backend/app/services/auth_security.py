from __future__ import annotations

import logging
import time
from collections import OrderedDict

from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_OTP_ATTEMPTS = 5
OTP_LOCK_TTL_S = 3600
_LOCAL_OTP_FAILS: OrderedDict[str, tuple[int, float]] = OrderedDict()


def _prune_local_otp(now: float) -> None:
    expired = [k for k, (_, exp) in _LOCAL_OTP_FAILS.items() if exp <= now]
    for k in expired:
        _LOCAL_OTP_FAILS.pop(k, None)
    while len(_LOCAL_OTP_FAILS) > 2000:
        _LOCAL_OTP_FAILS.popitem(last=False)


async def check_otp_attempts(email: str) -> None:
    key = f"otp_fail:{email.lower().strip()}"
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=0.3, socket_timeout=0.3)
        try:
            val = await client.get(key)
            if val is not None and int(val) >= MAX_OTP_ATTEMPTS:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Terlalu banyak percobaan OTP gagal. Silakan minta kode OTP baru.",
                )
            return
        finally:
            await client.aclose()
    except HTTPException:
        raise
    except Exception as err:  # noqa: BLE001
        logger.debug("Redis tidak tersedia untuk check_otp_attempts, gunakan fallback memori: %s", err)

    now = time.time()
    _prune_local_otp(now)
    cnt, exp = _LOCAL_OTP_FAILS.get(key, (0, 0.0))
    if exp > now and cnt >= MAX_OTP_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak percobaan OTP gagal. Silakan minta kode OTP baru.",
        )


async def record_otp_failure(email: str) -> int:
    key = f"otp_fail:{email.lower().strip()}"
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=0.3, socket_timeout=0.3)
        try:
            count = int(await client.incr(key))
            if count == 1:
                await client.expire(key, OTP_LOCK_TTL_S)
            return count
        finally:
            await client.aclose()
    except Exception as err:  # noqa: BLE001
        logger.debug("Redis tidak tersedia untuk record_otp_failure, gunakan fallback memori: %s", err)

    now = time.time()
    _prune_local_otp(now)
    cnt, exp = _LOCAL_OTP_FAILS.get(key, (0, 0.0))
    new_cnt = (cnt + 1) if exp > now else 1
    _LOCAL_OTP_FAILS[key] = (new_cnt, now + OTP_LOCK_TTL_S)
    return new_cnt


async def clear_otp_attempts(email: str) -> None:
    key = f"otp_fail:{email.lower().strip()}"
    _LOCAL_OTP_FAILS.pop(key, None)
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=0.3, socket_timeout=0.3)
        try:
            await client.delete(key)
        finally:
            await client.aclose()
    except Exception:  # noqa: BLE001
        pass


async def handle_otp_failure(db, email_clean: str) -> None:
    from datetime import datetime, timezone
    from sqlalchemy import select, update
    from app.models.password_reset import PasswordReset
    from app.models.user import User

    fails = await record_otp_failure(email_clean)
    if fails >= MAX_OTP_ATTEMPTS:
        u = (await db.execute(select(User).where(User.email == email_clean))).scalar_one_or_none()
        if u:
            await db.execute(
                update(PasswordReset)
                .where(PasswordReset.user_id == u.id, PasswordReset.used_at.is_(None))
                .values(used_at=datetime.now(timezone.utc))
            )
            await db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak percobaan OTP gagal. Silakan minta kode OTP baru.",
        )
