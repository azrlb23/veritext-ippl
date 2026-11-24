from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.schemas.admin import InvoiceSummary

_PAID_STATUSES = ("PAID", "SETTLEMENT")
_FAILED_STATUSES = ("FAILED", "EXPIRED", "CANCEL", "CHALLENGE")


def _serialize_invoice(inv: Invoice) -> dict[str, Any]:
    return {
        "id": str(getattr(inv, "id", "")),
        "order_id": getattr(inv, "order_id", ""),
        "user_id": str(getattr(inv, "user_id", "")),
        "package_name": getattr(inv, "package_name", ""),
        "token_amount": int(getattr(inv, "token_amount", 0) or 0),
        "gross_amount": int(getattr(inv, "gross_amount", 0) or 0),
        "payment_method": getattr(inv, "payment_method", None),
        "status": getattr(inv, "status", ""),
        "paid_at": inv.paid_at.isoformat() if getattr(inv, "paid_at", None) else None,
        "created_at": inv.created_at.isoformat() if getattr(inv, "created_at", None) else None,
    }


async def list_invoices(
    db: AsyncSession,
    status_filter: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> dict[str, Any]:
    """Return read-only invoice summary metrics and paginated invoice records."""
    upper_status = func.upper(Invoice.status)

    total_revenue = int(
        (
            await db.execute(
                select(func.coalesce(func.sum(Invoice.gross_amount), 0)).where(
                    upper_status.in_(_PAID_STATUSES)
                )
            )
        ).scalar()
        or 0
    )
    paid_count = int(
        (
            await db.execute(
                select(func.count(Invoice.id)).where(upper_status.in_(_PAID_STATUSES))
            )
        ).scalar()
        or 0
    )
    pending_count = int(
        (
            await db.execute(
                select(func.count(Invoice.id)).where(upper_status == "PENDING")
            )
        ).scalar()
        or 0
    )
    failed_count = int(
        (
            await db.execute(
                select(func.count(Invoice.id)).where(upper_status.in_(_FAILED_STATUSES))
            )
        ).scalar()
        or 0
    )
    top_pkg_row = (
        await db.execute(
            select(Invoice.package_name)
            .where(upper_status.in_(_PAID_STATUSES))
            .group_by(Invoice.package_name)
            .order_by(func.count(Invoice.id).desc())
            .limit(1)
        )
    ).first()
    top_package = str(top_pkg_row[0]) if top_pkg_row and top_pkg_row[0] else None

    summary = InvoiceSummary(
        total_revenue=total_revenue,
        paid=paid_count,
        pending=pending_count,
        failed=failed_count,
        top_package=top_package,
    )

    query = select(Invoice)
    if status_filter and status_filter.strip() and status_filter.strip().upper() != "ALL":
        normalized = status_filter.strip().upper()
        if normalized == "PAID":
            query = query.where(upper_status.in_(_PAID_STATUSES))
        elif normalized == "FAILED":
            query = query.where(upper_status.in_(_FAILED_STATUSES))
        else:
            query = query.where(upper_status == normalized)

    total = int((await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0)
    rows = (
        await db.execute(
            query.order_by(Invoice.created_at.desc()).offset((page - 1) * limit).limit(limit)
        )
    ).scalars().all()

    pages = (total + limit - 1) // limit if total > 0 else 1
    return {
        "summary": summary.model_dump(),
        "items": [_serialize_invoice(inv) for inv in rows],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }
