import io
import datetime
import re
from typing import Optional, List, Dict, Any
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def clean_pdf_filename(document_title: str) -> str:
    """Sanitizes document title to produce a clean, human-readable PDF filename."""
    name = re.sub(r"\.(pdf|docx?|txt)$", "", document_title, flags=re.IGNORECASE)
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "Naskah_Akademik"
    return f"Sertifikat_VeriText_{name}.pdf"


def generate_pdf_certificate(
    report_id: str,
    verification_uuid: str,
    document_title: str,
    user_name: str,
    institution: str,
    generated_at: Any,
    score_composite: float,
    score_lexical: float,
    score_semantic: float,
    score_stylometric: float,
    matched_sources: Optional[List[Dict[str, Any]]] = None,
    verify_base_url: str = "http://localhost:5173",
) -> bytes:
    """
    Generates an official academic PDF certificate of originality with QR code,
    similarity breakdown, and cryptographic verification UUID.
    """
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
        "Brand",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#171717"),
    )
    brand_sub = ParagraphStyle(
        "BrandSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#737373"),
    )
    badge_style = ParagraphStyle(
        "Badge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#065f46"),
    )
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#171717"),
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#404040"),
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#171717"),
    )
    score_num_comp = ParagraphStyle(
        "ScoreComp",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=30,
        alignment=1,
        textColor=colors.HexColor("#171717"),
    )
    score_num_lex = ParagraphStyle(
        "ScoreLex",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=1,
        textColor=colors.HexColor("#DC2626"),
    )
    score_num_sem = ParagraphStyle(
        "ScoreSem",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=1,
        textColor=colors.HexColor("#EA580C"),
    )
    score_num_sty = ParagraphStyle(
        "ScoreSty",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=1,
        textColor=colors.HexColor("#CA8A04"),
    )
    score_sub = ParagraphStyle(
        "ScoreSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        alignment=1,
        textColor=colors.HexColor("#737373"),
    )

    story = []

    # 1. Header Table
    left_header = [
        Paragraph("VERITEXT AI", brand_style),
        Paragraph("SISTEM AUDIT INTEGRITAS & ORISINALITAS AKADEMIK", brand_sub),
        Paragraph("Lembaga Komputasi Validasi Karya Ilmiah Digital", brand_sub),
    ]
    right_header = [
        Table(
            [[Paragraph("TERVERIFIKASI RESMI", badge_style)]],
            colWidths=[160],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#10B981")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]),
        ),
        Spacer(1, 4),
        Paragraph(
            f"<font color='#737373'>UUID: {str(verification_uuid)}</font>",
            ParagraphStyle(
                "Uid",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=7,
                leading=9,
                alignment=1,
            ),
        ),
    ]

    header_table = Table([[left_header, right_header]], colWidths=[350, 172])
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(
        HRFlowable(
            width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10
        )
    )

    # 2. Certificate Title
    story.append(Paragraph("SERTIFIKAT HASIL AUDIT ORISINALITAS", title_style))
    story.append(
        Paragraph(
            "Dokumen resmi bukti pengujian integritas naskah akademik berbasis arsitektur 4-Tier Hybrid Lexical & Semantic AI Engine.",
            body_style,
        )
    )
    story.append(Spacer(1, 8))

    # 3. Document & Author Metadata Card
    if hasattr(generated_at, "strftime"):
        date_str = generated_at.strftime("%d %B %Y, %H:%M WIB")
    else:
        date_str = str(generated_at)

    meta_data = [
        [
            Paragraph("<b>Judul Naskah:</b>", body_style),
            Paragraph(f"<b>{document_title}</b>", body_bold),
            Paragraph("<b>ID Laporan:</b>", body_style),
            Paragraph(f"{str(report_id)[:16]}...", body_style),
        ],
        [
            Paragraph("<b>Penulis / Mahasiswa:</b>", body_style),
            Paragraph(user_name, body_style),
            Paragraph("<b>Tanggal Audit:</b>", body_style),
            Paragraph(date_str, body_style),
        ],
        [
            Paragraph("<b>Institusi:</b>", body_style),
            Paragraph(institution, body_style),
            Paragraph("<b>Status Validasi:</b>", body_style),
            Paragraph("<font color='#065f46'><b>Lulus Evaluasi</b></font>", body_bold),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[110, 180, 80, 152])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 4. Scores Breakdown Grid (4 Boxes)
    box_comp = [
        Paragraph("SKOR KOMPOSIT", score_sub),
        Spacer(1, 2),
        Paragraph(f"{score_composite:.1f}%", score_num_comp),
        Spacer(1, 2),
        Paragraph("Tingkat Kemiripan Total", score_sub),
    ]
    box_lex = [
        Paragraph("TIER 1 (LEKSIKAL)", score_sub),
        Spacer(1, 2),
        Paragraph(f"{score_lexical:.1f}%", score_num_lex),
        Spacer(1, 2),
        Paragraph("Copy-Paste Kata", score_sub),
    ]
    box_sem = [
        Paragraph("TIER 2 (SEMANTIK)", score_sub),
        Spacer(1, 2),
        Paragraph(f"{score_semantic:.1f}%", score_num_sem),
        Spacer(1, 2),
        Paragraph("Parafrasa Makna", score_sub),
    ]
    box_sty = [
        Paragraph("TIER 3 (STILOMETRI)", score_sub),
        Spacer(1, 2),
        Paragraph(f"{score_stylometric:.1f}%", score_num_sty),
        Spacer(1, 2),
        Paragraph("Pola Sintaksis AI", score_sub),
    ]

    scores_table = Table([[box_comp, box_lex, box_sem, box_sty]], colWidths=[140, 126, 126, 130])
    scores_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F8FAFC")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FEF2F2")),
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#FFF7ED")),
            ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#FEFCE8")),
            ("BOX", (0, 0), (0, 0), 1, colors.HexColor("#E2E8F0")),
            ("BOX", (1, 0), (1, 0), 1, colors.HexColor("#FECACA")),
            ("BOX", (2, 0), (2, 0), 1, colors.HexColor("#FFEDD5")),
            ("BOX", (3, 0), (3, 0), 1, colors.HexColor("#FEF08A")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(scores_table)
    story.append(Spacer(1, 10))

    # 5. Matched Sources Section
    story.append(
        Paragraph(
            "<b>RUJUKAN KORPUS DOKUMEN YANG COCOK</b>",
            ParagraphStyle(
                "SecTitle",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor("#171717"),
            ),
        )
    )
    story.append(Spacer(1, 3))

    if matched_sources and len(matched_sources) > 0:
        table_rows = [
            [
                Paragraph("<b>No</b>", body_bold),
                Paragraph("<b>Judul Dokumen Rujukan</b>", body_bold),
                Paragraph("<b>Tingkat Kemiripan</b>", body_bold),
                Paragraph("<b>Kategori Tier</b>", body_bold),
            ]
        ]
        for idx, s in enumerate(matched_sources[:4], 1):
            src_title = s.get("source_title") or s.get("title") or "Dokumen Korpus Terindeks"
            sim_pct = s.get("similarity", 0)
            sim_str = f"{sim_pct * 100:.1f}%" if sim_pct <= 1.0 else f"{sim_pct:.1f}%"
            tier = s.get("tier", "T1")
            tier_label = (
                "Tier 1 (Leksikal)"
                if tier == "T1"
                else ("Tier 2 (Semantik)" if tier == "T2" else "Tier 3 (AI)")
            )
            table_rows.append([
                Paragraph(str(idx), body_style),
                Paragraph(src_title, body_style),
                Paragraph(sim_str, body_bold),
                Paragraph(tier_label, body_style),
            ])
        src_table = Table(table_rows, colWidths=[28, 304, 95, 95])
        src_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        story.append(src_table)
    else:
        empty_box = Table(
            [[
                Paragraph(
                    "<i>Tidak terdeteksi kecocokan signifikan dengan basis korpus pembanding (Naskah Unik).</i>",
                    body_style,
                )
            ]],
            colWidths=[522],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]),
        )
        story.append(empty_box)

    story.append(Spacer(1, 10))

    # 6. QR Code & Digital Signature Box
    verify_url = f"{verify_base_url}/verify/{verification_uuid}"
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#171717", back_color="white")
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_flowable = Image(qr_buf, width=78, height=78)

    qr_text = [
        Paragraph(
            "<b>VERIFIKASI KEASLIAN DIGITAL DENGAN KODE QR</b>",
            ParagraphStyle(
                "QrH",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#171717"),
            ),
        ),
        Spacer(1, 2),
        Paragraph(
            "Pindai kode QR atau buka tautan di bawah ini untuk mengonfirmasi keabsahan sertifikat ini langsung dari basis data server:",
            body_style,
        ),
        Spacer(1, 2),
        Paragraph(f"<font color='#2563EB'><u>{verify_url}</u></font>", body_bold),
        Spacer(1, 2),
        Paragraph(
            f"<font color='#737373'>Kode Verifikasi SHA-256: <b>{verification_uuid}</b></font>",
            ParagraphStyle(
                "Hsh",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=7.5,
                leading=10,
            ),
        ),
    ]

    qr_table = Table([[qr_flowable, qr_text]], colWidths=[90, 432])
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
    story.append(Spacer(1, 8))

    # 7. Official Legal Disclaimer & Footer
    story.append(
        HRFlowable(
            width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=5
        )
    )
    footer_text = (
        "Sertifikat ini diterbitkan secara otomatis oleh sistem VeriText AI berlandaskan UU PDP No. 27/2022 tentang Perlindungan Data Pribadi. "
        "Seluruh data naskah diuji secara terenkripsi dan dapat diverifikasi validitasnya melalui portal verifikasi publik. Hak Cipta VeriText AI."
    )
    story.append(
        Paragraph(
            footer_text,
            ParagraphStyle(
                "Foot",
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
