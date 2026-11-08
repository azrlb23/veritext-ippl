from __future__ import annotations

import io
from typing import Any

import qrcode
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Image, Paragraph, Spacer, Table, TableStyle


def build_certificate_header_table(
    verification_uuid: str, brand_style: Any, brand_sub: Any, badge_style: Any, styles: Any
) -> list[Any]:
    left_header = [
        Paragraph("VeriText <font color='#8A3FE0'>AI</font>", brand_style),
        Paragraph("Sistem audit orisinalitas naskah", brand_sub),
        Paragraph("Periksa kata, makna, dan pola tulisan", brand_sub),
    ]
    right_header = [
        Table(
            [[Paragraph("TERVERIFIKASI", badge_style)]],
            colWidths=[160],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3EEFA")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]),
        ),
        Spacer(1, 4),
        Paragraph(
            f"<font color='#5E5A6B'>UUID: {verification_uuid!s}</font>",
            ParagraphStyle("Uid", parent=styles["Normal"], fontName="Helvetica", fontSize=7, leading=9, alignment=1),
        ),
    ]
    header_table = Table([[left_header, right_header]], colWidths=[350, 172])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [
        header_table,
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E4DDF0"), spaceAfter=10),
    ]


def certificate_verdict(score: float) -> tuple[str, str]:
    """Label dan warna status berdasarkan skor kemiripan komposit (sama dengan layar hasil)."""
    if score <= 20:
        return "Aman", "#065f46"
    if score <= 40:
        return "Perlu ditinjau", "#b45309"
    return "Perlu direvisi", "#b91c1c"


def build_certificate_meta_table(
    safe_doc_title: str, report_id: str, safe_user_name: str,
    date_str: str, body_style: Any, body_bold: Any, score_composite: float = 0.0
) -> Table:
    verdict, tone = certificate_verdict(score_composite)
    meta_data = [
        [Paragraph("<b>Judul Naskah:</b>", body_style), Paragraph(f"<b>{safe_doc_title}</b>", body_bold), Paragraph("<b>ID Laporan:</b>", body_style), Paragraph(f"{str(report_id)[:16]}...", body_style)],
        [Paragraph("<b>Penulis:</b>", body_style), Paragraph(safe_user_name, body_style), Paragraph("<b>Tanggal Audit:</b>", body_style), Paragraph(date_str, body_style)],
        [Paragraph("<b>Status Validasi:</b>", body_style), Paragraph(f"<font color='{tone}'><b>{verdict}</b></font>", body_bold), Paragraph("<b>Sistem:</b>", body_style), Paragraph("VeriText AI Engine", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[110, 180, 80, 152])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3EEFA")),
        ("INNERGRID", (0, 0), (-1, -1), 1.5, colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return meta_table


def build_certificate_qr_table(verify_url: str, verification_uuid: str, body_style: Any, body_bold: Any, styles: Any) -> Table:
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#14111C", back_color="white")
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_flowable = Image(qr_buf, width=78, height=78)

    qr_text = [
        Paragraph("<b>VERIFIKASI KEASLIAN DIGITAL DENGAN KODE QR</b>", ParagraphStyle("QrH", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#14111C"))),
        Spacer(1, 2),
        Paragraph("Pindai kode QR atau buka tautan di bawah ini untuk mengonfirmasi keabsahan sertifikat ini langsung dari basis data server:", body_style),
        Spacer(1, 2),
        Paragraph(f"<font color='#6D28D9'><u>{verify_url}</u></font>", body_bold),
        Spacer(1, 2),
        Paragraph(f"<font color='#5E5A6B'>ID Sertifikat (UUID): <b>{verification_uuid}</b></font>", ParagraphStyle("Hsh", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, leading=10)),
    ]

    qr_table = Table([[qr_flowable, qr_text]], colWidths=[90, 432])
    qr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3EEFA")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return qr_table
