from __future__ import annotations

import uuid
import xml.etree.ElementTree as ET
from urllib.parse import quote

import httpx

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def reconstruct_abstract(inv_idx: dict[str, list[int]] | None) -> str:
    if not inv_idx or not isinstance(inv_idx, dict):
        return ""
    max_pos = max((max(pos) for pos in inv_idx.values() if pos), default=-1)
    if max_pos < 0 or max_pos > 4000:
        return ""
    words = [""] * (max_pos + 1)
    for token, positions in inv_idx.items():
        for pos in positions:
            if 0 <= pos <= max_pos:
                words[pos] = token
    return " ".join(w for w in words if w).strip()


def _clean_text(value: object, limit: int = 0) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit] if limit > 0 else text


def fetch_openalex_sliced(
    client: httpx.Client,
    lang: str,
    year: int | str,
    page: int,
) -> list[dict[str, str]]:
    params = {
        "filter": f"has_abstract:true,language:{lang},publication_year:{year}",
        "per-page": 200,
        "page": page,
        "select": "id,title,publication_year,abstract_inverted_index,primary_topic",
    }
    resp = client.get("https://api.openalex.org/works", params=params)
    resp.raise_for_status()
    payload = resp.json() if resp.content else {}
    items: list[dict[str, str]] = []
    for work in (payload.get("results") if isinstance(payload, dict) else None) or []:
        if not isinstance(work, dict):
            continue
        oa_id = str(work.get("id") or "").rsplit("/", 1)[-1] or uuid.uuid4().hex[:12]
        topic = work.get("primary_topic")
        topic_name = topic.get("display_name") if isinstance(topic, dict) else None
        items.append({
            "source_key": f"oa_{lang}_{oa_id}",
            "title": _clean_text(work.get("title"), 490),
            "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
            "category": _clean_text(topic_name or f"OpenAlex ({lang.upper()})", 250),
            "year": _clean_text(work.get("publication_year") or year, 20),
        })
    return items


def fetch_doaj_batch(
    client: httpx.Client,
    query: str,
    page: int,
    page_size: int = 100,
) -> list[dict[str, str]]:
    url = f"https://doaj.org/api/search/articles/{quote(query, safe='')}"
    resp = client.get(url, params={"page": page, "pageSize": page_size})
    resp.raise_for_status()
    payload = resp.json() if resp.content else {}
    items: list[dict[str, str]] = []
    for art in (payload.get("results") if isinstance(payload, dict) else None) or []:
        if not isinstance(art, dict):
            continue
        bib = art.get("bibjson")
        if not isinstance(bib, dict):
            continue
        subjects = bib.get("subject")
        first_subj = subjects[0] if isinstance(subjects, list) and subjects else None
        term = first_subj.get("term") if isinstance(first_subj, dict) else None
        art_id = str(art.get("id") or "").strip() or uuid.uuid4().hex[:12]
        items.append({
            "source_key": f"doaj_{art_id}",
            "title": _clean_text(bib.get("title"), 490),
            "abstract": _clean_text(bib.get("abstract")),
            "category": _clean_text(term or "DOAJ Journal", 250),
            "year": _clean_text(bib.get("year"), 20),
        })
    return items


def fetch_arxiv_batch(
    client: httpx.Client,
    category: str,
    start: int,
    max_results: int = 200,
) -> list[dict[str, str]]:
    params = {
        "search_query": f"cat:{category}",
        "start": start,
        "max_results": max_results,
    }
    resp = client.get("https://export.arxiv.org/api/query", params=params)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items: list[dict[str, str]] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        raw_id = (entry.findtext("atom:id", default="", namespaces=ATOM_NS) or "").strip()
        short_id = raw_id.rsplit("/", 1)[-1] or uuid.uuid4().hex[:12]
        published = (entry.findtext("atom:published", default="", namespaces=ATOM_NS) or "").strip()
        items.append({
            "source_key": f"arxiv_{short_id}",
            "title": _clean_text(entry.findtext("atom:title", default="", namespaces=ATOM_NS), 490),
            "abstract": _clean_text(entry.findtext("atom:summary", default="", namespaces=ATOM_NS)),
            "category": _clean_text(category, 250),
            "year": published[:4] if len(published) >= 4 else "",
        })
    return items
