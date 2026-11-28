from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.schemas.admin import AdminUserItem, OverviewExtras, SystemExtras
from app.schemas.common import APIResponse, PaginatedData
from app.services.admin_invoices_service import list_invoices
from app.services.admin_trends_service import get_overview_extras, get_system_extras
from app.services.admin_users_service import list_users

router = APIRouter(
    prefix="/admin",
    tags=["Admin Monitoring Extra (Read-Only)"],
    dependencies=[Depends(require_role("ADMIN"))],
)


@router.get("/users", response_model=APIResponse[PaginatedData[AdminUserItem]])
async def get_admin_users(
    q: Optional[str] = Query(None, max_length=100),
    role: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    data = await list_users(db, q=q, role=role, page=page, limit=limit)
    return APIResponse(message="Users retrieved successfully", data=data)


@router.get("/overview", response_model=APIResponse[OverviewExtras])
async def get_admin_overview(
    days: int = Query(14, ge=7, le=30),
    db: AsyncSession = Depends(get_db),
):
    data = await get_overview_extras(db, days=days)
    return APIResponse(message="Overview extras retrieved successfully", data=data)


@router.get("/invoices", response_model=APIResponse[dict])
async def get_admin_invoices(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    data = await list_invoices(db, status_filter=status, page=page, limit=limit)
    return APIResponse(message="Invoices retrieved successfully", data=data)


@router.get("/system-extras", response_model=APIResponse[SystemExtras])
async def get_admin_system_extras(db: AsyncSession = Depends(get_db)):
    data = await get_system_extras(db)
    return APIResponse(message="System extras retrieved successfully", data=data)


__all__ = [
    "get_admin_invoices",
    "get_admin_overview",
    "get_admin_system_extras",
    "get_admin_users",
    "router",
]
