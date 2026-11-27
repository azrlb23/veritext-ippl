from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import docx
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.core.config import settings
from app.models.audit import AuditReport, AuditSentence
from app.services.report_text_builder import build_structured_report_view

_INTEGRITY_ERR = "EXPORT_INTEGRITY_FAILED: Hasil ekspor gagal melewati pemeriksaan integritas dokumen."
_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _norm_ws(text: str) -> str: return " ".join((text or "").split())


def _is_heading(block: str) -> bool: return "\n" not in block and len(block) < 85 and not block.endswith((".", "!", "?", ";", ":"))


def _safe_filename(title: str | None, ext: str) -> str:
    raw = re.sub(r"\.(pdf|docx?|txt)$", "", str(title or "Naskah"), flags=re.IGNORECASE)
    clean = re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9_\-]", "_", raw)).strip("_") or "Naskah"
    return f"revisi_{clean}.{ext}"


def _all_docx_paras(doc_obj: Any) -> list[Any]:
    return list(doc_obj.paragraphs) + [p for t in doc_obj.tables for r in t.rows for c in r.cells for p in c.paragraphs]


def verify_export_integrity(exported_bytes: bytes, fmt: str, modified_sentences: list[str], structured_text: str) -> None:
    fmt_clean = (fmt or "").lower().strip()
    if not exported_bytes or not structured_text or not structured_text.strip():
        raise HTTPException(status_code=500, detail=_INTEGRITY_ERR)
    if fmt_clean == "docx":
        try:
            doc_obj = docx.Document(io.BytesIO(exported_bytes))
        except Exception:
            raise HTTPException(status_code=500, detail=_INTEGRITY_ERR) from None
        extracted, expected = _norm_ws("\n".join(p.text for p in _all_docx_paras(doc_obj) if p.text)), _norm_ws(structured_text)
        if not extracted or len(extracted) < max(1, int(len(expected) * 0.5)) or any(_norm_ws(s) and _norm_ws(s) not in extracted for s in modified_sentences):
            raise HTTPException(status_code=500, detail=_INTEGRITY_ERR)
        return
    if fmt_clean == "pdf" and exported_bytes.startswith(b"%PDF") and re.search(rb"/Type\s*/Page(?![a-zA-Z])", exported_bytes):
        return
    raise HTTPException(status_code=500, detail=_INTEGRITY_ERR)


def _resolve_docx_path(report: AuditReport) -> Path | None:
    task = getattr(report, "audit_task", None)
    doc = getattr(task, "document", None) if task else None
    if not doc:
        return None
    stored = getattr(doc, "stored_filename", None)
    for cand in (getattr(doc, "storage_path", None), (Path(settings.UPLOAD_DIR) / str(stored)) if stored else None):
        if cand and str(cand).lower().endswith(".docx") and Path(str(cand)).is_file():
            return Path(str(cand))
    return None


def _replace_para(para: Any, pairs: list[tuple[str, str]]) -> None:
    for old_t, new_t in pairs:
        if not old_t or old_t not in para.text:
            continue
        if new_t == "":
            target = f" {old_t}" if f" {old_t}" in para.text else (f"{old_t} " if f"{old_t} " in para.text else old_t)
        else:
            target = old_t
        for run in para.runs:
            if target in run.text:
                run.text = run.text.replace(target, new_t, 1)
                break
        else:
            para.text = para.text.replace(target, new_t, 1)


def _render_docx_bytes(
    report: AuditReport, sentences: list[AuditSentence], structured_text: str, modified: list[str]
) -> bytes:
    docx_path = _resolve_docx_path(report)
    if docx_path is not None:
        pairs = [
            (old_t, new_t)
            for s in sentences if getattr(s, "is_modified", False)
            for new_t in [(getattr(s, "current_text", None) or "").strip()]
            for cand in (getattr(s, "original_text", None), getattr(s, "sentence_text", None))
            for old_t in [(cand or "").strip()] if old_t and old_t != new_t
        ]
        try:
            doc_obj = docx.Document(str(docx_path))
            for para in _all_docx_paras(doc_obj):
                _replace_para(para, pairs)
            extracted = _norm_ws("\n".join(p.text for p in _all_docx_paras(doc_obj) if p.text))
            if all(_norm_ws(m) in extracted for m in modified if _norm_ws(m)):
                buf = io.BytesIO()
                doc_obj.save(buf)
                return buf.getvalue()
        except Exception:
            pass
    out = docx.Document()
    for block in (b.strip() for b in structured_text.split("\n\n") if b.strip()):
        out.add_heading(block, level=2) if _is_heading(block) else out.add_paragraph(block)
    buf = io.BytesIO()
    out.save(buf)
    return buf.getvalue()


def _render_pdf_bytes(structured_text: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=48, leftMargin=48, topMargin=48, bottomMargin=48)
    styles = getSampleStyleSheet()
    story: list[Any] = []
    for block in (b.strip() for b in structured_text.split("\n\n") if b.strip()):
        safe = escape(block).replace("\n", "<br/>")
        style = styles["Heading2"] if _is_heading(block) else styles["Normal"]
        story.extend([Paragraph(safe, style), Spacer(1, 6 if _is_heading(block) else 8)])
    if not story:
        story.append(Paragraph(escape(structured_text), styles["Normal"]))
    doc.build(story)
    return buf.getvalue()


def build_revised_document_response(report: AuditReport, sentences: list[AuditSentence], fmt: str) -> StreamingResponse:
    fmt_clean = (fmt or "").lower().strip()
    if fmt_clean not in ("docx", "pdf"):
        raise HTTPException(status_code=400, detail="INVALID_FORMAT: Format ekspor harus 'docx' atau 'pdf'.")
    structured_text, _ = build_structured_report_view(report, [], sentences)
    if not structured_text:
        structured_text = getattr(report, "document_text", None) or " ".join(
            (getattr(s, "current_text", None) or getattr(s, "sentence_text", None) or "").strip() for s in sentences
        ).strip()
    if not structured_text or not structured_text.strip():
        raise HTTPException(status_code=400, detail="EMPTY_DOCUMENT: Naskah tidak memiliki konten untuk diekspor.")
    modified = [(getattr(s, "current_text", None) or "").strip() for s in sentences if getattr(s, "is_modified", False) and (getattr(s, "current_text", None) or "").strip()]
    raw_bytes = _render_docx_bytes(report, sentences, structured_text, modified) if fmt_clean == "docx" else _render_pdf_bytes(structured_text)
    verify_export_integrity(raw_bytes, fmt_clean, modified, structured_text)
    filename = _safe_filename(getattr(report, "document_title", None), fmt_clean)
    media_type = _DOCX_MIME if fmt_clean == "docx" else "application/pdf"
    return StreamingResponse(io.BytesIO(raw_bytes), media_type=media_type, headers={"Content-Disposition": f'attachment; filename="{filename}"', "Cache-Control": "no-cache"})
