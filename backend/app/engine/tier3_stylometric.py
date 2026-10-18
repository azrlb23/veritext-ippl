import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from app.engine.preprocessor import SentenceSpan, TextPreprocessor


@dataclass
class StylometricSentenceAnomaly:
    sentence_index: int
    word_count: int
    anomaly_score: float
    reason: str


@dataclass
class StylometricAnalysisResult:
    score_t3: float  # AI Anomaly Score (0.0 - 100.0%)
    burstiness: float
    mean_sentence_length: float
    std_sentence_length: float
    type_token_ratio: float
    total_words: int
    unique_words: int
    is_ai_monotonous: bool
    sentence_anomalies: List[StylometricSentenceAnomaly] = field(default_factory=list)


class StylometricEngine:
    """Engine for stylometric syntax analysis and AI / LLM anomaly detection.
    
    Measures Burstiness (variance and standard deviation of sentence lengths) and
    Type-Token Ratio (TTR) as specified in SDD 3.2.3.
    """

    # Monotonous burstiness threshold below which text is characteristic of AI generation
    BURSTINESS_AI_THRESHOLD: float = 0.20

    # Common synthetic / AI transition patterns in Indonesian and English
    AI_TRANSITION_MARKERS = [
        r"\bdalam era (?:digital|modern|globalisasi) ini\b",
        r"\bpenting untuk (?:dicatat|diingat|diperhatikan)\b",
        r"\bsecara keseluruhan dapat disimpulkan bahwa\b",
        r"\bmemainkan peran (?:penting|krusial|vital)\b",
        r"\bkesimpulannya,? dapat dikatakan bahwa\b",
        r"\bberdasarkan penjelasan di atas\b",
        r"\bsebagaimana telah disebutkan sebelumnya\b",
        r"\bhal ini menunjukkan bahwa\b",
        r"\bmoreover, it is crucial to note that\b",
        r"\bin summary, it can be concluded that\b",
        r"\bplays a pivotal role\b",
    ]

    def __init__(self, burstiness_threshold: float = 0.20):
        self.burstiness_threshold = burstiness_threshold
        self.transition_regex = re.compile(
            "|".join(self.AI_TRANSITION_MARKERS), re.IGNORECASE
        )

    def calculate_sentence_length_stats(
        self, sentences: List[SentenceSpan]
    ) -> Tuple[float, float, float]:
        """Calculates Mean (mu), Standard Deviation (sigma), and Burstiness Metric:
        
        Burstiness = (sigma - mu) / (sigma + mu)
        """
        valid_lengths = [s.word_count for s in sentences if not s.is_citation and s.word_count > 0]
        n = len(valid_lengths)

        if n < 2:
            mu = float(valid_lengths[0]) if n == 1 else 0.0
            return mu, 0.0, 0.0

        mu = sum(valid_lengths) / n
        variance = sum((x - mu) ** 2 for x in valid_lengths) / n
        sigma = math.sqrt(variance)

        denom = sigma + mu
        if denom == 0.0:
            burstiness = 0.0
        else:
            burstiness = (sigma - mu) / denom

        return round(mu, 2), round(sigma, 2), round(burstiness, 4)

    def calculate_type_token_ratio(self, original_text: str) -> Tuple[float, int, int]:
        """Calculates Type-Token Ratio: TTR = Unique Words / Total Words."""
        tokens = TextPreprocessor.tokenize_words(original_text)
        total_words = len(tokens)
        if total_words == 0:
            return 0.0, 0, 0

        unique_words = len(set(tokens))
        ttr = unique_words / total_words
        return round(ttr, 4), total_words, unique_words

    def analyze_document(
        self,
        original_text: str,
        sentences: List[SentenceSpan],
    ) -> StylometricAnalysisResult:
        """Executes full Tier 3 stylometric and AI anomaly evaluation."""
        if not sentences or not original_text.strip():
            return StylometricAnalysisResult(
                score_t3=0.0,
                burstiness=0.0,
                mean_sentence_length=0.0,
                std_sentence_length=0.0,
                type_token_ratio=0.0,
                total_words=0,
                unique_words=0,
                is_ai_monotonous=False,
            )

        mu, sigma, burstiness = self.calculate_sentence_length_stats(sentences)
        ttr, total_words, unique_words = self.calculate_type_token_ratio(original_text)

        # 1. Burstiness Component (AI texts have monotonous cadence, low burstiness < 0.20)
        # B is bounded in [-1.0, 1.0]. Lower values indicate severe monotonicity.
        if burstiness < self.burstiness_threshold:
            # Map burstiness from threshold (0.20) down to -0.60 to factor [0.0, 1.0]
            burstiness_factor = (self.burstiness_threshold - burstiness) / (self.burstiness_threshold + 0.60)
            burstiness_factor = max(0.0, min(1.0, burstiness_factor))
        else:
            burstiness_factor = 0.0

        # 2. Transition Marker Component
        transition_matches = 0
        for s in sentences:
            if self.transition_regex.search(s.text):
                transition_matches += 1

        marker_factor = min(1.0, transition_matches / max(1, len(sentences) * 0.25))

        # 3. Uniformity Component (fraction of sentences clustered within +/- 2 words of the mean)
        clustered_count = sum(
            1 for s in sentences
            if not s.is_citation and abs(s.word_count - mu) <= 2.5
        )
        uniformity_ratio = clustered_count / max(1, len(sentences))
        uniformity_factor = max(0.0, min(1.0, (uniformity_ratio - 0.40) / 0.50)) if uniformity_ratio > 0.40 else 0.0

        # Combine into overall AI Anomaly Score (0.0 - 100.0%)
        # 60% burstiness + 25% uniformity + 15% marker
        raw_score = (
            burstiness_factor * 60.0 +
            uniformity_factor * 25.0 +
            marker_factor * 15.0
        )
        score_t3 = round(min(100.0, max(0.0, raw_score)), 2)

        is_ai = burstiness < self.burstiness_threshold and score_t3 >= 35.0

        # Identify anomalous sentences for heatmap annotation
        sentence_anomalies: List[StylometricSentenceAnomaly] = []
        for s in sentences:
            if s.is_citation:
                continue

            has_marker = bool(self.transition_regex.search(s.text))
            is_clustered = abs(s.word_count - mu) <= 2.0

            if (is_ai and is_clustered) or has_marker:
                reason = "Pola transisi generatif AI terdeteksi" if has_marker else "Panjang kalimat monoton / seragam dengan irama sintaksis AI"
                confidence = score_t3 / 100.0 if not has_marker else max(0.70, score_t3 / 100.0)
                sentence_anomalies.append(StylometricSentenceAnomaly(
                    sentence_index=s.index,
                    word_count=s.word_count,
                    anomaly_score=round(confidence, 2),
                    reason=reason,
                ))

        return StylometricAnalysisResult(
            score_t3=score_t3,
            burstiness=burstiness,
            mean_sentence_length=mu,
            std_sentence_length=sigma,
            type_token_ratio=ttr,
            total_words=total_words,
            unique_words=unique_words,
            is_ai_monotonous=is_ai,
            sentence_anomalies=sentence_anomalies,
        )
