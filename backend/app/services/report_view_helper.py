from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, Response, status
from fastapi.params import Depends as DependsParam
from sqlalchemy import select

from app.core.config import settings
from app.models.audit import AuditReport, AuditTask
from app.models.document import Document
from app.models.user import User
from app.schemas.audit import AuditVerificationResponse
from app.schemas.common import APIResponse
from app.services.pdf_certificate_service import clean_pdf_filename, generate_pdf_certificate


def check_report_authorization(report: AuditReport, current_user: User) -> None:
    eff = current_user
    if isinstance(eff, DependsParam) or hasattr(eff, "dependency"):
        if report.audit_task and report.audit_task.user:
            eff = report.audit_task.user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    is_admin = (getattr(eff, "role", None) or "").upper() == "ADMIN"
    t_owner = report.audit_task.user_id if (report.audit_task and report.audit_task.user_id) else (
        report.audit_task.user.id if (report.audit_task and report.audit_task.user) else None
    )
    if not is_admin and (t_owner is None or str(t_owner) != str(eff.id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have permission to access this report")


def build_report_pdf_response(report: AuditReport) -> Response:
    doc_title = report.document_title or "Naskah"
    pdf_bytes = generate_pdf_certificate(
        report_id=str(report.id),
        verification_uuid=str(report.verification_uuid),
        document_title=doc_title,
        user_name=report.user_name or "Pengguna VeriText",
        generated_at=report.generated_at or datetime.now(timezone.utc),  # noqa: UP017
        score_composite=float(report.score_composite or 0.0),
        score_lexical=float(report.score_lexical or 0.0),
        score_semantic=float(report.score_semantic or 0.0),
        score_stylometric=float(report.score_stylometric or 0.0),
        matched_sources=report.matched_sources or [],
        verify_base_url=settings.FRONTEND_URL.rstrip("/"),
    )
    filename = clean_pdf_filename(doc_title)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}"', "Cache-Control": "no-cache"})


async def lookup_verification_data(verification_uuid: str, db) -> APIResponse[AuditVerificationResponse]:
    try:
        p_uuid = verification_uuid if isinstance(verification_uuid, uuid.UUID) else uuid.UUID(str(verification_uuid).strip())
    except (ValueError, AttributeError):
        return APIResponse(
            success=False,
            message="Sertifikat tidak ditemukan atau tidak valid",
            data=AuditVerificationResponse(is_valid=False, verification_uuid=str(verification_uuid), message="Format kode sertifikat tidak valid. Harap gunakan format UUID v4 yang sah."),
        )

    stmt = (
        select(AuditReport, AuditTask, Document, User)
        .join(AuditTask, AuditReport.audit_task_id == AuditTask.id)
        .join(Document, AuditTask.document_id == Document.id)
        .join(User, AuditTask.user_id == User.id)
        .where(AuditReport.verification_uuid == p_uuid)
    )
    result = (await db.execute(stmt)).first()
    if not result:
        return APIResponse(
            success=False,
            message="Sertifikat tidak ditemukan atau tidak valid",
            data=AuditVerificationResponse(is_valid=False, verification_uuid=str(verification_uuid), message="Dokumen ini tidak terdaftar atau telah dihapus."),
        )

    report, _task, doc, user = result
    if doc.deleted_at is not None or doc.status == "DELETED":
        return APIResponse(
            success=False,
            message="Dokumen terkait telah dihapus oleh pemilik",
            data=AuditVerificationResponse(is_valid=False, verification_uuid=str(verification_uuid), message="Sertifikat kedaluwarsa karena data naskah telah dihapus permanen."),
        )

    return APIResponse(
        message="Sertifikat Terverifikasi Asli",
        data=AuditVerificationResponse(
            is_valid=True,
            verification_uuid=str(verification_uuid),
            document_title=doc.original_filename,
            user_name=user.full_name,
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


def attach_sentence_ids(annotations: list, sentences) -> list:
    """Menambahkan sentence_id ke tiap anotasi berdasarkan rentang karakter agar parafrase dapat menargetkan kalimat."""
    spans = sorted(((x.start_char, x.end_char, str(x.id)) for x in sentences), key=lambda t: t[0])
    result = []
    for anno in annotations:
        item = dict(anno) if isinstance(anno, dict) else anno
        if isinstance(item, dict) and not item.get("sentence_id"):
            start = int(item.get("start", 0))
            hit = next((sid for lo, hi, sid in spans if lo <= start < max(hi, lo + 1)), None)
            if hit:
                item["sentence_id"] = hit
        result.append(item)
    return result
