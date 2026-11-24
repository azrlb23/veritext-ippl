from datetime import datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditTask
from app.models.invoice import Invoice
from app.models.user import User
from app.models.wallet import TokenTransaction
from app.schemas.admin import OverviewExtras, SystemExtras, TrendPoint


async def get_overview_extras(db: AsyncSession, days: int = 14) -> OverviewExtras:
    """Aggregate KPI deltas, role breakdown, and daily audit/revenue trends."""
    safe_days = max(1, days)
    now = datetime.now(timezone.utc)
    start_today = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)
    start_trend_date = now.date() - timedelta(days=safe_days - 1)
    start_trend_dt = datetime.combine(start_trend_date, time.min, tzinfo=timezone.utc)

    new_users_7d = int(
        (await db.execute(select(func.count(User.id)).where(User.created_at >= cutoff_7d))).scalar()
        or 0
    )
    audits_today = int(
        (
            await db.execute(
                select(func.count(AuditTask.id)).where(AuditTask.created_at >= start_today)
            )
        ).scalar()
        or 0
    )
    tokens_spent_30d = int(
        (
            await db.execute(
                select(func.coalesce(func.sum(func.abs(TokenTransaction.amount)), 0)).where(
                    TokenTransaction.transaction_type.like("DEBIT_%"),
                    TokenTransaction.created_at >= cutoff_30d,
                )
            )
        ).scalar()
        or 0
    )

    role_distribution: dict[str, int] = {"FREE": 0, "PREMIUM": 0, "ADMIN": 0}
    role_rows = (
        await db.execute(select(User.role, func.count(User.id)).group_by(User.role))
    ).all()
    for role_val, cnt in role_rows:
        if role_val:
            role_distribution[str(role_val).upper()] = int(cnt or 0)

    audit_day_expr = func.date(AuditTask.created_at)
    audit_rows = (
        await db.execute(
            select(audit_day_expr, func.count(AuditTask.id))
            .where(AuditTask.created_at >= start_trend_dt)
            .group_by(audit_day_expr)
        )
    ).all()
    audits_by_day = {str(row_date)[:10]: int(cnt or 0) for row_date, cnt in audit_rows if row_date}

    inv_ts_expr = func.coalesce(Invoice.paid_at, Invoice.created_at)
    inv_day_expr = func.date(inv_ts_expr)
    rev_rows = (
        await db.execute(
            select(inv_day_expr, func.coalesce(func.sum(Invoice.gross_amount), 0))
            .where(
                func.upper(Invoice.status).in_(["PAID", "SETTLEMENT"]),
                inv_ts_expr >= start_trend_dt,
            )
            .group_by(inv_day_expr)
        )
    ).all()
    rev_by_day = {str(row_date)[:10]: int(amt or 0) for row_date, amt in rev_rows if row_date}

    trends: list[TrendPoint] = []
    for offset in range(safe_days):
        day_str = (start_trend_date + timedelta(days=offset)).isoformat()
        trends.append(
            TrendPoint(
                date=day_str,
                audits=audits_by_day.get(day_str, 0),
                revenue=rev_by_day.get(day_str, 0),
            )
        )

    return OverviewExtras(
        new_users_7d=new_users_7d,
        audits_today=audits_today,
        tokens_spent_30d=tokens_spent_30d,
        role_distribution=role_distribution,
        trends=trends,
    )


async def get_system_extras(db: AsyncSession) -> SystemExtras:
    """Return read-only operational queue and recent failure counters."""
    cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)

    failed_24h = int(
        (
            await db.execute(
                select(func.count(AuditTask.id)).where(
                    AuditTask.status == "FAILED",
                    AuditTask.created_at >= cutoff_24h,
                )
            )
        ).scalar()
        or 0
    )
    queued = int(
        (
            await db.execute(
                select(func.count(AuditTask.id)).where(AuditTask.status == "QUEUED")
            )
        ).scalar()
        or 0
    )
    processing = int(
        (
            await db.execute(
                select(func.count(AuditTask.id)).where(AuditTask.status == "PROCESSING")
            )
        ).scalar()
        or 0
    )

    return SystemExtras(
        failed_audits_24h=failed_24h,
        queued_audits=queued,
        processing_audits=processing,
    )
