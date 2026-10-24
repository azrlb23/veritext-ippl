from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from app.core.config import settings
from app.engine.preprocessor import SentenceSpan, TextPreprocessor


@dataclass
class SentenceLexicalMatch:
    sentence_index: int
    matching_fingerprints: int
    total_fingerprints: int
    similarity: float
    matched_corpus_doc_id: Optional[str] = None
    matched_source_title: Optional[str] = None


@dataclass
class LexicalAnalysisResult:
    score_t1: float
    doc_fingerprints: List[Tuple[int, int]]
    matched_fingerprints: Set[int]
    sentence_matches: List[SentenceLexicalMatch] = field(default_factory=list)
    corpus_contributions: Dict[str, Dict[str, any]] = field(default_factory=dict)


class WinnowingLexicalEngine:
    """Implements the robust Winnowing Fingerprinting Algorithm for lexical plagiarism detection.
    
    Uses polynomial Rabin-Karp rolling hash and sliding window with rightmost tie-breaking
    as specified in SDD 3.2.1.
    """

    def __init__(
        self,
        k: Optional[int] = None,
        w: Optional[int] = None,
        base: int = 257,
        mod: int = 1_000_000_007,
    ):
        self.k = k or settings.WINNOWING_K_GRAM
        self.w = w or settings.WINNOWING_WINDOW_SIZE
        self.base = base
        self.mod = mod
        # Precompute base^(k-1) % mod for O(1) rolling hash step
        self.base_k_minus_1 = pow(self.base, self.k - 1, self.mod)

    def polynomial_hash(self, substring: str) -> int:
        """Computes Rabin-Karp polynomial hash directly: H = sum(c_i * base^(k-1-i)) % mod."""
        h = 0
        for char in substring:
            h = (h * self.base + ord(char)) % self.mod
        return (h % self.mod + self.mod) % self.mod

    def compute_kgram_hashes(self, text: str) -> List[Tuple[int, int]]:
        """Generates k-grams and calculates their polynomial rolling hashes.
        
        Returns list of (hash_value, start_position).
        """
        clean = TextPreprocessor.clean_for_lexical(text)
        n = len(clean)
        if n < self.k:
            if n > 0:
                # If text is shorter than k, compute single hash for whatever exists
                return [(self.polynomial_hash(clean), 0)]
            return []

        hashes: List[Tuple[int, int]] = []

        # 1. Compute first hash directly
        first_kgram = clean[:self.k]
        current_hash = self.polynomial_hash(first_kgram)
        hashes.append((current_hash, 0))

        # 2. Compute subsequent hashes using Rabin-Karp rolling update
        for i in range(1, n - self.k + 1):
            prev_char = ord(clean[i - 1])
            new_char = ord(clean[i + self.k - 1])

            # Rolling hash: H_next = ((H_prev - prev_char * base^(k-1)) * base + new_char) % mod
            current_hash = (
                (current_hash - prev_char * self.base_k_minus_1) * self.base + new_char
            ) % self.mod
            current_hash = (current_hash % self.mod + self.mod) % self.mod

            hashes.append((current_hash, i))

        return hashes

    def winnow(self, hashes: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Applies sliding window of size w to select minimum hashes.
        
        Tie-breaking rule: when identical minimum hash values occur in the window,
        select the rightmost occurrence (highest index position).
        """
        n = len(hashes)
        if n == 0:
            return []
        if n <= self.w:
            # If fewer hashes than window size, find minimum with rightmost tie-breaking
            min_val = hashes[0][0]
            min_tuple = hashes[0]
            for h_val, pos in hashes:
                if h_val <= min_val:  # Rightmost tie-breaking
                    min_val = h_val
                    min_tuple = (h_val, pos)
            return [min_tuple]

        fingerprints: List[Tuple[int, int]] = []
        last_selected_pos: Optional[int] = None

        for i in range(n - self.w + 1):
            window = hashes[i : i + self.w]
            min_val = window[0][0]
            min_tuple = window[0]

            for h_val, pos in window:
                if h_val <= min_val:  # Rightmost tie-breaking
                    min_val = h_val
                    min_tuple = (h_val, pos)

            if last_selected_pos != min_tuple[1]:
                fingerprints.append(min_tuple)
                last_selected_pos = min_tuple[1]

        return fingerprints

    def extract_fingerprints(self, text: str) -> List[Tuple[int, int]]:
        """End-to-end pipeline: cleans text, computes rolling k-gram hashes, and winnows them."""
        hashes = self.compute_kgram_hashes(text)
        return self.winnow(hashes)

    def calculate_containment(
        self,
        doc_fps: List[Tuple[int, int]],
        corpus_fps: Set[int],
    ) -> Tuple[float, Set[int]]:
        """Computes containment similarity: Score_T1 = (|FP_doc ∩ FP_corpus| / |FP_doc|) * 100%."""
        doc_hash_set = {h for h, _ in doc_fps}
        if not doc_hash_set:
            return 0.0, set()

        intersection = doc_hash_set.intersection(corpus_fps)
        containment = (len(intersection) / len(doc_hash_set)) * 100.0
        return round(min(100.0, max(0.0, containment)), 2), intersection

    def analyze_document(
        self,
        original_text: str,
        sentences: List[SentenceSpan],
        corpus_index: Dict[int, List[Dict[str, any]]],
    ) -> LexicalAnalysisResult:
        """Performs full Tier 1 analysis on document sentences against the corpus fingerprint index.
        
        Args:
            original_text: Whole document raw string
            sentences: Segmented SentenceSpan objects
            corpus_index: Mapping of fingerprint_hash -> list of {doc_id, title, category}
        """
        # Overall document fingerprints
        doc_fps = self.extract_fingerprints(original_text)
        all_corpus_hashes = set(corpus_index.keys())

        score_t1, matched_fps = self.calculate_containment(doc_fps, all_corpus_hashes)

        sentence_matches: List[SentenceLexicalMatch] = []
        corpus_hits: Dict[str, Dict[str, any]] = {}

        # Sentence-by-sentence analysis for fine-grained heatmap annotation
        for s in sentences:
            s_fps = self.extract_fingerprints(s.text)
            s_hashes = {h for h, _ in s_fps}
            if not s_hashes:
                continue

            s_matched = s_hashes.intersection(all_corpus_hashes)
            if not s_matched:
                continue

            sim_ratio = len(s_matched) / len(s_hashes)

            # Match criteria: at least 40% fingerprint containment or >= 3 identical fingerprints
            if sim_ratio >= 0.40 or len(s_matched) >= 3:
                # Find the most frequent matching corpus source for this sentence
                source_counts: Dict[str, int] = {}
                source_info: Dict[str, Dict[str, str]] = {}

                for h in s_matched:
                    for ref in corpus_index.get(h, []):
                        d_id = str(ref.get("doc_id", "corpus-doc"))
                        source_counts[d_id] = source_counts.get(d_id, 0) + 1
                        if d_id not in source_info:
                            source_info[d_id] = {
                                "title": ref.get("title", "Dokumen Korpus Pembanding"),
                                "category": ref.get("category", "Umum"),
                            }

                best_doc_id = max(source_counts, key=source_counts.get) if source_counts else None
                best_title = source_info[best_doc_id]["title"] if best_doc_id else "Korpus Pembanding"

                # Record match
                sentence_matches.append(SentenceLexicalMatch(
                    sentence_index=s.index,
                    matching_fingerprints=len(s_matched),
                    total_fingerprints=len(s_hashes),
                    similarity=round(min(1.0, sim_ratio), 2),
                    matched_corpus_doc_id=best_doc_id,
                    matched_source_title=best_title,
                ))

                # Track corpus document contribution
                if best_doc_id:
                    if best_doc_id not in corpus_hits:
                        corpus_hits[best_doc_id] = {
                            "corpus_doc_id": best_doc_id,
                            "title": best_title,
                            "category": source_info[best_doc_id]["category"],
                            "match_count": 0,
                        }
                    corpus_hits[best_doc_id]["match_count"] += len(s_matched)

        return LexicalAnalysisResult(
            score_t1=score_t1,
            doc_fingerprints=doc_fps,
            matched_fingerprints=matched_fps,
            sentence_matches=sentence_matches,
            corpus_contributions=corpus_hits,
        )
