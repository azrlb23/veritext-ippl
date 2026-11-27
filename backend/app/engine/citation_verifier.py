from __future__ import annotations

import concurrent.futures
import logging
from dataclasses import dataclass
from typing import Any

from app.engine.bibliography_parser import BibliographyEntry, parse_bibliography_entries
from app.engine.citation_api_clients import verify_doi_entry, verify_search_entry

logger = logging.getLogger(__name__)


@dataclass
class CitationFinding:
    raw_text: str
    start_char: int
    end_char: int
    doi: str | None
    status: str  # VERIFIED | UNVERIFIED | MISMATCHED_DOI | UNKNOWN
    reason: str
    confidence_score: float = 0.0
    matched_url: str | None = None
    matched_title: str | None = None


class CitationVerifier:
    def __init__(self, timeout_s: float = 4.0, overall_timeout_s: float = 12.0, max_entries: int = 20) -> None:
        self.timeout_s = timeout_s
        self.overall_timeout_s = overall_timeout_s
        self.max_entries = max_entries

    def _verify_one(self, entry: BibliographyEntry) -> CitationFinding:
        if entry.doi:
            status, reason, url, title = verify_doi_entry(entry.doi, entry.title_query, self.timeout_s)
        else:
            status, reason, url, title = verify_search_entry(entry, self.timeout_s)
        score = 0.90 if status == "MISMATCHED_DOI" else 0.85 if status == "UNVERIFIED" else 0.0
        return CitationFinding(
            raw_text=entry.raw_text, start_char=entry.start_char, end_char=entry.end_char,
            doi=entry.doi, status=status, reason=reason, confidence_score=score,
            matched_url=url, matched_title=title,
        )

    def verify_entries(self, entries: list[BibliographyEntry]) -> list[CitationFinding]:
        if not entries:
            return []
        findings: list[CitationFinding] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(3, len(entries))) as executor:
            futures = [executor.submit(self._verify_one, e) for e in entries[: self.max_entries]]
            try:
                for fut in concurrent.futures.as_completed(futures, timeout=self.overall_timeout_s):
                    try:
                        findings.append(fut.result())
                    except Exception as err:  # noqa: BLE001
                        logger.debug("Citation worker error: %s", err)
            except concurrent.futures.TimeoutError:
                for fut in futures:
                    if not fut.done():
                        fut.cancel()
        return sorted(findings, key=lambda f: f.start_char)

    def verify_document(self, original_text: str) -> list[CitationFinding]:
        entries = parse_bibliography_entries(original_text, max_entries=self.max_entries)
        return self.verify_entries(entries) if entries else []


def merge_citation_annotations(
    annotations: list[dict[str, Any]], findings: list[CitationFinding]
) -> list[dict[str, Any]]:
    for f in findings:
        if f.status not in ("UNVERIFIED", "MISMATCHED_DOI"):
            continue
        overlaps = [a for a in annotations if int(a["start"]) < f.end_char and int(a["end"]) > f.start_char]
        if overlaps:
            for overlap in overlaps:
                overlap["ai_flag"] = True
                prev = overlap.get("ai_reason")
                overlap["ai_reason"] = f"{prev}; {f.reason}" if prev else f.reason
                overlap["ai_score"] = max(float(overlap.get("ai_score") or 0.0), f.confidence_score)
        else:
            annotations.append({
                "start": f.start_char, "end": f.end_char, "tier": "T3", "color": "YELLOW",
                "similarity": round(f.confidence_score, 2), "source_title": "Verifikasi Sitasi Daftar Pustaka",
                "text_snippet": f.raw_text, "source_chunk_id": None, "source_url": f.matched_url,
                "reason": f.reason, "ai_flag": True, "ai_reason": f.reason, "ai_score": f.confidence_score,
            })
    return sorted(annotations, key=lambda a: int(a["start"]))
