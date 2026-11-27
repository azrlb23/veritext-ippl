from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.engine.citation_verifier import CitationFinding, merge_citation_annotations
from app.engine.preprocessor import SentenceSpan
from app.engine.tier1_lexical import SentenceLexicalMatch
from app.engine.tier2_semantic import SentenceSemanticMatch
from app.engine.tier3_stylometric import StylometricSentenceAnomaly
from app.engine.web_scanner import WebMatchResult


def _clip(text: str | None, limit: int = 400) -> str | None:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return None
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 3].rstrip() + "..."


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
    matched_source_text: str | None = None
    source_category: str | None = None
    secondary_sources: list[dict[str, Any]] | None = None
    ai_flag: bool = False
    ai_reason: str | None = None
    ai_score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
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
        if self.matched_source_text:
            data["matched_source_text"] = self.matched_source_text
        if self.source_category:
            data["source_category"] = self.source_category
        if self.secondary_sources:
            data["secondary_sources"] = self.secondary_sources
        if self.ai_flag:
            data["ai_flag"] = True
            data["ai_reason"] = self.ai_reason
            data["ai_score"] = self.ai_score
        return data


def build_heatmap_annotations(
    sentences: list[SentenceSpan],
    web_matches: list[WebMatchResult],
    tier1_matched_indices: dict[int, SentenceLexicalMatch],
    tier2_matched_indices: dict[int, SentenceSemanticMatch],
    tier3_anomalies_by_index: dict[int, StylometricSentenceAnomaly],
    audit_depth: str,
    score_t3: float,
    citation_findings: list[CitationFinding] | None = None,
) -> list[dict[str, Any]]:
    """Builds prioritized heatmap annotations across all tiers (T1, T2, T3)."""
    web_by_idx = {m.sentence_index: m for m in web_matches}
    annotations: list[dict[str, Any]] = []

    for s in sentences:
        t3_match = tier3_anomalies_by_index.get(s.index) if audit_depth == "FULL" else None
        has_ai = t3_match is not None
        t3_reason = t3_match.reason if t3_match else None
        t3_score = t3_match.anomaly_score if t3_match else None
        if s.index in web_by_idx and web_by_idx[s.index].tier == "T1":
            wm = web_by_idx[s.index]
            sec = []
            if s.index in tier1_matched_indices:
                t1 = tier1_matched_indices[s.index]
                sec.append({"source_title": t1.matched_source_title, "source_category": t1.matched_source_category or "Bank Korpus", "similarity": t1.similarity, "matched_source_text": _clip(t1.matched_source_snippet)})
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T1", color="RED",
                similarity=wm.similarity, source_title=wm.source_title or "Sumber Web Publik",
                text_snippet=s.text, source_url=wm.source_url,
                matched_source_text=_clip(wm.matched_snippet), source_category="Sumber Internet Publik",
                secondary_sources=sec or None,
                reason="Kecocokan web publik terverifikasi", ai_flag=has_ai, ai_reason=t3_reason, ai_score=t3_score,
            ).to_dict())
        elif s.index in tier1_matched_indices:
            t1 = tier1_matched_indices[s.index]
            sec = [{"source_title": x.get("source_title"), "source_category": x.get("source_category"), "similarity": x.get("similarity"), "matched_source_text": _clip(x.get("matched_source_text"))} for x in t1.secondary_sources]
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T1", color="RED",
                similarity=t1.similarity,
                source_title=t1.matched_source_title or "Korpus Pembanding Leksikal",
                text_snippet=s.text, source_chunk_id=t1.matched_corpus_doc_id,
                matched_source_text=_clip(t1.matched_source_snippet), source_category=t1.matched_source_category or "Bank Korpus",
                secondary_sources=sec or None,
                reason="Kecocokan leksikal langsung dengan bank korpus", ai_flag=has_ai, ai_reason=t3_reason, ai_score=t3_score,
            ).to_dict())
        elif s.index in web_by_idx and web_by_idx[s.index].tier == "T2":
            wm = web_by_idx[s.index]
            sec = []
            if s.index in tier2_matched_indices:
                t2 = tier2_matched_indices[s.index]
                sec.append({"source_title": t2.matched_source_title, "source_category": "Bank Korpus", "similarity": t2.similarity, "matched_source_text": _clip(t2.matched_chunk_text)})
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T2", color="ORANGE",
                similarity=wm.similarity, source_title=wm.source_title or "Sumber Web Publik",
                text_snippet=s.text, source_url=wm.source_url,
                matched_source_text=_clip(wm.matched_snippet), source_category="Sumber Internet Publik",
                secondary_sources=sec or None,
                reason="Parafrasa konten web publik terverifikasi", ai_flag=has_ai, ai_reason=t3_reason, ai_score=t3_score,
            ).to_dict())
        elif s.index in tier2_matched_indices:
            t2 = tier2_matched_indices[s.index]
            sec = [{"source_title": x.get("source_title"), "source_category": x.get("source_category"), "similarity": x.get("similarity"), "matched_source_text": _clip(x.get("matched_source_text"))} for x in getattr(t2, "secondary_sources", [])]
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T2", color="ORANGE",
                similarity=t2.similarity,
                source_title=t2.matched_source_title or "Korpus Pembanding Semantik",
                text_snippet=s.text, source_chunk_id=t2.matched_chunk_id,
                matched_source_text=_clip(t2.matched_chunk_text), source_category="Bank Korpus",
                secondary_sources=sec or None,
                reason="Parafrasa semantik terdeteksi dari bank korpus", ai_flag=has_ai, ai_reason=t3_reason, ai_score=t3_score,
            ).to_dict())
        elif t3_match is not None and (score_t3 >= 20.0 or t3_match.anomaly_score >= 0.50):
            annotations.append(HeatmapAnnotationData(
                start=s.start_char, end=s.end_char, tier="T3", color="YELLOW",
                similarity=t3_match.anomaly_score, source_title="Analisis Pola Tulisan AI",
                text_snippet=s.text, reason=t3_match.reason, ai_flag=True,
                ai_reason=t3_match.reason, ai_score=t3_match.anomaly_score,
            ).to_dict())

    if audit_depth == "FULL" and citation_findings:
        return merge_citation_annotations(annotations, citation_findings)
    return annotations
