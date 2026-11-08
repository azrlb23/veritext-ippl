from __future__ import annotations

import io
from typing import Any

import qrcode
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle


def build_header_table(
    safe_order_id: str, status_display: str, badge_style: Any,
    status_bg: Any, status_border: Any, brand_style: Any, brand_sub: Any, styles: Any,
) -> Table:
    left = [
        Paragraph("VERITEXT AI", brand_style),
        Paragraph("SISTEM AUDIT ORISINALITAS NASKAH", brand_sub),
        Paragraph("Bukti Pembayaran Resmi Transaksi Token Komputasi", brand_sub),
    ]
    right = [
        Table([[Paragraph(status_display, badge_style)]], colWidths=[170], style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), status_bg),
            ("BOX", (0, 0), (-1, -1), 1, status_border),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])),
        Spacer(1, 4),
        Paragraph(f"<font color='#737373'>Order ID: <b>{safe_order_id}</b></font>", ParagraphStyle("InvHeadOrd", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, leading=10, alignment=1)),
    ]
    header_table = Table([[left, right]], colWidths=[352, 170])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return header_table


def build_meta_table(
    safe_user_name: str, safe_user_email: str,
    safe_order_id: str, created_at_str: str, paid_at_str: str,
    safe_payment_method: str, safe_midtrans_id: str, section_title: Any, body_style: Any,
) -> Table:
    buyer_info = [
        Paragraph("<b>DITAGIHKAN KEPADA:</b>", section_title),
        Spacer(1, 4),
        Paragraph(f"Nama Pembeli: <b>{safe_user_name}</b>", body_style),
        Paragraph(f"Alamat Email: <b>{safe_user_email}</b>", body_style),
    ]
    tx_info = [
        Paragraph("<b>INFORMASI TAGIHAN:</b>", section_title),
        Spacer(1, 4),
        Paragraph(f"Nomor Invoice: <b>{safe_order_id}</b>", body_style),
        Paragraph(f"Tanggal Diterbitkan: <b>{created_at_str}</b>", body_style),
        Paragraph(f"Tanggal Pelunasan: <b>{paid_at_str}</b>", body_style),
        Paragraph(f"Metode Pembayaran: <b>{safe_payment_method}</b>", body_style),
        Paragraph(f"Gateway Tx ID: <b>{safe_midtrans_id}</b>", body_style),
    ]
    meta_table = Table([[buyer_info, tx_info]], colWidths=[261, 261])
    meta_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return meta_table


def build_qr_table(verify_url: str, invoice_id: str, safe_order_id: str, body_style: Any, body_bold: Any, styles: Any) -> Table:
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#171717", back_color="white")
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_flowable = Image(qr_buf, width=72, height=72)

    qr_text = [
        Paragraph("<b>VERIFIKASI KEASLIAN DIGITAL DENGAN KODE QR</b>", ParagraphStyle("InvQrH", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#171717"))),
        Spacer(1, 2),
        Paragraph("Pindai kode QR atau buka tautan di bawah ini untuk mengonfirmasi keabsahan status pembayaran invoice ini secara real-time langsung ke server basis data:", body_style),
        Spacer(1, 2),
        Paragraph(f"<font color='#2563EB'><u>{verify_url}</u></font>", body_bold),
        Spacer(1, 2),
        Paragraph(f"<font color='#737373'>Invoice ID: <b>{invoice_id}</b> | Order ID: <b>{safe_order_id}</b></font>", ParagraphStyle("InvHsh", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, leading=10)),
    ]

    qr_table = Table([[qr_flowable, qr_text]], colWidths=[80, 442])
    qr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return qr_table
