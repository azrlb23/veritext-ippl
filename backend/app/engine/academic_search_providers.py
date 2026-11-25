from __future__ import annotations

import concurrent.futures
import logging
import re
from typing import Any

import httpx

from app.engine.preprocessor import SentenceSpan, TextPreprocessor

logger = logging.getLogger(__name__)
_TAG_RE = re.compile(r"<[^>]+>")


def reconstruct_openalex_abstract(inv_idx: dict[str, list[int]] | None) -> str:
    if not inv_idx:
        return ""
    words: dict[int, str] = {}
    for word, positions in inv_idx.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words[i] for i in sorted(words))


def search_openalex(query: str, timeout_s: float = 5.0) -> list[dict[str, str]]:
    url = "https://api.openalex.org/works"
    params = {"search": query, "per-page": 3, "select": "id,doi,title,abstract_inverted_index"}
    with httpx.Client(timeout=timeout_s) as client:
        r = client.get(url, params=params)
    if r.status_code != 200:
        return []
    out: list[dict[str, str]] = []
    for w in r.json().get("results", []):
        title = (w.get("title") or "").strip()
        abstract = reconstruct_openalex_abstract(w.get("abstract_inverted_index"))
        link = w.get("doi") or w.get("id") or ""
        if title and (abstract or title) and link:
            out.append({"source_title": f"[OpenAlex] {title}", "source_url": link, "snippet": abstract or title})
    return out


def search_crossref(query: str, timeout_s: float = 5.0) -> list[dict[str, str]]:
    url = "https://api.crossref.org/works"
    params = {"query.bibliographic": query, "rows": 3, "mailto": "veritext-audit@example.com"}
    with httpx.Client(timeout=timeout_s) as client:
        r = client.get(url, params=params)
    if r.status_code != 200:
        return []
    out: list[dict[str, str]] = []
    for item in r.json().get("message", {}).get("items", []):
        title_list = item.get("title") or []
        title = title_list[0].strip() if title_list else ""
        abstract = _TAG_RE.sub(" ", item.get("abstract") or "").strip()
        link = item.get("URL") or (f"https://doi.org/{item['DOI']}" if item.get("DOI") else "")
        if title and (abstract or title) and link:
            out.append({"source_title": f"[Crossref] {title}", "source_url": link, "snippet": abstract or title})
    return out


def search_semantic_scholar(query: str, timeout_s: float = 5.0) -> list[dict[str, str]]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": 3, "fields": "title,url,abstract"}
    with httpx.Client(timeout=timeout_s) as client:
        r = client.get(url, params=params)
    if r.status_code != 200:
        return []
    out: list[dict[str, str]] = []
    for p in r.json().get("data", []):
        title = (p.get("title") or "").strip()
        abstract = (p.get("abstract") or "").strip()
        link = p.get("url") or ""
        if title and (abstract or title) and link:
            out.append({"source_title": f"[SemanticScholar] {title}", "source_url": link, "snippet": abstract or title})
    return out


def _query_all_academic(span: SentenceSpan, query: str, req_timeout: float) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for fn in (search_openalex, search_crossref, search_semantic_scholar):
        try:
            for item in fn(query, req_timeout):
                hits.append({"sentence_index": span.index, **item})
        except Exception as err:  # noqa: BLE001
            logger.debug("Academic provider error (%s): %s", fn.__name__, err)
    return hits


def call_academic_search_api(timeout_s: int, batch_sentences: list[SentenceSpan]) -> list[dict[str, Any]]:
    """Mencari referensi jurnal paralel ke OpenAlex, Crossref, dan Semantic Scholar."""
    req_timeout = float(max(2, min(timeout_s, 6)))
    future_timeout = float(max(6, min(timeout_s, 14)))
    queries = [
        (s, " ".join([w for w in TextPreprocessor.tokenize_words(s.text) if len(w) > 3][:8]))
        for s in batch_sentences
    ]
    queries = [(s, q) for s, q in queries if q]
    if not queries:
        return []

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(queries))) as executor:
        futures = [executor.submit(_query_all_academic, s, q, req_timeout) for s, q in queries]
        try:
            for fut in concurrent.futures.as_completed(futures, timeout=future_timeout):
                try:
                    results.extend(fut.result())
                except Exception:  # noqa: BLE001
                    pass
        except concurrent.futures.TimeoutError:
            for fut in futures:
                if not fut.done():
                    fut.cancel()
    return results
