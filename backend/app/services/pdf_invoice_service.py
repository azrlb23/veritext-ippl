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
from app.services.pdf_invoice_draw import build_header_table, build_meta_table, build_qr_table
from app.services.pdf_invoice_template import (
    build_items_table,
    format_dt,
    get_invoice_styles,
    resolve_invoice_status_styling,
)


def clean_invoice_filename(order_id: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", str(order_id))
    name = re.sub(r"_+", "_", name).strip("_")
    return f"Invoice_{name or 'INV'}.pdf"


def generate_invoice_pdf(
    invoice_id: str, order_id: str, user_name: str, user_email: str,
    package_name: str, token_amount: int, gross_amount: float, status: str,
    created_at: Any, payment_method: str | None = None,
    paid_at: Any | None = None, midtrans_transaction_id: str | None = None,
    verify_base_url: str | None = None, **kwargs: Any,
) -> bytes:
    base_url = (verify_base_url or settings.FRONTEND_URL).rstrip("/")
    safe_order_id = html.escape(str(order_id or "ORDER-UNKNOWN"))
    safe_user_name = html.escape(str(user_name or "Pengguna VeriText"))
    safe_user_email = html.escape(str(user_email or "user@veritext.ai"))
    safe_package_name = html.escape(str(package_name or "Paket Token"))
    safe_status = str(status or "PENDING").upper()
    safe_payment_method = html.escape(str(payment_method or "Midtrans Snap Gateway"))
    safe_midtrans_id = html.escape(str(midtrans_transaction_id or "-"))

    created_at_str = format_dt(created_at)
    paid_at_str = format_dt(paid_at) if paid_at else "-"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles_dict = get_invoice_styles()
    styles = styles_dict["styles"]
    status_bg, status_border, status_display, badge_style = resolve_invoice_status_styling(safe_status, styles)

    story = [
        build_header_table(
            safe_order_id, status_display, badge_style, status_bg, status_border,
            styles_dict["brand_style"], styles_dict["brand_sub"], styles,
        ),
        Spacer(1, 4),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#171717"), spaceAfter=10),
        build_meta_table(
            safe_user_name, safe_user_email, safe_order_id,
            created_at_str, paid_at_str, safe_payment_method, safe_midtrans_id,
            styles_dict["section_title"], styles_dict["body_style"],
        ),
        Spacer(1, 14),
        Paragraph("<b>RINCIAN PEMBELIAN PAKET TOKEN</b>", styles_dict["section_title"]),
        Spacer(1, 6),
        build_items_table(
            safe_package_name, token_amount, status_display, gross_amount,
            styles_dict["body_style"], styles_dict["body_bold"],
        ),
        Spacer(1, 16),
        build_qr_table(
            f"{base_url}/verify?type=invoice&order_id={safe_order_id}&invoice_id={invoice_id}",
            invoice_id, safe_order_id, styles_dict["body_style"], styles_dict["body_bold"], styles,
        ),
        Spacer(1, 14),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=5),
        Paragraph(
            "Dokumen ini merupakan bukti pembayaran resmi yang sah yang diterbitkan oleh sistem otomatis VeriText AI dan "
            "memperhatikan perlindungan data pribadi pengguna. Kuota token yang telah dibeli tidak dapat ditukarkan kembali dengan uang tunai "
            "dan hanya berlaku untuk pemrosesan audit naskah pada ekosistem VeriText AI. Hak Cipta VeriText AI.",
            ParagraphStyle("InvFoot", parent=styles["Normal"], fontName="Helvetica", fontSize=7, leading=9.5, textColor=colors.HexColor("#A3A3A3"), alignment=1),
        ),
    ]

    doc.build(story)
    return buffer.getvalue()
