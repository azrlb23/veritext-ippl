from __future__ import annotations

import io
from typing import Any

import qrcode
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Image, Paragraph, Spacer, Table, TableStyle

TEXT_MAIN = colors.HexColor("#14111C")
TEXT_LABEL = colors.HexColor("#475569")
ACCENT_TEAL = colors.HexColor("#0F766E")
BORDER_SUBTLE = colors.HexColor("#CBD5E1")
BG_SUBTLE = colors.HexColor("#F8FAFC")


def build_certificate_header_table(
    verification_uuid: str, brand_style: Any, brand_sub: Any, badge_style: Any, styles: Any
) -> list[Any]:
    left_header = [
        Paragraph("VERITEXT <font color='#0F766E'>AI</font>", brand_style),
        Spacer(1, 2),
        Paragraph("SISTEM AUDIT ORISINALITAS &amp; INTEGRITAS NASKAH AKADEMIK", brand_sub),
    ]
    badge_table = Table(
        [[Paragraph("SERTIFIKAT RESMI", badge_style)]],
        colWidths=[168],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 1.0, ACCENT_TEAL),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
    )
    ref_style = ParagraphStyle("RefUid", parent=styles["Normal"], fontName="Helvetica", fontSize=7, leading=9.5, alignment=1, textColor=TEXT_LABEL)
    right_header = [badge_table, Spacer(1, 4), Paragraph(f"No. Ref: {verification_uuid!s}", ref_style)]
    header_table = Table([[left_header, right_header]], colWidths=[346, 176])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [
        header_table,
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=1.5, color=TEXT_MAIN, spaceAfter=2),
        HRFlowable(width="100%", thickness=0.5, color=BORDER_SUBTLE, spaceAfter=10),
    ]


def certificate_verdict(score: float) -> tuple[str, str]:
    """Label dan warna status resmi berdasarkan skor kemiripan komposit."""
    if score <= 20:
        return "Memenuhi Standar Orisinalitas", "#0F766E"
    if score <= 40:
        return "Perlu Tinjauan Lanjutan", "#B45309"
    return "Memerlukan Revisi", "#991B1B"


def build_certificate_meta_table(
    safe_doc_title: str, report_id: str, safe_user_name: str,
    date_str: str, body_style: Any, body_bold: Any, score_composite: float = 0.0
) -> Table:
    verdict, tone = certificate_verdict(score_composite)
    lbl_style = ParagraphStyle("MetaLbl", parent=body_bold, textColor=TEXT_LABEL)
    meta_data = [
        [Paragraph("Judul Naskah", lbl_style), Paragraph(f"<b>{safe_doc_title}</b>", body_bold), Paragraph("ID Laporan", lbl_style), Paragraph(f"{str(report_id)[:16]}...", body_style)],
        [Paragraph("Nama Penulis", lbl_style), Paragraph(safe_user_name, body_style), Paragraph("Tanggal Audit", lbl_style), Paragraph(date_str, body_style)],
        [Paragraph("Status Evaluasi", lbl_style), Paragraph(f"<font color='{tone}'><b>{verdict}</b></font>", body_bold), Paragraph("Sistem Audit", lbl_style), Paragraph("VeriText AI Engine", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[92, 182, 84, 164])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BG_SUBTLE),
        ("BACKGROUND", (2, 0), (2, -1), BG_SUBTLE),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("BACKGROUND", (3, 0), (3, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return meta_table


def build_certificate_qr_table(
    verify_url: str, verification_uuid: str, body_style: Any, body_bold: Any, styles: Any
) -> Table:
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_buf = io.BytesIO()
    qr.make_image(fill_color="#14111C", back_color="white").save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_flowable = Image(qr_buf, width=74, height=74)

    qr_head = ParagraphStyle("QrHead", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=TEXT_MAIN)
    qr_note = ParagraphStyle("QrNote", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11.5, textColor=TEXT_LABEL)
    qr_text = [
        Paragraph("PENGESAHAN DIGITAL &amp; VERIFIKASI KODE QR", qr_head),
        Spacer(1, 2),
        Paragraph("Sertifikat ini diterbitkan secara otomatis oleh sistem VeriText AI dan sah secara digital tanpa tanda tangan basah. Pindai kode QR atau buka tautan berikut untuk memverifikasi keabsahan laporan:", qr_note),
        Spacer(1, 3),
        Paragraph(f"<font color='#0F766E'><u>{verify_url}</u></font>", body_bold),
        Spacer(1, 2),
        Paragraph(f"No. Ref Sertifikat: <b>{verification_uuid}</b>", ParagraphStyle("QrUuid", parent=qr_note, fontSize=7.5, leading=10)),
    ]

    qr_table = Table([[qr_flowable, qr_text]], colWidths=[88, 434])
    qr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_SUBTLE),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return qr_table
