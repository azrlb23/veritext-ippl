from __future__ import annotations

import html
import io
import re
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from app.core.config import settings
from app.services.pdf_certificate_draw import (
    build_certificate_header_table,
    build_certificate_meta_table,
    build_certificate_qr_table,
)
from app.services.pdf_certificate_template import (
    build_matched_sources_table,
    build_scores_table,
    get_certificate_styles,
)
from app.services.pdf_invoice_service import clean_invoice_filename, generate_invoice_pdf


def clean_pdf_filename(document_title: str) -> str:
    name = re.sub(r"\.(pdf|docx?|txt)$", "", document_title, flags=re.IGNORECASE)
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return f"Sertifikat_VeriText_{name or 'Naskah'}.pdf"


def generate_pdf_certificate(
    report_id: str, verification_uuid: str, document_title: str,
    user_name: str, generated_at: Any,
    score_composite: float, score_lexical: float, score_semantic: float, score_stylometric: float,
    matched_sources: list[dict[str, Any]] | None = None, verify_base_url: str | None = None,
    **kwargs: Any,
) -> bytes:
    base_url = (verify_base_url or settings.FRONTEND_URL).rstrip("/")
    safe_doc_title = html.escape(str(document_title or "Naskah"))
    safe_user_name = html.escape(str(user_name or "Pengguna VeriText"))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    s = get_certificate_styles()
    styles = s["styles"]

    date_str = generated_at.strftime("%d %B %Y, %H:%M WIB") if hasattr(generated_at, "strftime") else str(generated_at)

    story = [
        *build_certificate_header_table(verification_uuid, s["brand_style"], s["brand_sub"], s["badge_style"], styles),
        Paragraph("SERTIFIKAT HASIL AUDIT ORISINALITAS", s["title_style"]),
        Paragraph("Dokumen resmi bukti pengujian orisinalitas naskah berbasis arsitektur 4-Tier Hybrid Lexical & Semantic AI Engine.", s["body_style"]),
        Spacer(1, 8),
        build_certificate_meta_table(safe_doc_title, report_id, safe_user_name, date_str, s["body_style"], s["body_bold"]),
        Spacer(1, 10),
        build_scores_table(score_composite, score_lexical, score_semantic, score_stylometric, s),
        Spacer(1, 10),
        Paragraph("<b>RUJUKAN KORPUS DOKUMEN YANG COCOK</b>", s["sec_title"]),
        Spacer(1, 3),
        build_matched_sources_table(matched_sources, s["body_style"], s["body_bold"]),
        Spacer(1, 10),
        build_certificate_qr_table(f"{base_url}/verify/{verification_uuid}", verification_uuid, s["body_style"], s["body_bold"], styles),
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=5),
        Paragraph(
            "Sertifikat ini diterbitkan secara otomatis oleh sistem VeriText AI dan memperhatikan perlindungan data pribadi pengguna. "
            "Seluruh data naskah diuji secara terenkripsi dan dapat diverifikasi validitasnya melalui portal verifikasi publik. Hak Cipta VeriText AI.",
            ParagraphStyle("Foot", parent=styles["Normal"], fontName="Helvetica", fontSize=7, leading=9.5, textColor=colors.HexColor("#A3A3A3"), alignment=1),
        ),
    ]

    doc.build(story)
    return buffer.getvalue()


generate_certificate_pdf = generate_pdf_certificate


class PDFCertificateService:
    generate_pdf_certificate = staticmethod(generate_pdf_certificate)
    generate_certificate_pdf = staticmethod(generate_pdf_certificate)
    clean_pdf_filename = staticmethod(clean_pdf_filename)


__all__ = [
    "PDFCertificateService",
    "clean_invoice_filename",
    "clean_pdf_filename",
    "generate_certificate_pdf",
    "generate_invoice_pdf",
    "generate_pdf_certificate",
]
