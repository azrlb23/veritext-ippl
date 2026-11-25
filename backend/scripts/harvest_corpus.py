"""Multi-source academic corpus harvester (OpenAlex, Crossref, Semantic Scholar, OAI-PMH)."""
from __future__ import annotations

import argparse
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SyncSessionLocal
from app.engine.academic_search_providers import reconstruct_openalex_abstract
from app.engine.reference_corpus import ReferenceCorpusBank
from app.engine.reference_corpus_data import sync_corpus_records
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticEngine

_TAG_RE = re.compile(r"<[^>]+>")
_OAI_NS = {"oai": "http://www.openarchives.org/OAI/2.0/", "dc": "http://purl.org/dc/elements/1.1/"}


def _make_record(title: str, text: str, category: str, year: str) -> dict:
    clean_t = " ".join(title.split())[:240]
    clean_body = _TAG_RE.sub(" ", " ".join(text.split()))
    return {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"veritext-corpus:{clean_t.lower()}")),
        "title": clean_t,
        "category": category,
        "academic_year": year,
        "text": f"{clean_t}. {clean_body}",
    }


def fetch_openalex(limit: int = 120) -> list[dict]:
    records, cursor = [], "*"
    with httpx.Client(timeout=15.0) as client:
        while len(records) < limit and cursor:
            r = client.get(
                "https://api.openalex.org/works",
                params={"filter": "language:id,has_abstract:true", "per-page": min(100, limit - len(records)), "cursor": cursor},
            )
            if r.status_code != 200:
                break
            data = r.json()
            for w in data.get("results", []):
                abs_text = reconstruct_openalex_abstract(w.get("abstract_inverted_index"))
                title = w.get("title") or ""
                if title and len(abs_text) >= 80:
                    records.append(_make_record(title, abs_text, "OpenAlex ID", str(w.get("publication_year") or "2025")))
            cursor = data.get("meta", {}).get("next_cursor")
    return records[:limit]


def fetch_crossref(queries: list[str], per_query: int = 25) -> list[dict]:
    records: list[dict] = []
    with httpx.Client(timeout=15.0) as client:
        for q in queries:
            r = client.get("https://api.crossref.org/works", params={"query": q, "filter": "has-abstract:true", "rows": per_query, "mailto": "veritext-audit@example.com"})
            if r.status_code != 200:
                continue
            for item in r.json().get("message", {}).get("items", []):
                t = (item.get("title") or [""])[0]
                ab = item.get("abstract") or ""
                if t and len(ab) >= 80:
                    records.append(_make_record(t, ab, "Crossref", "2025"))
    return records


def fetch_semantic_scholar(queries: list[str], per_query: int = 25) -> list[dict]:
    records: list[dict] = []
    with httpx.Client(timeout=15.0) as client:
        for q in queries:
            r = client.get("https://api.semanticscholar.org/graph/v1/paper/search", params={"query": q, "limit": per_query, "fields": "title,abstract,year"})
            if r.status_code != 200:
                continue
            for p in r.json().get("data", []):
                if p.get("title") and len(p.get("abstract") or "") >= 80:
                    records.append(_make_record(p["title"], p["abstract"], "Semantic Scholar", str(p.get("year") or "2025")))
    return records


def fetch_oaipmh(endpoints: list[str], per_endpoint: int = 25) -> list[dict]:
    records: list[dict] = []
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        for url in endpoints:
            try:
                r = client.get(url, params={"verb": "ListRecords", "metadataPrefix": "oai_dc"})
                if r.status_code != 200:
                    continue
                root = ET.fromstring(r.text)
                for rec in root.findall(".//oai:record", _OAI_NS)[:per_endpoint]:
                    t_el = rec.find(".//dc:title", _OAI_NS)
                    d_el = rec.find(".//dc:description", _OAI_NS)
                    if t_el is not None and d_el is not None and t_el.text and len(d_el.text or "") >= 80:
                        records.append(_make_record(t_el.text, d_el.text, "OJS Indonesia", "2025"))
            except Exception:  # noqa: BLE001
                continue
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--openalex", type=int, default=120)
    args = parser.parse_args()
    queries = ["plagiarisme kecerdasan buatan indonesia", "sistem informasi akademik", "pembelajaran mesin teks"]
    ojs_urls = ["https://journal.unnes.ac.id/journals/jal/oai", "https://ejournal.undip.ac.id/index.php/jtsi/oai"]

    docs = fetch_openalex(args.openalex) + fetch_crossref(queries) + fetch_semantic_scholar(queries) + fetch_oaipmh(ojs_urls)
    unique = list({d["id"]: d for d in docs}.values())
    print(f"Fetched {len(unique)} unique academic documents across 4 sources.")

    db = SyncSessionLocal()
    try:
        builtin_count = ReferenceCorpusBank.get_instance().sync_to_db(db)
        harvested_count = sync_corpus_records(unique, WinnowingLexicalEngine(), SemanticEngine(), db)
        print(f"Synced builtin={builtin_count}, harvested={harvested_count} into PostgreSQL pgvector.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
