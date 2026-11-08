from __future__ import annotations

import contextlib
import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle


def format_dt(dt_val: Any) -> str:
    if isinstance(dt_val, (datetime.datetime, datetime.date)):
        return dt_val.strftime("%d %B %Y, %H:%M WIB")
    if isinstance(dt_val, str) and dt_val:
        with contextlib.suppress(Exception):
            parsed = datetime.datetime.fromisoformat(dt_val)
            return parsed.strftime("%d %B %Y, %H:%M WIB")
        return str(dt_val)
    return "-"


def get_invoice_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    return {
        "styles": styles,
        "brand_style": ParagraphStyle("InvBrand", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#171717")),
        "brand_sub": ParagraphStyle("InvBrandSub", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#737373")),
        "section_title": ParagraphStyle("InvSecTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#171717")),
        "body_style": ParagraphStyle("InvBody", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#404040")),
        "body_bold": ParagraphStyle("InvBodyBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=colors.HexColor("#171717")),
    }


def resolve_invoice_status_styling(safe_status: str, styles: Any) -> tuple[colors.Color, colors.Color, str, ParagraphStyle]:
    if safe_status == "PAID":
        bg, border, text_col, display = colors.HexColor("#ECFDF5"), colors.HexColor("#10B981"), colors.HexColor("#065F46"), "LUNAS / TERBAYAR"
    elif safe_status == "PENDING":
        bg, border, text_col, display = colors.HexColor("#FEF3C7"), colors.HexColor("#F59E0B"), colors.HexColor("#92400E"), "MENUNGGU PEMBAYARAN"
    elif safe_status in ("CANCEL", "EXPIRED"):
        bg, border, text_col, display = colors.HexColor("#F3F4F6"), colors.HexColor("#9CA3AF"), colors.HexColor("#4B5563"), "DIBATALKAN / KEDALUWARSA"
    else:
        bg, border, text_col, display = colors.HexColor("#FEE2E2"), colors.HexColor("#EF4444"), colors.HexColor("#991B1B"), "TRANSAKSI GAGAL"

    badge_style = ParagraphStyle("InvBadge", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, alignment=1, textColor=text_col)
    return bg, border, display, badge_style


def build_items_table(safe_package_name: str, token_amount: int, status_display: str, gross_amount: float, body_style: Any, body_bold: Any) -> Table:
    formatted_gross = f"Rp {gross_amount:,.0f}".replace(",", ".")
    items_data = [
        [Paragraph("<b>No</b>", body_bold), Paragraph("<b>Deskripsi Paket</b>", body_bold), Paragraph("<b>Jumlah Token</b>", body_bold), Paragraph("<b>Status</b>", body_bold), Paragraph("<b>Total Harga</b>", body_bold)],
        [
            Paragraph("1", body_style),
            Paragraph(f"<b>{safe_package_name}</b><br/><font color='#737373'>Kuota token audit naskah VeriText AI</font>", body_style),
            Paragraph(f"<b>{token_amount} Token</b>", body_style),
            Paragraph(f"<b>{status_display}</b>", body_style),
            Paragraph(f"<b>{formatted_gross}</b>", body_bold),
        ],
        ["", "", "", Paragraph("<b>SUBTOTAL:</b>", body_bold), Paragraph(f"<b>{formatted_gross}</b>", body_bold)],
        ["", "", "", Paragraph("PPN (0%):", body_style), Paragraph("Rp 0", body_style)],
        ["", "", "", Paragraph("<b>TOTAL TAGIHAN:</b>", body_bold), Paragraph(f"<font color='#065F46'><b>{formatted_gross}</b></font>", body_bold)],
    ]

    table = Table(items_data, colWidths=[30, 222, 90, 80, 100])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#171717")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, 1), 1, colors.HexColor("#E2E8F0")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.white),
            ("LINEABOVE", (3, 2), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (3, 4), (-1, 4), colors.HexColor("#ECFDF5")),
        ])
    )
    for c in range(5):
        table.setStyle(TableStyle([("TEXTCOLOR", (c, 0), (c, 0), colors.white)]))
    return table
