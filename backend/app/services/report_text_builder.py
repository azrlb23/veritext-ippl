from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from app.core.config import settings
from app.models.audit import AuditReport
from app.services.safe_extract import extract_text_limited

_HEADING_PREFIXES = ("bagian ", "tahap ", "bab ", "langkah ", "sub-cpmk")


def _read_original_document_text(report: AuditReport) -> str | None:
    task = getattr(report, "audit_task", None)
    doc = getattr(task, "document", None) if task else None
    stored = getattr(doc, "stored_filename", None) if doc else None
    if not doc or not stored:
        return None
    file_path = Path(settings.UPLOAD_DIR) / stored
    if not file_path.is_file():
        return None
    try:
        extracted = extract_text_limited(str(file_path), getattr(doc, "mime_type", None))
    except Exception:
        return None
    return extracted if extracted and extracted.strip() else None


def _reconstruct_from_sentences(ordered: list[Any]) -> str | None:
    parts: list[str] = []
    prev: Any = None
    for s in ordered:
        text = (getattr(s, "sentence_text", None) or getattr(s, "current_text", None) or "").strip()
        if not text:
            continue
        if prev is not None:
            gap = int(getattr(s, "start_char", 0) or 0) - int(getattr(prev, "end_char", 0) or 0)
            if gap > 2:
                parts.append("\n\n")
            elif gap == 2 or text.lower().startswith(_HEADING_PREFIXES):
                parts.append("\n")
            else:
                parts.append(" ")
        parts.append(text)
        prev = s
    joined = "".join(parts).strip()
    return joined or None


def _ws_pattern(text: str) -> str | None:
    words = text.split()
    return r"\s+".join(re.escape(w) for w in words) if words else None


def _apply_modified_sentences(document_text: str, ordered: list[Any]) -> str:
    updated = document_text
    for s in ordered:
        orig_text = getattr(s, "sentence_text", None) or ""
        new_text = getattr(s, "current_text", None)
        is_mod = bool(getattr(s, "is_modified", False))
        if (is_mod or new_text != orig_text) and new_text and orig_text and new_text != orig_text:
            if orig_text in updated:
                updated = updated.replace(orig_text, new_text, 1)
            else:
                pattern = _ws_pattern(orig_text)
                m = re.search(pattern, updated) if pattern else None
                if m:
                    updated = updated[:m.start()] + new_text + updated[m.end():]
    return updated


def _find_snippet(document_text: str, snippet: str, orig_start: int) -> tuple[int, int]:
    search_from = max(0, orig_start - 40)
    idx = document_text.find(snippet, search_from)
    if idx == -1 and search_from > 0:
        idx = document_text.find(snippet)
    if idx != -1:
        return idx, len(snippet)
    pattern = _ws_pattern(snippet)
    if not pattern:
        return -1, 0
    compiled = re.compile(pattern)
    m = compiled.search(document_text, search_from)
    if m is None and search_from > 0:
        m = compiled.search(document_text)
    return (m.start(), m.end() - m.start()) if m else (-1, 0)


def _align_annotations(document_text: str, annotations: list[Any], ordered: list[Any]) -> list[Any]:
    sent_by_id = {str(getattr(s, "id")): s for s in ordered if getattr(s, "id", None) is not None}
    aligned: list[Any] = []
    for raw in annotations or []:
        if not isinstance(raw, dict):
            aligned.append(raw)
            continue
        item = dict(raw)
        orig_start = int(item.get("start") or 0)
        sent = sent_by_id.get(str(item["sentence_id"])) if item.get("sentence_id") else None
        sent_text = (getattr(sent, "current_text", None) or getattr(sent, "sentence_text", None)) if sent is not None else None
        snippet = item.get("text_snippet") or sent_text
        if snippet:
            idx, matched_len = _find_snippet(document_text, snippet, orig_start)
            if idx == -1 and sent_text and sent_text != snippet:
                idx, matched_len = _find_snippet(document_text, sent_text, orig_start)
            if idx != -1:
                s, e = idx, idx + matched_len
                while s > 0 and document_text[s - 1].isalnum():
                    s -= 1
                while e < len(document_text) and document_text[e].isalnum():
                    e += 1
                item["start"] = s
                item["end"] = e
        aligned.append(item)
    return aligned


def build_structured_report_view(
    report: AuditReport,
    annotations: list,
    sentences: list,
) -> tuple[str | None, list]:
    """Menyusun teks laporan terstruktur serta menyelaraskan koordinat sorotan."""
    ordered = sorted(sentences or [], key=lambda s: int(getattr(s, "sentence_index", 0) or 0))
    document_text = _read_original_document_text(report)
    if not document_text:
        document_text = _reconstruct_from_sentences(ordered)
    if not document_text:
        return None, list(annotations or [])
    document_text = _apply_modified_sentences(document_text, ordered)
    aligned = _align_annotations(document_text, annotations, ordered)
    return document_text, aligned
