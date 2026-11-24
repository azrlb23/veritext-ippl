from __future__ import annotations

import io
from typing import Any
from xml.sax.saxutils import escape

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.models.audit import AuditReport, AuditSentence
from app.services.report_text_builder import build_structured_report_view


def _is_heading(block: str) -> bool:
    return "\n" not in block and len(block) < 85 and not block.endswith((".", "!", "?", ";", ":"))


def _highlight_hex(anno: dict[str, Any]) -> str:
    tag = str(anno.get("color") or anno.get("match_type") or anno.get("tier") or "").upper()
    if tag == "RESOLVED_GREEN":
        return "#DCFCE7"
    if tag in ("RED", "T1"):
        return "#FEE2E2"
    if tag in ("ORANGE", "T2"):
        return "#FFEDD5"
    return "#FEF9C3"


def _fmt_segment(seg: str) -> str:
    return escape(seg).replace("\n", "<br/>")


def _markup_paragraph(text_slice: str, start_offset: int, annotations: list[dict[str, Any]]) -> str:
    end_offset = start_offset + len(text_slice)
    spans: list[tuple[int, int, str]] = []
    for raw in annotations or []:
        if not isinstance(raw, dict):
            continue
        try:
            a_start = int(raw.get("start", 0))
            a_end = int(raw.get("end", 0))
        except (TypeError, ValueError):
            continue
        lo = max(start_offset, a_start)
        hi = min(end_offset, a_end)
        if lo < hi:
            spans.append((lo, hi, _highlight_hex(raw)))

    spans.sort(key=lambda item: (item[0], item[1]))
    parts: list[str] = []
    cursor = start_offset
    for lo, hi, hex_color in spans:
        lo_clamped = max(lo, cursor)
        if lo_clamped >= hi:
            continue
        if lo_clamped > cursor:
            parts.append(_fmt_segment(text_slice[cursor - start_offset : lo_clamped - start_offset]))
        seg = _fmt_segment(text_slice[lo_clamped - start_offset : hi - start_offset])
        parts.append(f'<font backColor="{hex_color}">{seg}</font>')
        cursor = hi

    if cursor < end_offset:
        parts.append(_fmt_segment(text_slice[cursor - start_offset :]))
    return "".join(parts)


def _draw_page_chrome(title: str):
    clean_title = (title or "Naskah").strip()[:72]

    def _draw(canvas: Any, doc: Any) -> None:
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        page_w, page_h = A4
        canvas.drawString(48, page_h - 30, f"VeriText AI - Pratinjau PDF Teranotasi | {clean_title}")
        canvas.drawRightString(page_w - 48, 26, f"Halaman {doc.page}")
        canvas.restoreState()

    return _draw


def _render_annotated_pdf(document_text: str, annotations: list[dict[str, Any]], title: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=48, leftMargin=48, topMargin=48, bottomMargin=48)
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle("AnnotatedBody", parent=styles["Normal"], leading=16)
    story: list[Any] = []

    pos = 0
    for raw_block in document_text.split("\n\n"):
        block = raw_block.strip()
        if block:
            block_start = pos + raw_block.find(block)
            is_head = _is_heading(block)
            style = styles["Heading2"] if is_head else body_style
            markup = _markup_paragraph(block, block_start, annotations)
            story.extend([Paragraph(markup, style), Spacer(1, 6 if is_head else 8)])
        pos += len(raw_block) + 2

    if not story:
        story.append(Paragraph(_markup_paragraph(document_text, 0, annotations), body_style))

    drawer = _draw_page_chrome(title)
    doc.build(story, onFirstPage=drawer, onLaterPages=drawer)
    return buf.getvalue()


def build_annotated_pdf_response(report: AuditReport, sentences: list[AuditSentence]) -> StreamingResponse:
    raw_annotations = list(getattr(report, "heatmap_annotations", None) or [])
    document_text, aligned_annotations = build_structured_report_view(report, raw_annotations, sentences)
    if not document_text or not document_text.strip():
        raise HTTPException(status_code=400, detail="EMPTY_DOCUMENT")

    title = getattr(report, "document_title", None) or "Naskah"
    pdf_bytes = _render_annotated_pdf(document_text, aligned_annotations, str(title))
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="preview.pdf"', "Cache-Control": "no-cache"},
    )
