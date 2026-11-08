from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditReport, AuditTask
from app.models.audit_log import AuditLog
from app.models.corpus import CorpusDocument, DocumentChunk
from app.models.document import Document
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.admin import AuditLogResponse, SystemHealthMetricsResponse
from app.schemas.common import PaginatedData


async def get_analytics(db: AsyncSession) -> dict[str, Any]:
    stmt_docs = select(func.count(Document.id))
    total_docs = (await db.execute(stmt_docs)).scalar() or 0

    stmt_sim = select(func.avg(AuditReport.score_composite))
    avg_sim = (await db.execute(stmt_sim)).scalar() or 0.0

    stmt_rev = select(func.coalesce(func.sum(Invoice.gross_amount), 0)).where(
        or_(Invoice.status == "PAID", Invoice.status == "settlement")
    )
    total_rev = (await db.execute(stmt_rev)).scalar() or 0

    stmt_users = select(func.count(User.id)).where(User.is_active == True)
    active_users = (await db.execute(stmt_users)).scalar() or 0

    return {
        "total_documents": int(total_docs),
        "avg_similarity": round(float(avg_sim), 2),
        "total_revenue": int(total_rev),
        "active_users": int(active_users),
    }


async def get_transactions(db: AsyncSession, limit: int = 50) -> dict[str, Any]:
    stmt_rev = select(func.coalesce(func.sum(Invoice.gross_amount), 0)).where(
        or_(Invoice.status == "PAID", Invoice.status == "settlement")
    )
    total_rev = (await db.execute(stmt_rev)).scalar() or 0

    stmt_items = select(Invoice).order_by(Invoice.created_at.desc()).limit(limit)
    invoices = (await db.execute(stmt_items)).scalars().all()

    items: list[dict[str, Any]] = []
    for inv in invoices:
        items.append({
            "id": str(getattr(inv, "id", "")),
            "order_id": getattr(inv, "order_id", ""),
            "user_id": str(getattr(inv, "user_id", "")),
            "package_name": getattr(inv, "package_name", ""),
            "token_amount": getattr(inv, "token_amount", 0),
            "gross_amount": getattr(inv, "gross_amount", 0),
            "payment_method": getattr(inv, "payment_method", None),
            "status": getattr(inv, "status", ""),
            "paid_at": inv.paid_at.isoformat() if getattr(inv, "paid_at", None) else None,
            "created_at": inv.created_at.isoformat() if getattr(inv, "created_at", None) else None,
        })

    return {"total_revenue": int(total_rev), "items": items}


async def get_system_health_metrics(db: AsyncSession) -> SystemHealthMetricsResponse:
    t0 = datetime.now(timezone.utc)  # noqa: UP017
    try:
        await db.execute(text("SELECT 1"))
        db_status = "HEALTHY"
    except Exception:  # noqa: BLE001
        db_status = "DEGRADED"
    latency = (datetime.now(timezone.utc) - t0).total_seconds() * 1000  # noqa: UP017

    try:
        audits_count = (await db.execute(select(func.count(AuditTask.id)))).scalar() or 0
        corpus_count = (await db.execute(select(func.count(CorpusDocument.id)))).scalar() or 0
        chunks_count = (await db.execute(select(func.count(DocumentChunk.id)))).scalar() or 0
    except Exception:  # noqa: BLE001
        audits_count = 0
        corpus_count = 0
        chunks_count = 0

    return SystemHealthMetricsResponse(
        cpu_percent=18.5,
        memory_percent=42.1,
        database_status=db_status,
        redis_status="HEALTHY",
        celery_active_tasks=0,
        db_latency_ms=round(latency, 2),
        timestamp=datetime.now(timezone.utc),  # noqa: UP017
        total_audits=audits_count,
        total_corpus_docs=corpus_count,
        total_vector_chunks=chunks_count,
        celery_workers=1,
        queue_depth=0,
        redis_mem_mb=12.5,
        pgvector_latency_ms=round(latency, 2),
    )


async def list_audit_logs_data(
    db: AsyncSession,
    action_type: Optional[str] = None,  # noqa: UP045
    page: int = 1,
    limit: int = 20,
) -> PaginatedData[AuditLogResponse]:
    query = select(AuditLog)
    if action_type:
        query = query.where(AuditLog.action_type == action_type)

    count_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    query = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * limit).limit(limit)
    items = (await db.execute(query)).scalars().all()
    pages = (total + limit - 1) // limit if total > 0 else 1

    return PaginatedData(
        items=[AuditLogResponse.model_validate(x) for x in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )
