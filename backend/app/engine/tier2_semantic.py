import hashlib
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.engine.preprocessor import SentenceSpan, TextPreprocessor


@dataclass
class SentenceSemanticMatch:
    sentence_index: int
    similarity: float
    matched_chunk_id: Optional[str] = None
    matched_source_title: Optional[str] = None
    matched_chunk_text: Optional[str] = None
    matched_corpus_doc_id: Optional[str] = None


@dataclass
class SemanticAnalysisResult:
    score_t2: float
    sentence_matches: List[SentenceSemanticMatch] = field(default_factory=list)
    corpus_contributions: Dict[str, Dict[str, Any]] = field(default_factory=dict)


from contextlib import nullcontext


def get_inference_context():
    """Provides torch.inference_mode or torch.no_grad context manager to prevent RAM leakage."""
    try:
        import torch
        if hasattr(torch, "inference_mode"):
            return torch.inference_mode()
        elif hasattr(torch, "no_grad"):
            return torch.no_grad()
    except ImportError:
        pass
    return nullcontext()


class SemanticEngine:
    """Engine for sentence-level semantic vector embedding and cosine similarity comparison.
    
    Operates in 384-dimensional vector space (MiniLM-L12 specification).
    Includes deterministic dense subword/stem projection fallback for offline/low-resource
    environments, ensuring identical, paraphrased, and unrelated sentences are accurately scored.
    """

    PARAPHRASE_THRESHOLD: float = 0.75

    # Indonesian common morphological affixes for root approximation
    PREFIXES = ("meng", "meny", "men", "mem", "me", "peng", "peny", "pen", "pem", "pe", "di", "ter", "ber", "per", "se")
    SUFFIXES = ("kan", "an", "nya", "lah", "kah", "i")

    # Common Indonesian stopwords
    STOPWORDS = {
        "yang", "di", "dan", "dari", "ini", "itu", "untuk", "pada", "adalah", "dengan",
        "ke", "oleh", "dalam", "sebagai", "akan", "juga", "atau", "tidak", "dapat",
        "secara", "ia", "mereka", "kita", "kamu", "saya", "telah", "bisa", "hal",
    }

    # Indonesian academic synonym mappings to canonical concept IDs for paraphrase detection
    SYNONYM_CONCEPTS = {
        # Smart / intelligent
        "cerdas": "concept:smart", "pintar": "concept:smart", "pandai": "concept:smart", "intelektual": "concept:smart",
        # Use / utilize / apply
        "manfaat": "concept:use", "memanfaatkan": "concept:use", "pemanfaatan": "concept:use",
        "guna": "concept:use", "menggunakan": "concept:use", "penggunaan": "concept:use", "kegunaan": "concept:use",
        "pakai": "concept:use", "memakai": "concept:use", "terap": "concept:use", "menerapkan": "concept:use", "penerapan": "concept:use",
        # Combine / integrate / fusion
        "padu": "concept:combine", "perpaduan": "concept:combine", "memadukan": "concept:combine", "kombinasi": "concept:combine",
        "mengombinasikan": "concept:combine", "gabung": "concept:combine", "penggabungan": "concept:combine",
        "integrasi": "concept:combine", "mengintegrasikan": "concept:combine",
        # Detection / identify
        "deteksi": "concept:detect", "mendeteksi": "concept:detect", "pendeteksian": "concept:detect", "terdeteksi": "concept:detect",
        "identifikasi": "concept:detect", "mengidentifikasi": "concept:detect", "pengidentifikasian": "concept:detect",
        "temu": "concept:detect", "menemukan": "concept:detect",
        # Plagiarism / duplicate
        "plagiat": "concept:plagiarism", "plagiarisme": "concept:plagiarism", "jiplak": "concept:plagiarism", "penjiplakan": "concept:plagiarism",
        # Similarity
        "mirip": "concept:similarity", "kemiripan": "concept:similarity", "sama": "concept:similarity", "kesamaan": "concept:similarity", "serupa": "concept:similarity",
        # Method / algorithm
        "algoritma": "concept:algorithm", "metode": "concept:algorithm", "metodologi": "concept:algorithm", "pendekatan": "concept:algorithm", "teknik": "concept:algorithm",
        # Text / manuscript
        "naskah": "concept:text", "dokumen": "concept:text", "teks": "concept:text", "tulisan": "concept:text", "karya": "concept:text", "artikel": "concept:text", "paper": "concept:text",
        # Representation / vector
        "representasi": "concept:vector", "vektor": "concept:vector", "embedding": "concept:vector",
        # Lexical & semantics
        "leksikal": "concept:lexical", "kata": "concept:lexical",
        "semantik": "concept:semantic", "makna": "concept:semantic", "konteks": "concept:semantic",
        # Deep learning / AI
        "deep": "concept:deeplearning", "mendalam": "concept:deeplearning",
        "learning": "concept:deeplearning", "pembelajaran": "concept:deeplearning",
        # Base / foundation
        "basis": "concept:base", "berbasis": "concept:base", "dasar": "concept:base", "berdasarkan": "concept:base",
        # Conjunctions
        "dan": "concept:and", "serta": "concept:and", "beserta": "concept:and",
    }

    def __init__(self, dimension: int = 384, paraphrase_threshold: float = 0.75):
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self.paraphrase_threshold = paraphrase_threshold
        self._transformer_model = None
        self._attempted_transformer_load = False

    def _get_stem(self, word: str) -> str:
        """Lightweight Indonesian stemmer for semantic root alignment."""
        w = word.lower().strip()
        if len(w) <= 4:
            return w

        # Strip prefixes
        for p in self.PREFIXES:
            if w.startswith(p) and len(w) - len(p) >= 3:
                w = w[len(p):]
                break

        # Strip suffixes
        for s in self.SUFFIXES:
            if w.endswith(s) and len(w) - len(s) >= 3:
                w = w[:-len(s)]
                break

        return w

    def embed_sentence_dense(self, text: str) -> List[float]:
        """Generates a deterministic 384-D L2-normalized dense vector embedding.
        
        Uses subword n-grams, canonical concept mapping, morphological roots, and semantic hashing.
        """
        vec = [0.0] * self.dimension
        if not text or not text.strip():
            return vec

        tokens = TextPreprocessor.tokenize_words(text)
        if not tokens:
            return vec

        # 1. Feature extraction
        features: List[Tuple[str, float]] = []

        for i, token in enumerate(tokens):
            stem = self._get_stem(token)

            # Canonical synonym concept mapping with high weight
            if token in self.SYNONYM_CONCEPTS:
                features.append((self.SYNONYM_CONCEPTS[token], 4.0))
            elif stem in self.SYNONYM_CONCEPTS:
                features.append((self.SYNONYM_CONCEPTS[stem], 3.5))

            weight = 0.5 if token in self.STOPWORDS else 2.0
            features.append((f"tok:{token}", weight))
            features.append((f"stem:{stem}", weight * 1.5))

            # Character 3-grams of content words for morphological robustness
            if len(token) >= 3 and token not in self.STOPWORDS:
                for c_i in range(len(token) - 2):
                    features.append((f"char3:{token[c_i:c_i+3]}", 0.6))

            # Bigram syntactic context
            if i < len(tokens) - 1:
                next_stem = self._get_stem(tokens[i + 1])
                features.append((f"bi:{stem}_{next_stem}", 1.2))

        # 2. Dense projection into 384 dimensions using SHA-256 pseudo-random projection
        for feat_name, weight in features:
            h = hashlib.sha256(feat_name.encode("utf-8")).digest()
            # Distribute feature across dimensions with sign
            for offset in range(0, 16, 4):
                idx = int.from_bytes(h[offset:offset + 2], "big") % self.dimension
                sign = 1.0 if (h[offset + 2] % 2 == 0) else -1.0
                magnitude = (h[offset + 3] / 255.0) * weight
                vec[idx] += sign * magnitude

        # 3. L2 Unit Normalization: ||v|| = 1.0
        norm_sq = sum(x * x for x in vec)
        if norm_sq > 0:
            inv_norm = 1.0 / math.sqrt(norm_sq)
            vec = [x * inv_norm for x in vec]

        return vec

    _shared_transformer_model = None
    _shared_model_attempted = False

    @classmethod
    def get_shared_model(cls):
        """Singleton accessor for sentence transformer model."""
        if not cls._shared_model_attempted:
            cls._shared_model_attempted = True
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
                cls._shared_transformer_model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
            except Exception:
                cls._shared_transformer_model = None
        return cls._shared_transformer_model

    def embed_sentence(self, text: str) -> List[float]:
        """Generates 384-D vector embedding for text using singleton transformer model with torch inference mode."""
        model = self.get_shared_model() if self._transformer_model is None else self._transformer_model
        if model is not None:
            try:
                with get_inference_context():
                    emb = model.encode(text, convert_to_numpy=True).tolist()
                    return emb
            except Exception:
                pass

        return self.embed_sentence_dense(text)

    def embed_sentences(self, texts: List[str]) -> List[List[float]]:
        """Batch generates 384-D vector embeddings for multiple sentences efficiently."""
        if not texts:
            return []
        model = self.get_shared_model() if self._transformer_model is None else self._transformer_model
        if model is not None:
            try:
                with get_inference_context():
                    embs = model.encode(texts, convert_to_numpy=True, batch_size=32).tolist()
                    return embs
            except Exception:
                pass

        return [self.embed_sentence_dense(t) for t in texts]

    @staticmethod
    def cosine_similarity(u: Any, v: Any) -> float:
        """Calculates cosine similarity between two vectors: (u . v) / (||u|| * ||v||)."""
        if u is None or v is None:
            return 0.0
        try:
            if len(u) == 0 or len(v) == 0 or len(u) != len(v):
                return 0.0
        except TypeError:
            return 0.0

        dot = 0.0
        norm_u_sq = 0.0
        norm_v_sq = 0.0

        for a, b in zip(u, v):
            dot += float(a) * float(b)
            norm_u_sq += float(a) * float(a)
            norm_v_sq += float(b) * float(b)

        if norm_u_sq <= 1e-12 or norm_v_sq <= 1e-12:
            return 0.0

        sim = dot / (math.sqrt(norm_u_sq) * math.sqrt(norm_v_sq))
        # Clamp to [-1.0, 1.0] to guard against floating point inaccuracies
        return max(-1.0, min(1.0, sim))

    def analyze_document(
        self,
        sentences: List[SentenceSpan],
        corpus_chunks: List[Dict[str, Any]],
        exclude_sentence_indices: Optional[set] = None,
    ) -> SemanticAnalysisResult:
        """Compares document sentences against corpus chunks using cosine similarity.
        
        Args:
            sentences: segmented sentences from document
            corpus_chunks: list of dicts with keys: chunk_id, corpus_doc_id, title, category, chunk_text, embedding
            exclude_sentence_indices: optional set of sentence indices already matched by Tier 1
        """
        exclude = exclude_sentence_indices or set()
        sentence_matches: List[SentenceSemanticMatch] = []
        corpus_hits: Dict[str, Dict[str, Any]] = {}

        if not sentences or not corpus_chunks:
            return SemanticAnalysisResult(score_t2=0.0)

        # Precompute or retrieve embeddings for document sentences in batch
        doc_embeddings = self.embed_sentences([s.text for s in sentences])

        matched_similarities: List[float] = []

        for idx, s in enumerate(sentences):
            # Skip citations and sentences already matched by lexical tier 1 if desired
            if s.is_citation or idx in exclude:
                continue

            s_emb = doc_embeddings[idx]
            best_sim = -1.0
            best_chunk: Optional[Dict[str, Any]] = None

            for chunk in corpus_chunks:
                c_emb = chunk.get("embedding")
                if c_emb is None:
                    continue
                try:
                    if len(c_emb) == 0:
                        continue
                except TypeError:
                    continue

                sim = self.cosine_similarity(s_emb, c_emb)
                if sim > best_sim:
                    best_sim = sim
                    best_chunk = chunk

            # Threshold check for semantic paraphrase detection
            if best_chunk and best_sim >= self.paraphrase_threshold:
                matched_similarities.append(best_sim)
                doc_id = str(best_chunk.get("corpus_doc_id", "corpus-doc"))
                title = best_chunk.get("title", "Dokumen Korpus Pembanding")
                cat = best_chunk.get("category", "Umum")

                sentence_matches.append(SentenceSemanticMatch(
                    sentence_index=s.index,
                    similarity=round(best_sim, 2),
                    matched_chunk_id=str(best_chunk.get("chunk_id", "")),
                    matched_source_title=title,
                    matched_chunk_text=best_chunk.get("chunk_text", ""),
                    matched_corpus_doc_id=doc_id,
                ))

                if doc_id not in corpus_hits:
                    corpus_hits[doc_id] = {
                        "corpus_doc_id": doc_id,
                        "title": title,
                        "category": cat,
                        "match_count": 0,
                        "total_sim": 0.0,
                    }
                corpus_hits[doc_id]["match_count"] += 1
                corpus_hits[doc_id]["total_sim"] += best_sim

        # Calculate Tier 2 overall score
        # Percentage of sentences semantically matched, weighted by their similarity
        total_eval_sentences = len([s for s in sentences if not s.is_citation])
        if total_eval_sentences > 0 and matched_similarities:
            score_t2 = (sum(matched_similarities) / total_eval_sentences) * 100.0
        else:
            score_t2 = 0.0

        score_t2 = round(min(100.0, max(0.0, score_t2)), 2)

        return SemanticAnalysisResult(
            score_t2=score_t2,
            sentence_matches=sentence_matches,
            corpus_contributions=corpus_hits,
        )
