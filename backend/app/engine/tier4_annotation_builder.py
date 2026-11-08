from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.engine.preprocessor import SentenceSpan
from app.engine.tier1_lexical import SentenceLexicalMatch
from app.engine.tier2_semantic import SentenceSemanticMatch
from app.engine.tier3_stylometric import StylometricSentenceAnomaly
from app.engine.web_scanner import WebMatchResult


@dataclass
class HeatmapAnnotationData:
    start: int
    end: int
    tier: str  # T1, T2, T3
    color: str  # RED, ORANGE, YELLOW
    similarity: float
    source_title: str
    text_snippet: str
    source_chunk_id: str | None = None
    source_url: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "tier": self.tier,
            "color": self.color,
            "similarity": round(self.similarity, 2),
            "source_title": self.source_title,
            "text_snippet": self.text_snippet,
            "source_chunk_id": self.source_chunk_id,
            "source_url": self.source_url,
            "reason": self.reason,
        }


def build_heatmap_annotations(
    sentences: list[SentenceSpan],
    web_matches: list[WebMatchResult],
    tier1_matched_indices: dict[int, SentenceLexicalMatch],
    tier2_matched_indices: dict[int, SentenceSemanticMatch],
    tier3_anomalies_by_index: dict[int, StylometricSentenceAnomaly],
    audit_depth: str,
    score_t3: float,
) -> list[dict[str, Any]]:
    """Builds prioritized heatmap annotations across all tiers (T1, T2, T3)."""
    web_by_idx = {m.sentence_index: m for m in web_matches}
    annotations: list[dict[str, Any]] = []

    for s in sentences:
        if s.index in web_by_idx and web_by_idx[s.index].tier == "T1":
            wm = web_by_idx[s.index]
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T1", color="RED",
                similarity=wm.similarity, source_title=wm.source_title or "Sumber Web Publik",
                text_snippet=wm.matched_snippet or s.text, source_url=wm.source_url,
                reason="Kecocokan web publik terverifikasi",
            ).to_dict())
        elif s.index in tier1_matched_indices:
            t1 = tier1_matched_indices[s.index]
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T1", color="RED",
                similarity=t1.similarity,
                source_title=t1.matched_source_title or "Korpus Pembanding Leksikal",
                text_snippet=s.text, source_chunk_id=t1.matched_corpus_doc_id,
                reason="Kecocokan leksikal langsung dengan bank korpus",
            ).to_dict())
        elif s.index in web_by_idx and web_by_idx[s.index].tier == "T2":
            wm = web_by_idx[s.index]
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T2", color="ORANGE",
                similarity=wm.similarity, source_title=wm.source_title or "Sumber Web Publik",
                text_snippet=wm.matched_snippet or s.text, source_url=wm.source_url,
                reason="Parafrasa konten web publik terverifikasi",
            ).to_dict())
        elif s.index in tier2_matched_indices:
            t2 = tier2_matched_indices[s.index]
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T2", color="ORANGE",
                similarity=t2.similarity,
                source_title=t2.matched_source_title or "Korpus Pembanding Semantik",
                text_snippet=s.text, source_chunk_id=t2.matched_chunk_id,
                reason="Parafrasa semantik terdeteksi dari bank korpus",
            ).to_dict())
        elif audit_depth == "FULL" and s.index in tier3_anomalies_by_index and (
            score_t3 >= 20.0 or tier3_anomalies_by_index[s.index].anomaly_score >= 0.50
        ):
            t3 = tier3_anomalies_by_index[s.index]
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T3", color="YELLOW",
                similarity=t3.anomaly_score, source_title="Evaluator AI · Gemini Flash",
                text_snippet=s.text, reason=t3.reason,
            ).to_dict())

    return annotations
