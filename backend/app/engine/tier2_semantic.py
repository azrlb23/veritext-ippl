from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any
from app.core.config import settings
from app.engine.preprocessor import SentenceSpan
from app.engine.tier1_filters import is_heading_or_too_short
from app.engine.tier2_reranker import SemanticReranker
from app.engine.tier2_fallback_embedder import cosine_similarity, embed_sentence_dense, get_inference_context

logger = logging.getLogger(__name__)


@dataclass
class SentenceSemanticMatch:
    sentence_index: int
    similarity: float
    matched_chunk_id: str | None = None
    matched_source_title: str | None = None
    matched_chunk_text: str | None = None
    matched_corpus_doc_id: str | None = None
    secondary_sources: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SemanticAnalysisResult:
    score_t2: float
    sentence_matches: list[SentenceSemanticMatch] = field(default_factory=list)
    corpus_contributions: dict[str, dict[str, Any]] = field(default_factory=dict)


class SemanticEngine:
    """Engine for sentence-level semantic vector embedding and cosine similarity comparison."""

    PARAPHRASE_THRESHOLD: float = 0.75
    _shared_transformer_model = None
    _shared_model_attempted = False
    cosine_similarity = staticmethod(cosine_similarity)

    def __init__(self, dimension: int = 384, paraphrase_threshold: float = 0.75):
        self.dimension, self.paraphrase_threshold, self._transformer_model = dimension or settings.EMBEDDING_DIMENSION, paraphrase_threshold, None

    def embed_sentence_dense(self, text: str) -> list[float]:
        return embed_sentence_dense(text, dimension=self.dimension)

    @classmethod
    def get_shared_model(cls):
        if not cls._shared_model_attempted:
            cls._shared_model_attempted = True
            try:
                from sentence_transformers import SentenceTransformer

                cls._shared_transformer_model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
            except Exception as e:  # noqa: BLE001
                logger.debug("SentenceTransformer load skipped: %s", e)
                cls._shared_transformer_model = None
        return cls._shared_transformer_model

    def embed_sentence(self, text: str) -> list[float]:
        model = self.get_shared_model() if self._transformer_model is None else self._transformer_model
        if model is not None:
            try:
                with get_inference_context():
                    return model.encode(text, convert_to_numpy=True, normalize_embeddings=True).tolist()
            except Exception as e:  # noqa: BLE001
                logger.debug("Model encode error, falling back to dense: %s", e)
        return self.embed_sentence_dense(text)

    def embed_sentences(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self.get_shared_model() if self._transformer_model is None else self._transformer_model
        if model is not None:
            try:
                with get_inference_context():
                    return model.encode(texts, convert_to_numpy=True, batch_size=32, normalize_embeddings=True).tolist()
            except Exception as e:  # noqa: BLE001
                logger.debug("Batch encode error, falling back to dense: %s", e)
        return [self.embed_sentence_dense(t) for t in texts]

    def _best_chunk(self, s_emb: list[float], corpus_chunks: list[dict[str, Any]]):
        best_sim, best_chunk = -1.0, None
        for chunk in corpus_chunks:
            c_emb = chunk.get("embedding")
            if c_emb is None or len(c_emb) == 0:
                continue
            sim = self.cosine_similarity(s_emb, c_emb)
            if sim > best_sim:
                best_sim, best_chunk = sim, chunk
        return best_sim, best_chunk

    def analyze_document(
        self, sentences: list[SentenceSpan], corpus_chunks: list[dict[str, Any]],
        exclude_sentence_indices: set | None = None, corpus_searcher: Any | None = None,
    ) -> SemanticAnalysisResult:
        exclude = exclude_sentence_indices or set()
        sentence_matches: list[SentenceSemanticMatch] = []
        corpus_hits: dict[str, dict[str, Any]] = {}
        if not sentences or not (corpus_chunks or corpus_searcher):
            return SemanticAnalysisResult(score_t2=0.0)

        doc_embeddings = self.embed_sentences([s.text for s in sentences])
        matched_similarities, candidates = [], []
        for idx, s in enumerate(sentences):
            if s.is_citation or idx in exclude or is_heading_or_too_short(s.text):
                continue
            hits: list[tuple[float, dict[str, Any]]] = []
            best_sim, best_chunk = self._best_chunk(doc_embeddings[idx], corpus_chunks)
            if best_chunk and best_sim >= self.paraphrase_threshold:
                hits.append((best_sim, best_chunk))
            if corpus_searcher and hasattr(corpus_searcher, "nearest_k"):
                hits.extend((sim, ch) for sim, ch in corpus_searcher.nearest_k(doc_embeddings[idx], k=5) if sim >= self.paraphrase_threshold)
            elif corpus_searcher and (ann := corpus_searcher.nearest(doc_embeddings[idx])) and ann[0] >= self.paraphrase_threshold:
                hits.append(ann)
            seen_docs: set[str] = set()
            for sim, ch in sorted(hits, key=lambda x: x[0], reverse=True):
                did = str(ch.get("corpus_doc_id", "corpus-doc"))
                if did not in seen_docs:
                    seen_docs.add(did)
                    candidates.append((s, sim, ch))
        keep = SemanticReranker.accept_mask([(s.text, c.get("chunk_text", "")) for s, _, c in candidates])
        by_sent: dict[int, list[tuple[SentenceSpan, float, dict[str, Any]]]] = {}
        for item, accepted in zip(candidates, keep):
            if accepted:
                by_sent.setdefault(item[0].index, []).append(item)
        for s_idx, group in by_sent.items():
            s, best_sim, best_chunk = group[0]
            matched_similarities.append(best_sim)
            doc_id = str(best_chunk.get("corpus_doc_id", "corpus-doc"))
            title = best_chunk.get("title", "Dokumen Korpus Pembanding")
            sec = [{"source_title": c.get("title"), "source_category": c.get("category", "Bank Korpus"), "similarity": round(sim, 2), "matched_source_text": c.get("chunk_text")} for _, sim, c in group[1:]]
            sentence_matches.append(SentenceSemanticMatch(
                sentence_index=s_idx, similarity=round(best_sim, 2), matched_chunk_id=str(best_chunk.get("chunk_id", "")),
                matched_source_title=title, matched_chunk_text=best_chunk.get("chunk_text", ""), matched_corpus_doc_id=doc_id, secondary_sources=sec,
            ))
            hit = corpus_hits.setdefault(doc_id, {"corpus_doc_id": doc_id, "title": title, "category": best_chunk.get("category", "Umum"), "match_count": 0, "total_sim": 0.0})
            hit["match_count"] += 1
            hit["total_sim"] += best_sim

        meaningful = len([s for s in sentences if not s.is_citation])
        has_hits = meaningful > 0 and matched_similarities
        score_t2 = (sum(matched_similarities) / meaningful) * 100.0 if has_hits else 0.0
        return SemanticAnalysisResult(
            score_t2=round(min(100.0, max(0.0, score_t2)), 2),
            sentence_matches=sentence_matches,
            corpus_contributions=corpus_hits,
        )
