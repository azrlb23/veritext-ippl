from __future__ import annotations

import logging
import re
from urllib.parse import quote

import httpx

from app.engine.bibliography_parser import BibliographyEntry

logger = logging.getLogger(__name__)
_WORD_RE = re.compile(r"[a-z0-9]{3,}")
_HEADERS = {"User-Agent": "VeriTextAI/1.0 (mailto:veritext-audit@example.com)"}


def title_overlap(query: str, candidate_title: str) -> float:
    q_toks = set(_WORD_RE.findall((query or "").lower()))
    c_toks = set(_WORD_RE.findall((candidate_title or "").lower()))
    if not q_toks or not c_toks:
        return 0.0
    inter = len(q_toks & c_toks)
    return (2.0 * inter) / (len(q_toks) + len(c_toks))


def _check_doi_title(doi: str, title_query: str, title: str, source_name: str) -> tuple[str, str, str | None, str | None]:
    if title and len(title_query.split()) >= 3 and title_overlap(title_query, title) < 0.30:
        return (
            "MISMATCHED_DOI",
            f"DOI {doi} ditemukan di {source_name} tetapi judul tidak cocok dengan metadata asli ('{title[:70]}')",
            f"https://doi.org/{doi}",
            title,
        )
    return "VERIFIED", f"DOI terverifikasi di {source_name}", f"https://doi.org/{doi}", title or None


def verify_doi_entry(doi: str, title_query: str, timeout_s: float) -> tuple[str, str, str | None, str | None]:
    encoded = quote(doi, safe="/")
    cr_status, oa_status = None, None
    try:
        with httpx.Client(timeout=timeout_s, headers=_HEADERS, follow_redirects=True) as client:
            cr = client.get(f"https://api.crossref.org/works/{encoded}")
            cr_status = cr.status_code
            if cr_status == 200:
                title = (cr.json().get("message", {}).get("title") or [""])[0].strip()
                return _check_doi_title(doi, title_query, title, "Crossref")
            oa = client.get(f"https://api.openalex.org/works/https://doi.org/{encoded}")
            oa_status = oa.status_code
            if oa_status == 200:
                title = (oa.json().get("title") or "").strip()
                return _check_doi_title(doi, title_query, title, "OpenAlex")
    except Exception as err:  # noqa: BLE001
        logger.debug("DOI verification network error for %s: %s", doi, err)
        return "UNKNOWN", "Verifikasi DOI melewati batas waktu jaringan", None, None

    if cr_status == 404 and oa_status == 404:
        return "UNVERIFIED", f"DOI {doi} tidak ditemukan di Crossref maupun OpenAlex (indikasi sitasi fiktif)", None, None
    return "UNKNOWN", "Verifikasi DOI tidak mendapat respons valid dari API", None, None


def _extract_year_cr(item: dict) -> str | None:
    parts = (item.get("published-print") or item.get("published-online") or item.get("issued") or {}).get("date-parts")
    return str(parts[0][0]) if parts and parts[0] else None


def verify_search_entry(entry: BibliographyEntry, timeout_s: float) -> tuple[str, str, str | None, str | None]:
    if len(entry.title_query.split()) < 3:
        return "UNKNOWN", "Judul referensi terlalu singkat untuk diverifikasi", None, None
    candidates: list[tuple[str, str, str | None]] = []
    any_ok = False
    try:
        with httpx.Client(timeout=timeout_s, headers=_HEADERS, follow_redirects=True) as client:
            cr = client.get("https://api.crossref.org/works", params={"query.bibliographic": entry.title_query, "rows": 3})
            if cr.status_code == 200:
                any_ok = True
                for item in cr.json().get("message", {}).get("items", []):
                    t = (item.get("title") or [""])[0].strip()
                    url = item.get("URL") or (f"https://doi.org/{item['DOI']}" if item.get("DOI") else "")
                    if t:
                        candidates.append((t, url, _extract_year_cr(item)))
            oa = client.get("https://api.openalex.org/works", params={"search": entry.title_query, "per-page": 3, "select": "id,doi,title,publication_year"})
            if oa.status_code == 200:
                any_ok = True
                for w in oa.json().get("results", []):
                    t = (w.get("title") or "").strip()
                    url = w.get("doi") or w.get("id") or ""
                    yr = str(w.get("publication_year")) if w.get("publication_year") else None
                    if t:
                        candidates.append((t, url, yr))
    except Exception as err:  # noqa: BLE001
        logger.debug("Citation search error: %s", err)

    for title, url, yr in candidates:
        threshold = 0.58 if (entry.year and yr and entry.year == yr) else 0.68
        if title_overlap(entry.title_query, title) >= threshold:
            return "VERIFIED", "Referensi terverifikasi di Crossref/OpenAlex", url or None, title
    if any_ok:
        return "UNVERIFIED", "Referensi daftar pustaka tidak ditemukan di Crossref maupun OpenAlex (indikasi sitasi fiktif)", None, None
    return "UNKNOWN", "Verifikasi sitasi melewati batas waktu layanan eksternal", None, None
