import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.audit import AuditReport, AuditTask
from app.models.user import User
from app.schemas.audit import AuditReportResponse, AuditVerificationResponse
from app.schemas.common import APIResponse
from app.services.report_view_helper import (
    build_report_pdf_response,
    check_report_authorization,
    lookup_verification_data,
)

router = APIRouter(tags=["Reports & Verification"])


@router.get("/reports/{report_id}", response_model=APIResponse[AuditReportResponse])
async def get_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(AuditReport)
        .options(
            selectinload(AuditReport.audit_task).selectinload(AuditTask.document),
            selectinload(AuditReport.audit_task).selectinload(AuditTask.user),
            selectinload(AuditReport.audit_task).selectinload(AuditTask.sentences),
        )
        .where((AuditReport.id == report_id) | (AuditReport.audit_task_id == report_id))
    )
    report = (await db.execute(stmt)).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit report not found")

    check_report_authorization(report, current_user)
    return APIResponse(message="Audit report retrieved", data=AuditReportResponse.model_validate(report))


@router.get("/reports/{report_id}/export-pdf")
async def export_pdf(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(AuditReport)
        .options(
            selectinload(AuditReport.audit_task).selectinload(AuditTask.document),
            selectinload(AuditReport.audit_task).selectinload(AuditTask.user),
        )
        .where((AuditReport.id == report_id) | (AuditReport.audit_task_id == report_id))
    )
    report = (await db.execute(stmt)).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit report not found")

    check_report_authorization(report, current_user)
    return build_report_pdf_response(report)


@router.get("/verify/{verification_uuid}", response_model=APIResponse[AuditVerificationResponse])
async def verify_certificate_public(
    verification_uuid: str,
    db: AsyncSession = Depends(get_db),
):
    return await lookup_verification_data(verification_uuid, db)


# Backwards compatibility and public contract aliases
get_audit_report = get_report
download_report_pdf = export_pdf
verify_certificate_qr = verify_certificate_public
