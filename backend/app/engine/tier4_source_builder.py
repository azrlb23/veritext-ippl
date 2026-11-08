from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.engine.tier1_lexical import LexicalAnalysisResult
from app.engine.tier2_semantic import SemanticAnalysisResult
from app.engine.web_scanner import WebMatchResult

logger = logging.getLogger(__name__)


@dataclass
class MatchedSourceData:
    corpus_doc_id: str
    title: str
    category: str
    contribution_pct: float
    source_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "corpus_doc_id": self.corpus_doc_id,
            "title": self.title,
            "category": self.category,
            "contribution_pct": round(self.contribution_pct, 1),
            "source_url": self.source_url,
        }


def scan_web_sources(
    web_scanner: Any, sentences: list[Any], on_progress: Any | None
) -> tuple[list[WebMatchResult], bool, str | None]:
    """Scans public web sources using Google Search Grounding with safe fallback handling."""
    from app.core.config import settings

    if not settings.WEB_SCAN_ENABLED:
        return [], False, "Pemindaian web dinonaktifkan di konfigurasi sistem."
    try:
        if on_progress:
            on_progress(45, "Tahap 2 · Penelusuran sumber internet publik (Google Search Grounding)")
        matches = web_scanner.scan(sentences)
        avail = getattr(web_scanner, "last_scan_available", True)
        note = getattr(web_scanner, "last_scan_note", None)
        return matches, avail, note
    except Exception as web_err:  # noqa: BLE001
        logger.warning("Catatan: Web scan fallback: %s", web_err)
        return [], False, "Pemindaian web tidak tersedia (fallback tier lokal aktif)"


def compute_web_union_scores(
    sentences: list[Any],
    t1_indices: set[int],
    t2_indices: set[int],
    web_matches: list[WebMatchResult],
    score_t1: float,
    score_t2: float,
) -> tuple[float, float]:
    """Combines corpus and web matches non-overlappingly into accurate T1 and T2 scores."""
    if not sentences:
        return score_t1, score_t2
    meaningful = max(1, len([s for s in sentences if not s.is_citation]))
    t1_all = t1_indices.union({m.sentence_index for m in web_matches if m.tier == "T1"})
    s1 = round(min(100.0, max(score_t1, (len(t1_all) / meaningful) * 100.0)), 2) if t1_all else score_t1
    t2_all = {i for i in t2_indices if i not in t1_all}.union(
        {m.sentence_index for m in web_matches if m.tier == "T2" and m.sentence_index not in t1_all}
    )
    s2 = round(min(100.0, max(score_t2, (len(t2_all) / meaningful) * 100.0)), 2) if t2_all else score_t2
    return s1, s2


def aggregate_matched_sources(
    t1_result: LexicalAnalysisResult | None,
    t2_result: SemanticAnalysisResult | None,
    score_composite: float,
    web_matches: list[WebMatchResult] | None = None,
    web_scan_available: bool = True,
    web_scan_note: str | None = None,
    audit_depth: str = "FULL",
) -> list[dict[str, Any]]:
    """Aggregates and formats matched corpus sources and web findings with relative contribution percentages."""
    source_weights: dict[str, dict[str, Any]] = {}

    if t1_result:
        for doc_id, data in t1_result.corpus_contributions.items():
            entry = source_weights.setdefault(doc_id, {
                "corpus_doc_id": doc_id, "title": data.get("title", "Dokumen Korpus"),
                "category": data.get("category", "Umum"), "raw_weight": 0.0, "source_url": None,
            })
            entry["raw_weight"] += data.get("match_count", 1) * 1.5

    if t2_result:
        for doc_id, data in t2_result.corpus_contributions.items():
            entry = source_weights.setdefault(doc_id, {
                "corpus_doc_id": doc_id, "title": data.get("title", "Dokumen Korpus"),
                "category": data.get("category", "Umum"), "raw_weight": 0.0, "source_url": None,
            })
            entry["raw_weight"] += data.get("total_sim", 1.0) * 2.0

    if web_matches:
        for wm in web_matches:
            url_key = wm.source_url
            if not url_key:
                continue
            entry = source_weights.setdefault(url_key, {
                "corpus_doc_id": url_key, "title": wm.source_title or "Sumber Web Publik",
                "category": "Sumber Internet Publik", "raw_weight": 0.0, "source_url": url_key,
            })
            weight = 2.5 if wm.tier == "T1" else 1.8
            entry["raw_weight"] += wm.similarity * weight

    matched_list: list[dict[str, Any]] = []
    if source_weights and score_composite > 0.0:
        total_weight = sum(item["raw_weight"] for item in source_weights.values())
        if total_weight <= 0:
            total_weight = 1.0
        for item in source_weights.values():
            ratio = item["raw_weight"] / total_weight
            contrib = round(ratio * score_composite, 1)
            matched_list.append(MatchedSourceData(
                corpus_doc_id=item["corpus_doc_id"], title=item["title"],
                category=item["category"], contribution_pct=contrib,
                source_url=item.get("source_url"),
            ).to_dict())
        matched_list.sort(key=lambda x: x["contribution_pct"], reverse=True)

    return matched_list
