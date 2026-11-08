from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings
from app.engine.preprocessor import SentenceSpan
from app.engine.tier1_hasher import compute_kgram_hashes, polynomial_hash, winnow_hashes


@dataclass
class SentenceLexicalMatch:
    sentence_index: int
    matching_fingerprints: int
    total_fingerprints: int
    similarity: float
    matched_corpus_doc_id: str | None = None
    matched_source_title: str | None = None


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
        score_t1, matched_fps = self.calculate_containment(doc_fps, all_corpus_hashes)

        sentence_matches: list[SentenceLexicalMatch] = []
        corpus_hits: dict[str, dict[str, Any]] = {}

        for s in sentences:
            s_fps = self.extract_fingerprints(s.text)
            s_hashes = {h for h, _ in s_fps}
            s_matched = s_hashes.intersection(all_corpus_hashes) if s_hashes else set()
            if not s_matched:
                continue

            sim_ratio = len(s_matched) / len(s_hashes)
            if sim_ratio >= 0.40 or len(s_matched) >= 3:
                source_counts: dict[str, int] = {}
                source_info: dict[str, dict[str, str]] = {}
                for h in s_matched:
                    for ref in corpus_index.get(h, []):
                        d_id = str(ref.get("doc_id", "corpus-doc"))
                        source_counts[d_id] = source_counts.get(d_id, 0) + 1
                        source_info.setdefault(d_id, {
                            "title": ref.get("title", "Dokumen Korpus Pembanding"),
                            "category": ref.get("category", "Umum"),
                        })

                best_id = max(source_counts, key=source_counts.get) if source_counts else None
                best_title = source_info[best_id]["title"] if best_id else "Korpus Pembanding"
                sentence_matches.append(SentenceLexicalMatch(
                    sentence_index=s.index, matching_fingerprints=len(s_matched),
                    total_fingerprints=len(s_hashes), similarity=round(min(1.0, sim_ratio), 2),
                    matched_corpus_doc_id=best_id, matched_source_title=best_title,
                ))
                if best_id:
                    hit = corpus_hits.setdefault(best_id, {
                        "corpus_doc_id": best_id, "title": best_title,
                        "category": source_info[best_id]["category"], "match_count": 0,
                    })
                    hit["match_count"] += len(s_matched)

        return LexicalAnalysisResult(
            score_t1=score_t1, doc_fingerprints=doc_fps, matched_fingerprints=matched_fps,
            sentence_matches=sentence_matches, corpus_contributions=corpus_hits,
        )
