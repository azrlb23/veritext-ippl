from __future__ import annotations

import html
from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def get_certificate_styles() -> dict[str, Any]:
    styles = getSampleStyleSheet()
    return {
        "styles": styles,
        "brand_style": ParagraphStyle("Brand", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#171717")),
        "brand_sub": ParagraphStyle("BrandSub", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#737373")),
        "badge_style": ParagraphStyle("Badge", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, alignment=1, textColor=colors.HexColor("#065f46")),
        "title_style": ParagraphStyle("Title", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=colors.HexColor("#171717")),
        "body_style": ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#404040")),
        "body_bold": ParagraphStyle("BodyBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=colors.HexColor("#171717")),
        "score_num_comp": ParagraphStyle("ScoreComp", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=26, leading=30, alignment=1, textColor=colors.HexColor("#171717")),
        "score_num_lex": ParagraphStyle("ScoreLex", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=20, leading=24, alignment=1, textColor=colors.HexColor("#DC2626")),
        "score_num_sem": ParagraphStyle("ScoreSem", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=20, leading=24, alignment=1, textColor=colors.HexColor("#EA580C")),
        "score_num_sty": ParagraphStyle("ScoreSty", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=20, leading=24, alignment=1, textColor=colors.HexColor("#CA8A04")),
        "score_sub": ParagraphStyle("ScoreSub", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, leading=10, alignment=1, textColor=colors.HexColor("#737373")),
        "sec_title": ParagraphStyle("SecTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=colors.HexColor("#171717")),
    }


def build_scores_table(score_comp: float, score_lex: float, score_sem: float, score_sty: float, s: dict[str, Any]) -> Table:
    box_comp = [Paragraph("SKOR KOMPOSIT", s["score_sub"]), Spacer(1, 2), Paragraph(f"{score_comp:.1f}%", s["score_num_comp"]), Spacer(1, 2), Paragraph("Tingkat Kemiripan Total", s["score_sub"])]
    box_lex = [Paragraph("TIER 1 (LEKSIKAL)", s["score_sub"]), Spacer(1, 2), Paragraph(f"{score_lex:.1f}%", s["score_num_lex"]), Spacer(1, 2), Paragraph("Copy-Paste Kata", s["score_sub"])]
    box_sem = [Paragraph("TIER 2 (SEMANTIK)", s["score_sub"]), Spacer(1, 2), Paragraph(f"{score_sem:.1f}%", s["score_num_sem"]), Spacer(1, 2), Paragraph("Parafrasa Makna", s["score_sub"])]
    box_sty = [Paragraph("TIER 3 (STILOMETRI)", s["score_sub"]), Spacer(1, 2), Paragraph(f"{score_sty:.1f}%", s["score_num_sty"]), Spacer(1, 2), Paragraph("Pola Sintaksis AI", s["score_sub"])]

    table = Table([[box_comp, box_lex, box_sem, box_sty]], colWidths=[140, 126, 126, 130])
    table.setStyle(TableStyle([
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
    ]))
    return table


def build_matched_sources_table(matched_sources: list[dict[str, Any]] | None, body_style: Any, body_bold: Any) -> Table:
    if matched_sources and len(matched_sources) > 0:
        table_rows = [[Paragraph("<b>No</b>", body_bold), Paragraph("<b>Judul Dokumen Rujukan</b>", body_bold), Paragraph("<b>Tingkat Kemiripan</b>", body_bold), Paragraph("<b>Kategori Tier</b>", body_bold)]]
        for idx, src in enumerate(matched_sources[:4], 1):
            raw_title = src.get("source_title") or src.get("title") or "Dokumen Korpus Terindeks"
            src_title = html.escape(str(raw_title))
            sim_pct = src.get("similarity", 0)
            sim_str = f"{sim_pct * 100:.1f}%" if sim_pct <= 1.0 else f"{sim_pct:.1f}%"
            tier = src.get("tier", "T1")
            tier_label = "Tier 1 (Leksikal)" if tier == "T1" else ("Tier 2 (Semantik)" if tier == "T2" else "Tier 3 (AI)")
            table_rows.append([Paragraph(str(idx), body_style), Paragraph(src_title, body_style), Paragraph(sim_str, body_bold), Paragraph(tier_label, body_style)])

        table = Table(table_rows, colWidths=[28, 304, 95, 95])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        return table

    empty_box = Table(
        [[Paragraph("<i>Tidak terdeteksi kecocokan signifikan dengan basis korpus pembanding (Naskah Unik).</i>", body_style)]],
        colWidths=[522],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]),
    )
    return empty_box
