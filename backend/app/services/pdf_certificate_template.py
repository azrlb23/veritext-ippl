from __future__ import annotations

import html
from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

TEXT_MAIN = colors.HexColor("#14111C")
TEXT_SCORE = colors.HexColor("#1E293B")
TEXT_LABEL = colors.HexColor("#475569")
ACCENT_TEAL = colors.HexColor("#0F766E")
BORDER_SUBTLE = colors.HexColor("#CBD5E1")
BG_HEADER = colors.HexColor("#F1F5F9")


def get_certificate_styles() -> dict[str, Any]:
    styles = getSampleStyleSheet()
    base = styles["Normal"]
    return {
        "styles": styles,
        "brand_style": ParagraphStyle("Brand", parent=base, fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=TEXT_MAIN),
        "brand_sub": ParagraphStyle("BrandSub", parent=base, fontName="Helvetica", fontSize=7.5, leading=11, textColor=TEXT_LABEL),
        "badge_style": ParagraphStyle("Badge", parent=base, fontName="Helvetica-Bold", fontSize=8.5, leading=11, alignment=1, textColor=ACCENT_TEAL),
        "title_style": ParagraphStyle("Title", parent=base, fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=TEXT_MAIN),
        "body_style": ParagraphStyle("Body", parent=base, fontName="Helvetica", fontSize=9, leading=13, textColor=TEXT_MAIN),
        "body_bold": ParagraphStyle("BodyBold", parent=base, fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=TEXT_MAIN),
        "score_num_comp": ParagraphStyle("ScoreComp", parent=base, fontName="Helvetica-Bold", fontSize=24, leading=28, alignment=1, textColor=TEXT_MAIN),
        "score_num_lex": ParagraphStyle("ScoreLex", parent=base, fontName="Helvetica-Bold", fontSize=18, leading=22, alignment=1, textColor=TEXT_SCORE),
        "score_num_sem": ParagraphStyle("ScoreSem", parent=base, fontName="Helvetica-Bold", fontSize=18, leading=22, alignment=1, textColor=TEXT_SCORE),
        "score_num_sty": ParagraphStyle("ScoreSty", parent=base, fontName="Helvetica-Bold", fontSize=18, leading=22, alignment=1, textColor=TEXT_SCORE),
        "score_sub": ParagraphStyle("ScoreSub", parent=base, fontName="Helvetica", fontSize=7.5, leading=10, alignment=1, textColor=TEXT_LABEL),
        "sec_title": ParagraphStyle("SecTitle", parent=base, fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=TEXT_MAIN),
    }


def build_scores_table(
    score_comp: float, score_lex: float, score_sem: float, score_sty: float, s: dict[str, Any]
) -> Table:
    sub = s["score_sub"]
    cards = [
        ("SKOR KOMPOSIT TOTAL", score_comp, s["score_num_comp"], "Indeks Kemiripan Gabungan"),
        ("KEMIRIPAN LEKSIKAL", score_lex, s["score_num_lex"], "Kecocokan Teks Langsung"),
        ("KEMIRIPAN SEMANTIK", score_sem, s["score_num_sem"], "Parafrasa &amp; Kesamaan Makna"),
        ("INDIKASI POLA AI", score_sty, s["score_num_sty"], "Evaluasi Gaya Penulisan"),
    ]
    row = [
        [Paragraph(f"<b>{lbl}</b>", sub), Spacer(1, 3), Paragraph(f"{val:.1f}%", num_style), Spacer(1, 3), Paragraph(desc, sub)]
        for lbl, val, num_style, desc in cards
    ]
    table = Table([row], colWidths=[140, 126, 126, 130])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def build_matched_sources_table(
    matched_sources: list[dict[str, Any]] | None, body_style: Any, body_bold: Any
) -> Table:
    cell_reg = body_style or ParagraphStyle("CellReg", fontName="Helvetica", fontSize=9, leading=13, textColor=TEXT_MAIN)
    cell_bld = body_bold or ParagraphStyle("CellBld", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=TEXT_MAIN)

    if matched_sources:
        headers = ["No", "Dokumen / Sumber Rujukan", "Kemiripan", "Kategori"]
        table_rows = [[Paragraph(f"<b>{h}</b>", cell_bld) for h in headers]]
        for idx, src in enumerate(matched_sources[:4], 1):
            raw_title = src.get("source_title") or src.get("title") or "Dokumen Korpus Terindeks"
            src_title = html.escape(str(raw_title))
            sim_pct = float(src.get("contribution_pct", src.get("similarity", 0)) or 0)
            sim_str = f"{sim_pct * 100:.1f}%" if sim_pct <= 1.0 else f"{sim_pct:.1f}%"
            tier = src.get("tier", "T1")
            tier_label = "Leksikal" if tier == "T1" else ("Semantik" if tier == "T2" else "Pola AI")
            table_rows.append([
                Paragraph(str(idx), cell_reg),
                Paragraph(src_title, cell_reg),
                Paragraph(sim_str, cell_bld),
                Paragraph(tier_label, cell_reg),
            ])

        table = Table(table_rows, colWidths=[28, 304, 95, 95])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG_HEADER),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE),
            ("LINEBELOW", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        return table

    return Table(
        [[Paragraph("<i>Tidak terdeteksi kecocokan signifikan dengan basis korpus pembanding (Naskah Orisinal).</i>", cell_reg)]],
        colWidths=[522],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]),
    )


def _short_pdf_text(text: str | None, limit: int = 160) -> str:
    cleaned = " ".join(str(text or "").split())
    if not cleaned:
        return "-"
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 3].rstrip() + "..."


def build_source_quotes_table(heatmap_annotations: list[dict[str, Any]] | None, body_style: Any, body_bold: Any) -> Table | None:
    findings = [a for a in (heatmap_annotations or []) if a.get("tier") in ("T1", "T2") and a.get("color") != "RESOLVED_GREEN"]
    if not findings:
        return None
    findings.sort(key=lambda x: float(x.get("similarity", 0) or 0), reverse=True)
    cell_reg = body_style or ParagraphStyle("QReg", fontName="Helvetica", fontSize=8, leading=11, textColor=TEXT_MAIN)
    cell_bld = body_bold or ParagraphStyle("QBld", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=TEXT_MAIN)
    rows = [[Paragraph(f"<b>{h}</b>", cell_bld) for h in ["No", "Kalimat Naskah", "Kutipan Sumber", "Sumber & Skor"]]]
    for idx, item in enumerate(findings[:5], 1):
        sim = float(item.get("similarity", 0) or 0)
        sim_str = f"{sim * 100:.1f}%" if sim <= 1.0 else f"{sim:.1f}%"
        src_title = html.escape(_short_pdf_text(item.get("source_title") or "Sumber Pembanding", 70))
        quote = item.get("matched_source_text") or "Kutipan teks tidak tersedia dari sumber; kecocokan berbasis judul/snippet indeks."
        rows.append([
            Paragraph(str(idx), cell_reg), Paragraph(html.escape(_short_pdf_text(item.get("text_snippet"))), cell_reg),
            Paragraph(html.escape(_short_pdf_text(quote)), cell_reg), Paragraph(f"<b>{src_title}</b><br/>{sim_str}", cell_reg),
        ])
    table = Table(rows, colWidths=[24, 178, 180, 140])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BG_HEADER), ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE), ("LINEBELOW", (0, 0), (-1, -1), 0.6, BORDER_SUBTLE),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table
