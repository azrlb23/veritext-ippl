from __future__ import annotations

import html as html_lib
import re
import uuid
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.reference_corpus import BUILTIN_REFERENCE_CORPUS
from app.models.audit import AuditReport
from app.models.corpus import CorpusDocument, DocumentChunk

_TAG_RE = re.compile(r"<[^>]+>")


def _find_builtin_corpus(corpus_doc_id: str | None, title: str | None) -> dict[str, Any] | None:
    target_title = (title or "").strip().lower()
    for doc in BUILTIN_REFERENCE_CORPUS:
        if corpus_doc_id and str(doc.get("id")) == corpus_doc_id:
            return doc
        if target_title and str(doc.get("title", "")).strip().lower() == target_title:
            return doc
    return None


async def _find_db_corpus(db: AsyncSession, corpus_doc_id: str | None, title: str | None) -> tuple[str | None, str | None, str | None]:
    doc = None
    if corpus_doc_id:
        try:
            uid = uuid.UUID(corpus_doc_id)
            doc = (await db.execute(select(CorpusDocument).where(CorpusDocument.id == uid))).scalar_one_or_none()
        except ValueError:
            doc = None
    if doc is None and title:
        doc = (await db.execute(select(CorpusDocument).where(CorpusDocument.title == title).limit(1))).scalar_one_or_none()
    if doc is None:
        return None, None, None
    chunks = (
        await db.execute(select(DocumentChunk.chunk_text).where(DocumentChunk.corpus_doc_id == doc.id).order_by(DocumentChunk.chunk_index.asc()))
    ).scalars().all()
    full_text = "\n\n".join(c for c in chunks if c)
    return doc.title, doc.category, full_text or None


async def _fetch_web_excerpt(source_url: str | None) -> str | None:
    if not source_url or not source_url.startswith(("http://", "https://")):
        return None
    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
            resp = await client.get(source_url, headers={"User-Agent": "VeriTextAI/1.0"})
        if resp.status_code != 200 or "html" not in (resp.headers.get("content-type") or "").lower():
            return None
        paras = re.findall(r"<p[^>]*>(.*?)</p>", resp.text, flags=re.IGNORECASE | re.DOTALL)
        cleaned = [html_lib.unescape(_TAG_RE.sub(" ", p)).strip() for p in paras]
        good = [" ".join(c.split()) for c in cleaned if len(c.split()) >= 8][:8]
        return "\n\n".join(good) if good else None
    except Exception:  # noqa: BLE001
        return None


def _collect_matches(report: AuditReport, title: str | None, source_url: str | None) -> list[dict[str, Any]]:
    t_norm = (title or "").strip().lower()
    out: list[dict[str, Any]] = []
    for a in report.heatmap_annotations or []:
        if not isinstance(a, dict) or a.get("tier") not in ("T1", "T2"):
            continue
        a_title = str(a.get("source_title") or "").strip().lower()
        a_url = a.get("source_url")
        if (t_norm and a_title == t_norm) or (source_url and a_url == source_url):
            out.append({
                "sentence_text": a.get("text_snippet") or "",
                "matched_source_text": a.get("matched_source_text") or "",
                "similarity": float(a.get("similarity") or 0.0),
                "tier": a.get("tier"),
            })
    out.sort(key=lambda x: x["similarity"], reverse=True)
    return out


async def build_source_preview(
    db: AsyncSession, report: AuditReport, title: str | None = None, corpus_doc_id: str | None = None, source_url: str | None = None
) -> dict[str, Any]:
    matches = _collect_matches(report, title, source_url)
    builtin = _find_builtin_corpus(corpus_doc_id, title)
    if builtin:
        return {
            "title": builtin.get("title") or title or "Dokumen Korpus",
            "category": builtin.get("category") or "Bank Korpus",
            "source_type": "corpus",
            "source_url": None,
            "full_text": builtin.get("text") or "",
            "matched_highlights": matches,
        }

    db_title, db_cat, db_text = await _find_db_corpus(db, corpus_doc_id, title)
    if db_text:
        return {
            "title": db_title or title or "Dokumen Korpus",
            "category": db_cat or "Bank Korpus",
            "source_type": "corpus",
            "source_url": None,
            "full_text": db_text,
            "matched_highlights": matches,
        }

    snippets = [m["matched_source_text"] for m in matches if m.get("matched_source_text")]
    unique_snippets = list(dict.fromkeys(snippets))
    web_excerpt = await _fetch_web_excerpt(source_url)
    combined = web_excerpt or ("\n\n".join(unique_snippets) if unique_snippets else "")
    return {
        "title": title or "Sumber Pembanding",
        "category": "Sumber Internet Publik" if source_url else "Bank Korpus",
        "source_type": "web" if source_url else "corpus",
        "source_url": source_url,
        "full_text": combined,
        "matched_highlights": matches,
    }
