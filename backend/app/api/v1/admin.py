from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.schemas.admin import (
    AuditLogResponse,
    SystemHealthMetricsResponse,
)
from app.schemas.common import APIResponse, PaginatedData
from app.services.admin_monitoring_service import (
    get_analytics,
    get_system_health_metrics,
    get_transactions,
    list_audit_logs_data,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin Monitoring (Read-Only)"],
    dependencies=[Depends(require_role("ADMIN"))],
)


@router.get("/analytics", response_model=APIResponse[dict])
async def get_analytics_route(db: AsyncSession = Depends(get_db)):
    data = await get_analytics(db)
    return APIResponse(message="Analytics retrieved successfully", data=data)


@router.get("/transactions", response_model=APIResponse[dict])
async def get_transactions_route(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    data = await get_transactions(db, limit=limit)
    return APIResponse(message="Transactions retrieved successfully", data=data)


@router.get("/system-health", response_model=APIResponse[SystemHealthMetricsResponse])
@router.get("/health-metrics", response_model=APIResponse[SystemHealthMetricsResponse])
async def get_health_metrics(db: AsyncSession = Depends(get_db)):
    data = await get_system_health_metrics(db)
    return APIResponse(message="System health metrics retrieved", data=data)


@router.get("/audit-logs", response_model=APIResponse[PaginatedData[AuditLogResponse]])
async def list_audit_logs(
    action_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    data = await list_audit_logs_data(db, action_type=action_type, page=page, limit=limit)
    return APIResponse(message="Audit logs retrieved", data=data)


__all__ = [
    "get_analytics_route",
    "get_health_metrics",
    "get_transactions_route",
    "list_audit_logs",
    "router",
]
