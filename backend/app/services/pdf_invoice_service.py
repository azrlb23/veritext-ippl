import datetime
import html
import io
import re
from typing import Any, Optional

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import settings


def clean_invoice_filename(order_id: str) -> str:
    """Sanitizes order ID to produce a clean, human-readable PDF filename."""
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", str(order_id))
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "INV"
    return f"Invoice_{name}.pdf"


def generate_invoice_pdf(
    invoice_id: str,
    order_id: str,
    user_name: str,
    user_email: str,
    package_name: str,
    token_amount: int,
    gross_amount: float,
    status: str,
    created_at: Any,
    institution: Optional[str] = None,
    payment_method: Optional[str] = None,
    paid_at: Optional[Any] = None,
    midtrans_transaction_id: Optional[str] = None,
    verify_base_url: Optional[str] = None,
) -> bytes:
    """
    Generates an official token purchase invoice PDF with ReportLab.
    Includes VeriText AI header, Order ID, buyer info, token package,
    gross amount in IDR, payment status badge, timestamp, and verification QR code.
    """
    if not verify_base_url:
        verify_base_url = settings.FRONTEND_URL.rstrip("/")
    else:
        verify_base_url = verify_base_url.rstrip("/")

    # HTML escape user-supplied inputs to prevent XML injection
    safe_order_id = html.escape(str(order_id or "ORDER-UNKNOWN"))
    safe_user_name = html.escape(str(user_name or "Pengguna VeriText"))
    safe_user_email = html.escape(str(user_email or "user@veritext.ai"))
    safe_institution = html.escape(str(institution or "Institusi Akademik"))
    safe_package_name = html.escape(str(package_name or "Paket Token Akademik"))
    safe_status = str(status or "PENDING").upper()
    safe_payment_method = html.escape(str(payment_method or "Midtrans Snap Gateway"))
    safe_midtrans_id = html.escape(str(midtrans_transaction_id or "-"))

    # Format dates
    def _format_dt(dt_val: Any) -> str:
        if isinstance(dt_val, (datetime.datetime, datetime.date)):
            return dt_val.strftime("%d %B %Y, %H:%M WIB")
        if isinstance(dt_val, str) and dt_val:
            try:
                parsed = datetime.datetime.fromisoformat(dt_val.replace("Z", "+00:00"))
                return parsed.strftime("%d %B %Y, %H:%M WIB")
            except Exception:
                return str(dt_val)
        return "-"

    created_at_str = _format_dt(created_at)
    paid_at_str = _format_dt(paid_at) if paid_at else "-"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    brand_style = ParagraphStyle(
        "InvBrand",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#171717"),
    )
    brand_sub = ParagraphStyle(
        "InvBrandSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#737373"),
    )
    section_title = ParagraphStyle(
        "InvSecTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#171717"),
    )
    body_style = ParagraphStyle(
        "InvBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#404040"),
    )
    body_bold = ParagraphStyle(
        "InvBodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#171717"),
    )

    # Status badge styling
    if safe_status == "PAID":
        status_bg = colors.HexColor("#ECFDF5")
        status_border = colors.HexColor("#10B981")
        status_text_color = colors.HexColor("#065F46")
        status_display = "LUNAS / TERBAYAR"
    elif safe_status == "PENDING":
        status_bg = colors.HexColor("#FEF3C7")
        status_border = colors.HexColor("#F59E0B")
        status_text_color = colors.HexColor("#92400E")
        status_display = "MENUNGGU PEMBAYARAN"
    elif safe_status in ("CANCEL", "EXPIRED"):
        status_bg = colors.HexColor("#F3F4F6")
        status_border = colors.HexColor("#9CA3AF")
        status_text_color = colors.HexColor("#4B5563")
        status_display = "DIBATALKAN / KEDALUWARSA"
    else:
        status_bg = colors.HexColor("#FEE2E2")
        status_border = colors.HexColor("#EF4444")
        status_text_color = colors.HexColor("#991B1B")
        status_display = "TRANSAKSI GAGAL"

    badge_style = ParagraphStyle(
        "InvBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=status_text_color,
    )

    story = []

    # 1. Header (Brand left, Status and Order right)
    left_header = [
        Paragraph("VERITEXT AI", brand_style),
        Paragraph("SISTEM AUDIT INTEGRITAS &amp; ORISINALITAS AKADEMIK", brand_sub),
        Paragraph("Bukti Pembayaran Resmi Transaksi Token Komputasi", brand_sub),
    ]
    right_header = [
        Table(
            [[Paragraph(status_display, badge_style)]],
            colWidths=[170],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), status_bg),
                ("BOX", (0, 0), (-1, -1), 1, status_border),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]),
        ),
        Spacer(1, 4),
        Paragraph(
            f"<font color='#737373'>Order ID: <b>{safe_order_id}</b></font>",
            ParagraphStyle("InvHeadOrd", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, leading=10, alignment=1),
        ),
    ]

    header_table = Table([[left_header, right_header]], colWidths=[352, 170])
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 4))

    # Divider
    story.append(
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#171717"), spaceAfter=10)
    )

    # 2. Buyer and Invoice Metadata (2 Columns)
    buyer_info = [
        Paragraph("<b>DITAGIHKAN KEPADA:</b>", section_title),
        Spacer(1, 4),
        Paragraph(f"Nama Pembeli: <b>{safe_user_name}</b>", body_style),
        Paragraph(f"Alamat Email: <b>{safe_user_email}</b>", body_style),
        Paragraph(f"Institusi: <b>{safe_institution}</b>", body_style),
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
    meta_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Itemized Bill Table
    story.append(Paragraph("<b>RINCIAN PEMBELIAN PAKET TOKEN</b>", section_title))
    story.append(Spacer(1, 6))

    formatted_gross = f"Rp {gross_amount:,.0f}".replace(",", ".")
    items_data = [
        [
            Paragraph("<b>No</b>", body_bold),
            Paragraph("<b>Deskripsi Paket</b>", body_bold),
            Paragraph("<b>Jumlah Token</b>", body_bold),
            Paragraph("<b>Status</b>", body_bold),
            Paragraph("<b>Total Harga</b>", body_bold),
        ],
        [
            Paragraph("1", body_style),
            Paragraph(f"<b>{safe_package_name}</b><br/><font color='#737373'>Kuota token audit naskah akademik VeriText AI</font>", body_style),
            Paragraph(f"<b>{token_amount} Token</b>", body_style),
            Paragraph(f"<b>{status_display}</b>", body_style),
            Paragraph(f"<b>{formatted_gross}</b>", body_bold),
        ],
        [
            "",
            "",
            "",
            Paragraph("<b>SUBTOTAL:</b>", body_bold),
            Paragraph(f"<b>{formatted_gross}</b>", body_bold),
        ],
        [
            "",
            "",
            "",
            Paragraph("PPN (0%):", body_style),
            Paragraph("Rp 0", body_style),
        ],
        [
            "",
            "",
            "",
            Paragraph("<b>TOTAL TAGIHAN:</b>", body_bold),
            Paragraph(f"<font color='#065F46'><b>{formatted_gross}</b></font>", body_bold),
        ],
    ]

    items_table = Table(items_data, colWidths=[30, 222, 90, 80, 100])
    items_table.setStyle(
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
    # Header cells text color override for readability
    for c in range(5):
        items_table.setStyle(TableStyle([("TEXTCOLOR", (c, 0), (c, 0), colors.white)]))

    story.append(items_table)
    story.append(Spacer(1, 16))

    # 4. QR Code & Digital Verification
    verify_url = f"{verify_base_url}/verify?type=invoice&order_id={safe_order_id}&invoice_id={invoice_id}"
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#171717", back_color="white")
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_flowable = Image(qr_buf, width=72, height=72)

    qr_text = [
        Paragraph(
            "<b>VERIFIKASI KEASLIAN DIGITAL DENGAN KODE QR</b>",
            ParagraphStyle(
                "InvQrH",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#171717"),
            ),
        ),
        Spacer(1, 2),
        Paragraph(
            "Pindai kode QR atau buka tautan di bawah ini untuk mengonfirmasi keabsahan status pembayaran invoice ini secara real-time langsung ke server basis data:",
            body_style,
        ),
        Spacer(1, 2),
        Paragraph(f"<font color='#2563EB'><u>{verify_url}</u></font>", body_bold),
        Spacer(1, 2),
        Paragraph(
            f"<font color='#737373'>Invoice ID: <b>{invoice_id}</b> | Order ID: <b>{safe_order_id}</b></font>",
            ParagraphStyle(
                "InvHsh",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=7.5,
                leading=10,
            ),
        ),
    ]

    qr_table = Table([[qr_flowable, qr_text]], colWidths=[80, 442])
    qr_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(qr_table)
    story.append(Spacer(1, 14))

    # 5. Legal Disclaimer & Footer
    story.append(
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=5)
    )
    footer_text = (
        "Dokumen ini merupakan bukti pembayaran resmi yang sah yang diterbitkan oleh sistem otomatis VeriText AI berlandaskan "
        "UU ITE No. 1/2024 dan UU PDP No. 27/2022 tentang Perlindungan Data Pribadi. Kuota token yang telah dibeli tidak dapat ditukarkan kembali dengan uang tunai "
        "dan hanya berlaku untuk pemrosesan audit karya ilmiah pada ekosistem VeriText AI. Hak Cipta VeriText AI."
    )
    story.append(
        Paragraph(
            footer_text,
            ParagraphStyle(
                "InvFoot",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=7,
                leading=9.5,
                textColor=colors.HexColor("#A3A3A3"),
                alignment=1,
            ),
        )
    )

    doc.build(story)
    return buffer.getvalue()
