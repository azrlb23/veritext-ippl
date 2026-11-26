from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.audit import AuditReport, AuditTask
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.report_view_helper import check_report_authorization
from app.services.source_preview_service import build_source_preview

router = APIRouter(tags=["Reports & Verification"])


class SourcePreviewResponse(BaseModel):
    title: str
    category: str
    source_type: str
    source_url: Optional[str] = None
    full_text: str
    matched_highlights: list[dict[str, Any]]


@router.get("/reports/{report_id}/source-preview", response_model=APIResponse[SourcePreviewResponse])
async def get_report_source_preview(
    report_id: uuid.UUID,
    title: Optional[str] = Query(default=None),
    corpus_doc_id: Optional[str] = Query(default=None),
    source_url: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    stmt = (
        select(AuditReport)
        .options(selectinload(AuditReport.audit_task).selectinload(AuditTask.user))
        .where((AuditReport.id == report_id) | (AuditReport.audit_task_id == report_id))
    )
    report = (await db.execute(stmt)).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit report not found")

    check_report_authorization(report, current_user)
    data = await build_source_preview(db, report, title=title, corpus_doc_id=corpus_doc_id, source_url=source_url)
    return APIResponse(message="Pratinjau isi sumber pembanding berhasil dimuat", data=SourcePreviewResponse(**data))
