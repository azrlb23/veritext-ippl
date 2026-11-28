from __future__ import annotations

import html as html_lib
import re
import uuid
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.url_guard import extract_report_allowed_urls, is_safe_public_url
from app.engine.reference_corpus import BUILTIN_REFERENCE_CORPUS
from app.models.audit import AuditReport
from app.models.corpus import CorpusDocument, DocumentChunk

_TAG_RE = re.compile(r"<[^>]+>")
_NOISE_BLOCK_RE = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", flags=re.IGNORECASE | re.DOTALL)


def _is_readable_prose(text: str) -> bool:
    words = text.split()
    if len(words) < 8 or any(sym in text for sym in ("{", "}", "=>", "function(", "var ", "const ")):
        return False
    alpha_space = sum(1 for ch in text if ch.isalpha() or ch.isspace())
    avg_len = sum(len(w) for w in words) / len(words)
    return (alpha_space / max(1, len(text)) >= 0.78) and (3.0 <= avg_len <= 13.0)


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


async def _fetch_web_excerpt(source_url: str | None, allowed_urls: set[str] | None = None) -> str | None:
    if not source_url or not source_url.startswith(("http://", "https://")):
        return None
    if allowed_urls is not None and source_url not in allowed_urls:
        return None
    if not is_safe_public_url(source_url):
        return None
    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=False) as client:
            resp = await client.get(source_url, headers={"User-Agent": "VeriTextAI/1.0"})
        if resp.status_code != 200 or "html" not in (resp.headers.get("content-type") or "").lower():
            return None
        body = _NOISE_BLOCK_RE.sub(" ", resp.text[:524288])
        paras = re.findall(r"<p[^>]*>(.*?)</p>", body, flags=re.IGNORECASE | re.DOTALL)
        cleaned = [" ".join(html_lib.unescape(_TAG_RE.sub(" ", p)).split()) for p in paras]
        good = [c for c in cleaned if _is_readable_prose(c)][:8]
        return "\n\n".join(good) if good else None
    except Exception:  # noqa: BLE001
        return None


def _collect_matches(report: AuditReport, title: str | None, source_url: str | None) -> list[dict[str, Any]]:
    t_norm, out = (title or "").strip().lower(), []
    for a in report.heatmap_annotations or []:
        if not isinstance(a, dict) or a.get("tier") not in ("T1", "T2"):
            continue
        a_title = str(a.get("source_title") or "").strip().lower()
        if (t_norm and a_title == t_norm) or (source_url and a.get("source_url") == source_url):
            out.append({"sentence_text": a.get("text_snippet") or "", "matched_source_text": a.get("matched_source_text") or "", "similarity": float(a.get("similarity") or 0.0), "tier": a.get("tier")})
        else:
            for sec in a.get("secondary_sources") or []:
                if isinstance(sec, dict) and t_norm and str(sec.get("source_title") or "").strip().lower() == t_norm:
                    out.append({"sentence_text": a.get("text_snippet") or "", "matched_source_text": sec.get("matched_source_text") or "", "similarity": float(sec.get("similarity") or a.get("similarity") or 0.0), "tier": a.get("tier")})
    return sorted(out, key=lambda x: x["similarity"], reverse=True)


def _fill_missing_quotes(matches: list[dict[str, Any]], full_text: str) -> None:
    from app.engine.tier1_filters import content_words

    sents = [s.strip() for s in full_text.split(".") if len(s.strip()) >= 15]
    if not sents:
        return
    for m in matches:
        if m.get("matched_source_text"):
            continue
        ref = set(content_words(str(m.get("sentence_text") or "")))
        if not ref:
            continue
        best = max(sents, key=lambda s: len(ref.intersection(content_words(s))))
        if len(ref.intersection(content_words(best))) >= 2:
            m["matched_source_text"] = (best + ".")[:400]


def _corpus_result(doc_title: str | None, category: str | None, full_text: str, matches: list[dict[str, Any]]) -> dict[str, Any]:
    _fill_missing_quotes(matches, full_text)
    return {
        "title": doc_title or "Dokumen Korpus",
        "category": category or "Bank Korpus",
        "source_type": "corpus",
        "source_url": None,
        "full_text": full_text,
        "matched_highlights": matches,
    }


async def build_source_preview(
    db: AsyncSession, report: AuditReport, title: str | None = None, corpus_doc_id: str | None = None, source_url: str | None = None
) -> dict[str, Any]:
    matches = _collect_matches(report, title, source_url)
    builtin = _find_builtin_corpus(corpus_doc_id, title)
    if builtin:
        return _corpus_result(builtin.get("title") or title, builtin.get("category"), builtin.get("text") or "", matches)
    db_title, db_cat, db_text = await _find_db_corpus(db, corpus_doc_id, title)
    if db_text:
        return _corpus_result(db_title or title, db_cat, db_text, matches)
    unique_snippets = list(dict.fromkeys(m["matched_source_text"] for m in matches if m.get("matched_source_text")))
    web_excerpt = await _fetch_web_excerpt(source_url, extract_report_allowed_urls(report))
    return {
        "title": title or "Sumber Pembanding",
        "category": "Sumber Internet Publik" if source_url else "Bank Korpus",
        "source_type": "web" if source_url else "corpus",
        "source_url": source_url,
        "full_text": web_excerpt or ("\n\n".join(unique_snippets) if unique_snippets else ""),
        "matched_highlights": matches,
    }
