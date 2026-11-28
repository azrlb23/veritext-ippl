from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.url_guard import escape_ilike
from app.models.audit import AuditTask
from app.models.user import User
from app.models.wallet import TokenWallet
from app.schemas.admin import AdminUserItem
from app.schemas.common import PaginatedData


def _is_user_locked(lockout_until: Optional[datetime], now: datetime) -> bool:
    if lockout_until is None:
        return False
    aware_dt = (
        lockout_until.replace(tzinfo=timezone.utc)
        if lockout_until.tzinfo is None
        else lockout_until
    )
    return aware_dt > now


async def list_users(
    db: AsyncSession,
    q: Optional[str] = None,
    role: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> PaginatedData[AdminUserItem]:
    """Return read-only paginated user overview without sensitive credentials."""
    audit_counts_sq = (
        select(
            AuditTask.user_id.label("user_id"),
            func.count(AuditTask.id).label("audit_count"),
        )
        .group_by(AuditTask.user_id)
        .subquery()
    )

    filters = []
    if q and q.strip():
        pattern = f"%{escape_ilike(q.strip())}%"
        filters.append(or_(User.email.ilike(pattern, escape="\\"), User.full_name.ilike(pattern, escape="\\")))
    if role and role.strip() and role.strip().upper() != "ALL":
        filters.append(User.role == role.strip().upper())

    count_stmt = select(func.count(User.id))
    if filters:
        count_stmt = count_stmt.where(*filters)
    total = int((await db.execute(count_stmt)).scalar() or 0)

    stmt = (
        select(
            User.id,
            User.full_name,
            User.email,
            User.role,
            User.is_active,
            User.lockout_until,
            User.created_at,
            func.coalesce(TokenWallet.balance, 0).label("balance"),
            func.coalesce(TokenWallet.ai_trial_remaining, 0).label("ai_trial_remaining"),
            func.coalesce(audit_counts_sq.c.audit_count, 0).label("audit_count"),
        )
        .outerjoin(TokenWallet, TokenWallet.user_id == User.id)
        .outerjoin(audit_counts_sq, audit_counts_sq.c.user_id == User.id)
    )
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit)

    rows = (await db.execute(stmt)).all()
    now = datetime.now(timezone.utc)
    items = [
        AdminUserItem(
            id=row.id,
            full_name=row.full_name,
            email=row.email,
            role=row.role,
            is_active=bool(row.is_active),
            balance=int(row.balance or 0),
            ai_trial_remaining=int(row.ai_trial_remaining or 0),
            audit_count=int(row.audit_count or 0),
            is_locked=_is_user_locked(row.lockout_until, now),
            created_at=row.created_at,
        )
        for row in rows
    ]
    pages = (total + limit - 1) // limit if total > 0 else 1
    return PaginatedData(items=items, total=total, page=page, limit=limit, pages=pages)
