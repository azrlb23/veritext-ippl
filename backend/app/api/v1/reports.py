from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.audit import AuditReport, AuditTask
from app.models.document import Document
from app.models.user import User
from app.schemas.audit import AuditReportResponse, AuditVerificationResponse
from app.schemas.common import APIResponse

router = APIRouter(tags=["Reports & Verification"])


@router.get("/reports/{report_id}", response_model=APIResponse[AuditReportResponse])
async def get_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AuditReport).where(AuditReport.id == report_id)
    report = (await db.execute(stmt)).scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit report not found")

    return APIResponse(
        message="Audit report retrieved",
        data=AuditReportResponse.model_validate(report),
    )


@router.get("/reports/{report_id}/export-pdf")
async def export_pdf(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AuditReport).where(AuditReport.id == report_id)
    report = (await db.execute(stmt)).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit report not found")

    # Generate a lightweight mockup PDF header/stream
    pdf_content = (
        b"%PDF-1.4\n1 0 obj\n<< /Title (VeriText AI Plagiarism Certificate) >>\nendobj\n"
        b"trailer\n<< /Root 1 0 R >>\n%%EOF"
    )

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="VeriText_Certificate_{report.verification_uuid}.pdf"'},
    )


@router.get("/verify/{verification_uuid}", response_model=APIResponse[AuditVerificationResponse])
async def verify_certificate_public(
    verification_uuid: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(AuditReport, AuditTask, Document, User)
        .join(AuditTask, AuditReport.audit_task_id == AuditTask.id)
        .join(Document, AuditTask.document_id == Document.id)
        .join(User, AuditTask.user_id == User.id)
        .where(AuditReport.verification_uuid == verification_uuid)
    )
    result = (await db.execute(stmt)).first()

    if not result:
        return APIResponse(
            success=False,
            message="Sertifikat tidak ditemukan atau tidak valid",
            data=AuditVerificationResponse(
                is_valid=False,
                verification_uuid=str(verification_uuid),
                message="Dokumen ini tidak terdaftar atau telah dihapus.",
            ),
        )

    report, task, doc, user = result

    # Check if doc was deleted under UU PDP
    if doc.deleted_at is not None or doc.status == "DELETED":
        return APIResponse(
            success=False,
            message="Dokumen terkait telah dihapus oleh pemilik atas dasar UU PDP No. 27/2022",
            data=AuditVerificationResponse(
                is_valid=False,
                verification_uuid=str(verification_uuid),
                message="Sertifikat kedaluwarsa karena data naskah telah dihapus permanen.",
            ),
        )

    return APIResponse(
        message="Sertifikat Terverifikasi Asli",
        data=AuditVerificationResponse(
            is_valid=True,
            verification_uuid=str(verification_uuid),
            document_title=doc.original_filename,
            user_name=user.full_name,
            institution=user.institution or "Umum",
            audit_date=report.generated_at,
            score_composite=float(report.score_composite) if report.score_composite else 0.0,
            tier_scores={
                "lexical": float(report.score_lexical) if report.score_lexical else 0.0,
                "semantic": float(report.score_semantic) if report.score_semantic else 0.0,
                "stylometric": float(report.score_stylometric) if report.score_stylometric else 0.0,
            },
            message="Sertifikat Terverifikasi Asli oleh Mesin Hybrid VeriText AI",
        ),
    )
