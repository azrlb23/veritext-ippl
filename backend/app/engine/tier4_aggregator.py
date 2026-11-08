from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from app.engine.ai_detector import GeminiAIDetector
from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.reference_corpus import ReferenceCorpusBank
from app.engine.tier1_lexical import LexicalAnalysisResult, WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticAnalysisResult, SemanticEngine
from app.engine.tier3_stylometric import StylometricAnalysisResult, StylometricEngine
from app.engine.tier4_annotation_builder import HeatmapAnnotationData, build_heatmap_annotations
from app.engine.tier4_source_builder import (
    MatchedSourceData,
    aggregate_matched_sources,
    compute_web_union_scores,
    scan_web_sources,
)
from app.engine.web_scanner import GeminiWebScanner, WebMatchResult

__all__ = ["HeatmapAnnotationData", "HybridAggregator", "HybridAuditResult", "MatchedSourceData"]


@dataclass
class HybridAuditResult:
    score_lexical: float
    score_semantic: float
    score_stylometric: float
    score_composite: float
    audit_depth: str
    sentences: list[SentenceSpan]
    heatmap_annotations: list[dict[str, Any]]
    matched_sources: list[dict[str, Any]]
    t1_result: LexicalAnalysisResult | None = None
    t2_result: SemanticAnalysisResult | None = None
    t3_result: StylometricAnalysisResult | None = None
    web_matches: list[WebMatchResult] | None = None
    web_scan_available: bool = True
    web_scan_note: str | None = None


class HybridAggregator:
    """Orchestrator for the 4-Tier Hybrid Plagiarism Detection Engine."""

    def __init__(
        self,
        w_lexical: float | None = None,
        w_semantic: float | None = None,
        w_stylometric: float | None = None,
        corpus_bank: ReferenceCorpusBank | None = None,
        ai_detector: GeminiAIDetector | None = None,
        web_scanner: GeminiWebScanner | None = None,
    ):
        self.w_lexical = settings.SIMILARITY_LEXICAL_WEIGHT if w_lexical is None else w_lexical
        self.w_semantic = settings.SIMILARITY_SEMANTIC_WEIGHT if w_semantic is None else w_semantic
        self.w_stylometric = settings.SIMILARITY_STYLO_WEIGHT if w_stylometric is None else w_stylometric
        self.preprocessor = TextPreprocessor()
        self.tier1_engine = WinnowingLexicalEngine()
        self.tier2_engine = SemanticEngine()
        self.tier3_engine = StylometricEngine()
        self.ai_detector = ai_detector or GeminiAIDetector(stylometric_engine=self.tier3_engine)
        self.web_scanner = web_scanner or GeminiWebScanner(
            lexical_engine=self.tier1_engine, semantic_engine=self.tier2_engine
        )
        self.corpus_bank = corpus_bank or ReferenceCorpusBank.get_instance()

    @staticmethod
    def sanitize_score(val: Any) -> float:
        try:
            f = float(val)
            return 0.0 if math.isnan(f) or math.isinf(f) else round(min(100.0, max(0.0, f)), 2)
        except (TypeError, ValueError):
            return 0.0

    def calculate_composite_score(self, score_t1: float, score_t2: float, score_t3: float) -> float:
        raw = (
            self.w_lexical * self.sanitize_score(score_t1)
            + self.w_semantic * self.sanitize_score(score_t2)
            + self.w_stylometric * self.sanitize_score(score_t3)
        )
        return self.sanitize_score(raw)

    def _aggregate_matched_sources(self, **kwargs) -> list[dict[str, Any]]:
        return aggregate_matched_sources(**kwargs)

    def run_pipeline(
        self,
        original_text: str,
        audit_depth: str = "FULL",
        custom_corpus_index: dict[int, list[dict[str, Any]]] | None = None,
        custom_corpus_chunks: list[dict[str, Any]] | None = None,
        on_progress: Any | None = None,
        corpus_searcher: Any | None = None,
    ) -> HybridAuditResult:
        if not original_text or not original_text.strip():
            return HybridAuditResult(
                score_lexical=0.0, score_semantic=0.0, score_stylometric=0.0, score_composite=0.0,
                audit_depth=audit_depth, sentences=[], heatmap_annotations=[], matched_sources=[],
            )

        sentences = self.preprocessor.segment_sentences(original_text)
        c_index = custom_corpus_index if custom_corpus_index is not None else self.corpus_bank.get_fingerprint_index()
        c_chunks = custom_corpus_chunks if custom_corpus_chunks is not None else self.corpus_bank.get_corpus_chunks()

        t1_res = self.tier1_engine.analyze_document(original_text=original_text, sentences=sentences, corpus_index=c_index)
        score_t1, t1_idx = t1_res.score_t1, {m.sentence_index: m for m in t1_res.sentence_matches}

        if audit_depth == "TIER1_ONLY":
            score_t2, score_t3, score_comp = 0.0, 0.0, self.sanitize_score(score_t1)
            t2_res, t3_res, t2_idx, t3_idx = None, None, {}, {}
            web_matches, web_avail, web_note = [], False, "Mode pindaian cepat (TIER1_ONLY) tidak mencakup pemindaian web."
        else:
            t2_res = self.tier2_engine.analyze_document(
                sentences=sentences, corpus_chunks=c_chunks, exclude_sentence_indices=set(t1_idx.keys()),
                corpus_searcher=corpus_searcher,
            )
            score_t2, t2_idx = t2_res.score_t2, {m.sentence_index: m for m in t2_res.sentence_matches}
            web_matches, web_avail, web_note = scan_web_sources(self.web_scanner, sentences, on_progress)
            score_t1, score_t2 = compute_web_union_scores(
                sentences, set(t1_idx.keys()), set(t2_idx.keys()), web_matches, score_t1, score_t2
            )

            if on_progress:
                on_progress(75, "Tahap 3 · Evaluasi indikasi tulisan AI (Gemini Flash) & kompilasi laporan")
            t3_res = self.ai_detector.analyze_document(original_text=original_text, sentences=sentences)
            score_t3, t3_idx = t3_res.score_t3, {a.sentence_index: a for a in t3_res.sentence_anomalies}
            score_comp = self.calculate_composite_score(score_t1, score_t2, score_t3)

        heatmap = build_heatmap_annotations(sentences, web_matches, t1_idx, t2_idx, t3_idx, audit_depth, score_t3)
        sources = self._aggregate_matched_sources(
            t1_result=t1_res, t2_result=t2_res, score_composite=score_comp,
            web_matches=web_matches, web_scan_available=web_avail, web_scan_note=web_note, audit_depth=audit_depth,
        )
        return HybridAuditResult(
            score_lexical=self.sanitize_score(score_t1), score_semantic=self.sanitize_score(score_t2),
            score_stylometric=self.sanitize_score(score_t3), score_composite=self.sanitize_score(score_comp),
            audit_depth=audit_depth, sentences=sentences, heatmap_annotations=heatmap, matched_sources=sources,
            t1_result=t1_res, t2_result=t2_res, t3_result=t3_res, web_matches=web_matches,
            web_scan_available=web_avail, web_scan_note=web_note,
        )
