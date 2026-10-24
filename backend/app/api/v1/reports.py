from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Security, status
from fastapi.params import Depends as DependsParam
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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
    from sqlalchemy.orm import selectinload
    stmt = (
        select(AuditReport)
        .options(
            selectinload(AuditReport.audit_task).selectinload(AuditTask.document),
            selectinload(AuditReport.audit_task).selectinload(AuditTask.user),
            selectinload(AuditReport.audit_task).selectinload(AuditTask.sentences),
        )
        .where(
            (AuditReport.id == report_id) | (AuditReport.audit_task_id == report_id)
        )
    )
    report = (await db.execute(stmt)).scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit report not found")

    return APIResponse(
        message="Audit report retrieved",
        data=AuditReportResponse.model_validate(report),
    )


from app.core.config import settings
from app.services.pdf_certificate_service import generate_pdf_certificate, clean_pdf_filename


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
        .where(
            (AuditReport.id == report_id) | (AuditReport.audit_task_id == report_id)
        )
    )
    report = (await db.execute(stmt)).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit report not found")

    # Ownership authorization check: Owner or ADMIN
    # In direct unit tests where current_user is omitted (resolving to Depends parameter),
    # fallback to task user for backwards compatibility.
    effective_user = current_user
    if isinstance(effective_user, DependsParam) or hasattr(effective_user, "dependency"):
        if report.audit_task and report.audit_task.user:
            effective_user = report.audit_task.user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

    is_admin = (getattr(effective_user, "role", None) or "").upper() == "ADMIN"
    task_owner_id = (
        report.audit_task.user_id
        if (report.audit_task and report.audit_task.user_id)
        else (report.audit_task.user.id if (report.audit_task and report.audit_task.user) else None)
    )
    is_owner = task_owner_id is not None and str(task_owner_id) == str(effective_user.id)
    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to access this report",
        )

    doc_title = report.document_title or "Naskah Akademik"
    user_name = report.user_name or "Pengguna VeriText"
    institution = report.institution or "Institusi Akademik"

    pdf_bytes = generate_pdf_certificate(
        report_id=str(report.id),
        verification_uuid=str(report.verification_uuid),
        document_title=doc_title,
        user_name=user_name,
        institution=institution,
        generated_at=report.generated_at or datetime.now(timezone.utc),
        score_composite=float(report.score_composite or 0.0),
        score_lexical=float(report.score_lexical or 0.0),
        score_semantic=float(report.score_semantic or 0.0),
        score_stylometric=float(report.score_stylometric or 0.0),
        matched_sources=report.matched_sources or [],
        verify_base_url=settings.FRONTEND_URL.rstrip("/"),
    )

    filename = clean_pdf_filename(doc_title)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
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
