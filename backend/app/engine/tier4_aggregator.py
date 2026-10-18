from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.reference_corpus import ReferenceCorpusBank
from app.engine.tier1_lexical import WinnowingLexicalEngine, LexicalAnalysisResult
from app.engine.tier2_semantic import SemanticEngine, SemanticAnalysisResult
from app.engine.tier3_stylometric import StylometricEngine, StylometricAnalysisResult


@dataclass
class HeatmapAnnotationData:
    start: int
    end: int
    tier: str  # T1, T2, T3
    color: str  # RED, ORANGE, YELLOW
    similarity: float
    source_title: str
    text_snippet: str
    source_chunk_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "tier": self.tier,
            "color": self.color,
            "similarity": round(self.similarity, 2),
            "source_title": self.source_title,
            "text_snippet": self.text_snippet,
            "source_chunk_id": self.source_chunk_id,
        }


@dataclass
class MatchedSourceData:
    corpus_doc_id: str
    title: str
    category: str
    contribution_pct: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "corpus_doc_id": self.corpus_doc_id,
            "title": self.title,
            "category": self.category,
            "contribution_pct": round(self.contribution_pct, 1),
        }


@dataclass
class HybridAuditResult:
    score_lexical: float
    score_semantic: float
    score_stylometric: float
    score_composite: float
    audit_depth: str
    sentences: List[SentenceSpan]
    heatmap_annotations: List[Dict[str, Any]]
    matched_sources: List[Dict[str, Any]]
    t1_result: Optional[LexicalAnalysisResult] = None
    t2_result: Optional[SemanticAnalysisResult] = None
    t3_result: Optional[StylometricAnalysisResult] = None


class HybridAggregator:
    """Orchestrator for the 4-Tier Hybrid Plagiarism Detection Engine.
    
    1. Preprocessing & sentence segmentation with exact character offsets.
    2. Tier 1: Winnowing Lexical Fingerprinting.
    3. Tier 2: Sentence Transformers 384D Dense Semantic Cosine Similarity.
    4. Tier 3: Stylometric Burstiness & TTR AI Anomaly Detection.
    5. Tier 4: Weighted Composite Aggregation and Heatmap Annotation Assembly.
    """

    def __init__(
        self,
        w_lexical: Optional[float] = None,
        w_semantic: Optional[float] = None,
        w_stylometric: Optional[float] = None,
        corpus_bank: Optional[ReferenceCorpusBank] = None,
    ):
        self.w_lexical = w_lexical if w_lexical is not None else settings.SIMILARITY_LEXICAL_WEIGHT
        self.w_semantic = w_semantic if w_semantic is not None else settings.SIMILARITY_SEMANTIC_WEIGHT
        self.w_stylometric = w_stylometric if w_stylometric is not None else settings.SIMILARITY_STYLO_WEIGHT

        self.preprocessor = TextPreprocessor()
        self.tier1_engine = WinnowingLexicalEngine()
        self.tier2_engine = SemanticEngine()
        self.tier3_engine = StylometricEngine()
        self.corpus_bank = corpus_bank or ReferenceCorpusBank.get_instance()

    def run_pipeline(
        self,
        original_text: str,
        audit_depth: str = "FULL",
        custom_corpus_index: Optional[Dict[int, List[Dict[str, Any]]]] = None,
        custom_corpus_chunks: Optional[List[Dict[str, Any]]] = None,
    ) -> HybridAuditResult:
        """Executes the complete 4-tier pipeline on raw manuscript text."""
        if not original_text or not original_text.strip():
            return HybridAuditResult(
                score_lexical=0.0,
                score_semantic=0.0,
                score_stylometric=0.0,
                score_composite=0.0,
                audit_depth=audit_depth,
                sentences=[],
                heatmap_annotations=[],
                matched_sources=[],
            )

        # Step 1: Preprocessing & Sentence Segmentation
        sentences = self.preprocessor.segment_sentences(original_text)

        # Get corpus indexes
        corpus_index = (
            custom_corpus_index
            if custom_corpus_index is not None
            else self.corpus_bank.get_fingerprint_index()
        )
        corpus_chunks = (
            custom_corpus_chunks
            if custom_corpus_chunks is not None
            else self.corpus_bank.get_corpus_chunks()
        )

        # Step 2: Tier 1 Winnowing Lexical Analysis
        t1_result = self.tier1_engine.analyze_document(
            original_text=original_text,
            sentences=sentences,
            corpus_index=corpus_index,
        )
        score_t1 = t1_result.score_t1

        # Track sentence matches across tiers
        tier1_matched_indices = {m.sentence_index: m for m in t1_result.sentence_matches}

        if audit_depth == "TIER1_ONLY":
            score_t2 = 0.0
            score_t3 = 0.0
            score_composite = score_t1
            t2_result = None
            t3_result = None
            tier2_matched_indices = {}
            tier3_anomalies_by_index = {}
        else:
            # Step 3: Tier 2 Semantic Cosine Similarity Analysis
            # Sentences strongly matched by lexical Tier 1 can be skipped or included
            t2_result = self.tier2_engine.analyze_document(
                sentences=sentences,
                corpus_chunks=corpus_chunks,
                exclude_sentence_indices=set(tier1_matched_indices.keys()),
            )
            score_t2 = t2_result.score_t2
            tier2_matched_indices = {m.sentence_index: m for m in t2_result.sentence_matches}

            # Step 4: Tier 3 Stylometric AI Anomaly Detection
            t3_result = self.tier3_engine.analyze_document(
                original_text=original_text,
                sentences=sentences,
            )
            score_t3 = t3_result.score_t3
            tier3_anomalies_by_index = {a.sentence_index: a for a in t3_result.sentence_anomalies}

            # Step 5: Weighted Composite Score Calculation
            raw_composite = (
                self.w_lexical * score_t1 +
                self.w_semantic * score_t2 +
                self.w_stylometric * score_t3
            )
            score_composite = round(min(100.0, max(0.0, raw_composite)), 2)

        # Build Heatmap Annotations
        heatmap_annotations: List[Dict[str, Any]] = []

        for s in sentences:
            # Priority 1: Tier 1 Lexical (RED)
            if s.index in tier1_matched_indices:
                t1_match = tier1_matched_indices[s.index]
                anno = HeatmapAnnotationData(
                    start=s.start_char,
                    end=s.end_char,
                    tier="T1",
                    color="RED",
                    similarity=t1_match.similarity,
                    source_title=t1_match.matched_source_title or "Korpus Pembanding Leksikal",
                    text_snippet=s.text,
                    source_chunk_id=t1_match.matched_corpus_doc_id,
                )
                heatmap_annotations.append(anno.to_dict())

            # Priority 2: Tier 2 Semantic Paraphrase (ORANGE)
            elif s.index in tier2_matched_indices:
                t2_match = tier2_matched_indices[s.index]
                anno = HeatmapAnnotationData(
                    start=s.start_char,
                    end=s.end_char,
                    tier="T2",
                    color="ORANGE",
                    similarity=t2_match.similarity,
                    source_title=t2_match.matched_source_title or "Korpus Pembanding Semantik",
                    text_snippet=s.text,
                    source_chunk_id=t2_match.matched_chunk_id,
                )
                heatmap_annotations.append(anno.to_dict())

            # Priority 3: Tier 3 Stylometric AI Anomaly (YELLOW)
            elif audit_depth == "FULL" and s.index in tier3_anomalies_by_index and score_t3 >= 30.0:
                t3_anomaly = tier3_anomalies_by_index[s.index]
                anno = HeatmapAnnotationData(
                    start=s.start_char,
                    end=s.end_char,
                    tier="T3",
                    color="YELLOW",
                    similarity=t3_anomaly.anomaly_score,
                    source_title="AI Pattern Indicator",
                    text_snippet=s.text,
                    source_chunk_id=None,
                )
                heatmap_annotations.append(anno.to_dict())

        # Compile Matched Sources Breakdown
        matched_sources = self._aggregate_matched_sources(
            t1_result=t1_result,
            t2_result=t2_result,
            score_composite=score_composite,
        )

        return HybridAuditResult(
            score_lexical=score_t1,
            score_semantic=score_t2,
            score_stylometric=score_t3,
            score_composite=score_composite,
            audit_depth=audit_depth,
            sentences=sentences,
            heatmap_annotations=heatmap_annotations,
            matched_sources=matched_sources,
            t1_result=t1_result,
            t2_result=t2_result,
            t3_result=t3_result,
        )

    def _aggregate_matched_sources(
        self,
        t1_result: Optional[LexicalAnalysisResult],
        t2_result: Optional[SemanticAnalysisResult],
        score_composite: float,
    ) -> List[Dict[str, Any]]:
        """Aggregates and formats matched corpus sources with relative contribution percentages."""
        source_weights: Dict[str, Dict[str, Any]] = {}

        # 1. Collect from Tier 1
        if t1_result:
            for doc_id, data in t1_result.corpus_contributions.items():
                if doc_id not in source_weights:
                    source_weights[doc_id] = {
                        "corpus_doc_id": doc_id,
                        "title": data.get("title", "Dokumen Korpus"),
                        "category": data.get("category", "Umum"),
                        "raw_weight": 0.0,
                    }
                source_weights[doc_id]["raw_weight"] += data.get("match_count", 1) * 1.5

        # 2. Collect from Tier 2
        if t2_result:
            for doc_id, data in t2_result.corpus_contributions.items():
                if doc_id not in source_weights:
                    source_weights[doc_id] = {
                        "corpus_doc_id": doc_id,
                        "title": data.get("title", "Dokumen Korpus"),
                        "category": data.get("category", "Umum"),
                        "raw_weight": 0.0,
                    }
                source_weights[doc_id]["raw_weight"] += data.get("total_sim", 1.0) * 2.0

        if not source_weights:
            return []

        total_weight = sum(item["raw_weight"] for item in source_weights.values())
        if total_weight <= 0:
            total_weight = 1.0

        matched_list: List[Dict[str, Any]] = []
        for item in source_weights.values():
            ratio = item["raw_weight"] / total_weight
            contrib = round(ratio * max(score_composite, 5.0), 1)
            matched_list.append(MatchedSourceData(
                corpus_doc_id=item["corpus_doc_id"],
                title=item["title"],
                category=item["category"],
                contribution_pct=contrib,
            ).to_dict())

        # Sort descending by contribution percentage
        matched_list.sort(key=lambda x: x["contribution_pct"], reverse=True)
        return matched_list
