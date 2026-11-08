from __future__ import annotations

import logging
import time

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.audit import AuditTask

logger = logging.getLogger(__name__)
ACTIVE_STATUSES = ("QUEUED", "PROCESSING")


async def enforce_rate_limit(user_id, scope: str) -> None:
    """Jendela tetap per menit di Redis. Jika Redis tidak tersedia, pembatas dilewati (fail-open) dan dicatat."""
    limit = settings.UPLOAD_RATE_LIMIT_PER_MINUTE
    key = f"rl:{scope}:{user_id}:{int(time.time() // 60)}"
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=0.3, socket_timeout=0.3)
        try:
            count = await client.incr(key)
            if count == 1:
                await client.expire(key, 90)
        finally:
            await client.aclose()
    except Exception as err:  # noqa: BLE001
        logger.warning("Pembatas laju dilewati karena Redis tidak tersedia: %s", err)
        return
    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Terlalu banyak unggahan. Batas {limit} per menit, coba lagi sebentar lagi.",
            headers={"Retry-After": "60"},
        )


async def enforce_active_audit_limit(db: AsyncSession, user_id) -> None:
    limit = settings.MAX_ACTIVE_AUDITS_PER_USER
    stmt = select(func.count()).select_from(AuditTask).where(AuditTask.user_id == user_id, AuditTask.status.in_(ACTIVE_STATUSES))
    active = (await db.execute(stmt)).scalar() or 0
    if active >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Anda masih memiliki {active} audit yang berjalan (batas {limit}). Tunggu hingga selesai.",
        )
