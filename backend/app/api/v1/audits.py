import csv
import io
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.audit import AuditTask
from app.models.document import Document
from app.models.user import User
from app.schemas.audit import AuditStartRequest, AuditTaskStatusResponse
from app.schemas.common import APIResponse, PaginatedData
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audits", tags=["Audits"])


@router.post("", response_model=APIResponse[AuditTaskStatusResponse], status_code=status.HTTP_201_CREATED)
async def start_audit(
    req: AuditStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await AuditService.create_audit_task(db, current_user.id, req)
    return APIResponse(
        message="Audit task created and queued for processing",
        data=AuditTaskStatusResponse.model_validate(task),
    )


@router.get("/{task_id}/status", response_model=APIResponse[AuditTaskStatusResponse])
async def get_audit_status(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await AuditService.get_task_status(db, task_id, current_user.id)
    return APIResponse(
        message="Audit status retrieved",
        data=AuditTaskStatusResponse.model_validate(task),
    )


@router.post("/{task_id}/cancel", response_model=APIResponse[dict])
async def cancel_audit(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await AuditService.cancel_task(db, task_id, current_user.id)
    return APIResponse(message="Audit task cancelled", data={})


async def _get_audit_tasks_paginated(
    user_id: uuid.UUID,
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
) -> PaginatedData[AuditTaskStatusResponse]:
    from sqlalchemy.orm import selectinload
    query = (
        select(AuditTask)
        .options(selectinload(AuditTask.document), selectinload(AuditTask.report))
        .where(AuditTask.user_id == user_id)
    )
    count_stmt = select(func.count(AuditTask.id)).where(AuditTask.user_id == user_id)
    if search:
        search_filter = Document.original_filename.ilike(f"%{search}%")
        query = query.join(Document, AuditTask.document_id == Document.id).where(search_filter)
        count_stmt = count_stmt.join(Document, AuditTask.document_id == Document.id).where(search_filter)

    total = (await db.execute(count_stmt)).scalar() or 0

    query = query.order_by(AuditTask.created_at.desc()).offset((page - 1) * limit).limit(limit)
    items = (await db.execute(query)).scalars().all()

    pages = (total + limit - 1) // limit if total > 0 else 1

    task_responses = [AuditTaskStatusResponse.model_validate(x) for x in items]

    return PaginatedData(
        items=task_responses,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/tasks", response_model=APIResponse[PaginatedData[AuditTaskStatusResponse]])
async def list_audit_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by document original filename"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await _get_audit_tasks_paginated(current_user.id, db, page=page, limit=limit, search=search)
    return APIResponse(message="Audit tasks retrieved", data=data)


@router.get("/history", response_model=APIResponse[PaginatedData[AuditTaskStatusResponse]])
async def audit_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by document original filename"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await _get_audit_tasks_paginated(current_user.id, db, page=page, limit=limit, search=search)
    return APIResponse(message="Audit history retrieved", data=data)


@router.get("/history/export-csv")
async def export_audit_history_csv(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(AuditTask)
        .where(AuditTask.user_id == current_user.id)
        .order_by(AuditTask.created_at.desc())
    )
    items = (await db.execute(stmt)).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Task ID", "Document ID", "Depth", "Status", "Progress %", "Started At", "Completed At"])

    for item in items:
        writer.writerow([
            str(item.id),
            str(item.document_id),
            item.audit_depth,
            item.status,
            item.progress_pct,
            item.started_at.isoformat() if item.started_at else "",
            item.completed_at.isoformat() if item.completed_at else "",
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="veritext_audit_history.csv"'},
    )
