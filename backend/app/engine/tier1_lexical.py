from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings
from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.tier1_hasher import compute_kgram_hashes, polynomial_hash, winnow_hashes

_STOPWORDS = frozenset({
    "dan", "atau", "yang", "untuk", "dengan", "pada", "dari", "dalam", "oleh", "sebagai",
    "serta", "terhadap", "adalah", "ini", "itu", "agar", "karena", "sehingga", "bahwa",
    "dapat", "akan", "telah", "juga", "antara", "secara", "menjadi", "merupakan", "tersebut",
    "bab", "the", "and", "for", "with", "that", "this", "from", "into", "are", "was", "were", "been", "have", "has",
})

def _content_words(text: str) -> set[str]:
    return {w for w in TextPreprocessor.tokenize_words(text) if len(w) >= 4 and w not in _STOPWORDS}


@dataclass
class SentenceLexicalMatch:
    sentence_index: int
    matching_fingerprints: int
    total_fingerprints: int
    similarity: float
    matched_corpus_doc_id: str | None = None
    matched_source_title: str | None = None
    matched_source_category: str | None = None
    matched_source_snippet: str | None = None
    secondary_sources: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class LexicalAnalysisResult:
    score_t1: float
    doc_fingerprints: list[tuple[int, int]]
    matched_fingerprints: set[int]
    sentence_matches: list[SentenceLexicalMatch] = field(default_factory=list)
    corpus_contributions: dict[str, dict[str, Any]] = field(default_factory=dict)


class WinnowingLexicalEngine:
    """Implements the Winnowing Fingerprinting Algorithm for lexical plagiarism detection."""

    def __init__(
        self,
        k: int | None = None,
        w: int | None = None,
        base: int = 257,
        mod: int = 1_000_000_007,
    ):
        self.k = k or settings.WINNOWING_K_GRAM
        self.w = w or settings.WINNOWING_WINDOW_SIZE
        self.base = base
        self.mod = mod
        self.base_k_minus_1 = pow(self.base, self.k - 1, self.mod)

    def polynomial_hash(self, substring: str) -> int:
        return polynomial_hash(substring, self.base, self.mod)

    def compute_kgram_hashes(self, text: str) -> list[tuple[int, int]]:
        return compute_kgram_hashes(text, self.k, self.base, self.mod, self.base_k_minus_1)

    def winnow(self, hashes: list[tuple[int, int]]) -> list[tuple[int, int]]:
        return winnow_hashes(hashes, self.w)

    def extract_fingerprints(self, text: str) -> list[tuple[int, int]]:
        return self.winnow(self.compute_kgram_hashes(text))

    def calculate_containment(
        self, doc_fps: list[tuple[int, int]], corpus_fps: set[int]
    ) -> tuple[float, set[int]]:
        doc_hash_set = {h for h, _ in doc_fps}
        if not doc_hash_set:
            return 0.0, set()
        intersection = doc_hash_set.intersection(corpus_fps)
        containment = (len(intersection) / len(doc_hash_set)) * 100.0
        return round(min(100.0, max(0.0, containment)), 2), intersection

    def analyze_document(
        self,
        original_text: str,
        sentences: list[SentenceSpan],
        corpus_index: dict[int, list[dict[str, Any]]],
    ) -> LexicalAnalysisResult:
        doc_fps = self.extract_fingerprints(original_text)
        all_corpus_hashes = set(corpus_index.keys())
        _, matched_fps = self.calculate_containment(doc_fps, all_corpus_hashes)
        sentence_matches: list[SentenceLexicalMatch] = []
        corpus_hits: dict[str, dict[str, Any]] = {}

        for s in sentences:
            s_fps = self.extract_fingerprints(s.text)
            s_hashes = {h for h, _ in s_fps}
            s_matched = s_hashes.intersection(all_corpus_hashes) if s_hashes else set()
            if not s_matched:
                continue

            doc_hits: dict[str, set[int]] = {}
            source_info: dict[str, dict[str, str]] = {}
            for h in s_matched:
                for ref in corpus_index.get(h, []):
                    d_id = str(ref.get("doc_id", "corpus-doc"))
                    doc_hits.setdefault(d_id, set()).add(h)
                    source_info.setdefault(d_id, {
                        "title": ref.get("title", "Dokumen Korpus Pembanding"),
                        "category": ref.get("category", "Umum"),
                        "snippet": ref.get("snippet", ""),
                    })

            ranked = sorted(doc_hits.items(), key=lambda x: len(x[1]), reverse=True)
            if not ranked:
                continue
            best_id, best_hashes = ranked[0]
            best_ratio = len(best_hashes) / len(s_hashes)
            best_info = source_info[best_id]
            snippet = best_info.get("snippet") or ""
            shared_cw = len(_content_words(s.text).intersection(_content_words(snippet))) if snippet else 2
            if best_ratio >= 0.50 and len(best_hashes) >= 4 and shared_cw >= 2:
                best_title = best_info.get("title", "Korpus Pembanding")
                sec = [
                    {
                        "source_title": source_info[d_id]["title"],
                        "source_category": source_info[d_id]["category"],
                        "similarity": round(min(1.0, len(hset) / len(s_hashes)), 2),
                        "matched_source_text": source_info[d_id].get("snippet") or None,
                    }
                    for d_id, hset in ranked[1:]
                    if len(hset) / len(s_hashes) >= 0.40 and len(hset) >= 3
                ]
                sentence_matches.append(SentenceLexicalMatch(
                    sentence_index=s.index, matching_fingerprints=len(best_hashes),
                    total_fingerprints=len(s_hashes), similarity=round(min(1.0, best_ratio), 2),
                    matched_corpus_doc_id=best_id, matched_source_title=best_title,
                    matched_source_category=best_info.get("category"),
                    matched_source_snippet=best_info.get("snippet") or None,
                    secondary_sources=sec,
                ))
                hit = corpus_hits.setdefault(best_id, {"corpus_doc_id": best_id, "title": best_title, "category": best_info["category"], "match_count": 0})
                hit["match_count"] += len(best_hashes)

        meaningful = max(1, len([s for s in sentences if not s.is_citation]))
        tuned_t1 = round(min(100.0, (sum(m.similarity for m in sentence_matches) / meaningful) * 100.0), 2) if sentence_matches else 0.0
        return LexicalAnalysisResult(
            score_t1=tuned_t1, doc_fingerprints=doc_fps, matched_fingerprints=matched_fps,
            sentence_matches=sentence_matches, corpus_contributions=corpus_hits,
        )
