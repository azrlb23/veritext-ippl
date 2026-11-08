import math
import re
from dataclasses import dataclass, field
from typing import ClassVar

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
    sentence_anomalies: list[StylometricSentenceAnomaly] = field(default_factory=list)


class StylometricEngine:
    """Engine for stylometric syntax analysis and AI / LLM anomaly detection."""

    BURSTINESS_AI_THRESHOLD: float = 0.20

    AI_TRANSITION_MARKERS: ClassVar[list[str]] = [
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
        self.transition_regex = re.compile("|".join(self.AI_TRANSITION_MARKERS), re.IGNORECASE)

    def calculate_sentence_length_stats(
        self, sentences: list[SentenceSpan]
    ) -> tuple[float, float, float]:
        """Calculates Mean (mu), Standard Deviation (sigma), and Burstiness Metric."""
        valid_lengths = [s.word_count for s in sentences if not s.is_citation and s.word_count > 0]
        n = len(valid_lengths)
        if n < 2:
            mu = float(valid_lengths[0]) if n == 1 else 0.0
            return mu, 0.0, 0.0

        mu = sum(valid_lengths) / n
        sigma = math.sqrt(sum((x - mu) ** 2 for x in valid_lengths) / n)
        denom = sigma + mu
        burstiness = 0.0 if denom == 0.0 else (sigma - mu) / denom
        return round(mu, 2), round(sigma, 2), round(burstiness, 4)

    def calculate_type_token_ratio(self, original_text: str) -> tuple[float, int, int]:
        """Calculates Type-Token Ratio: TTR = Unique Words / Total Words."""
        tokens = TextPreprocessor.tokenize_words(original_text)
        if not tokens:
            return 0.0, 0, 0
        unique_words = len(set(tokens))
        return round(unique_words / len(tokens), 4), len(tokens), unique_words

    def analyze_document(
        self, original_text: str, sentences: list[SentenceSpan]
    ) -> StylometricAnalysisResult:
        """Executes full Tier 3 stylometric and AI anomaly evaluation."""
        if not sentences or not original_text.strip():
            return StylometricAnalysisResult(
                score_t3=0.0, burstiness=0.0, mean_sentence_length=0.0, std_sentence_length=0.0,
                type_token_ratio=0.0, total_words=0, unique_words=0, is_ai_monotonous=False,
            )

        mu, sigma, burstiness = self.calculate_sentence_length_stats(sentences)
        ttr, total_words, unique_words = self.calculate_type_token_ratio(original_text)

        burstiness_factor = 0.0
        if burstiness < self.burstiness_threshold:
            b_norm = (self.burstiness_threshold - burstiness) / (self.burstiness_threshold + 0.60)
            burstiness_factor = max(0.0, min(1.0, b_norm))

        matches = sum(1 for s in sentences if self.transition_regex.search(s.text))
        marker_factor = min(1.0, matches / max(1, len(sentences) * 0.25))

        clustered = sum(1 for s in sentences if not s.is_citation and abs(s.word_count - mu) <= 2.5)
        ratio = clustered / max(1, len(sentences))
        uniformity_factor = max(0.0, min(1.0, (ratio - 0.40) / 0.50)) if ratio > 0.40 else 0.0

        raw_score = burstiness_factor * 60.0 + uniformity_factor * 25.0 + marker_factor * 15.0
        score_t3 = round(min(100.0, max(0.0, raw_score)), 2)
        is_ai = burstiness < self.burstiness_threshold and score_t3 >= 35.0

        anomalies: list[StylometricSentenceAnomaly] = []
        for s in sentences:
            if s.is_citation:
                continue
            has_marker = bool(self.transition_regex.search(s.text))
            if (is_ai and abs(s.word_count - mu) <= 2.0) or has_marker:
                reason = "Pola transisi generatif AI terdeteksi" if has_marker else (
                    "Panjang kalimat monoton / seragam dengan irama sintaksis AI"
                )
                conf = max(0.70, score_t3 / 100.0) if has_marker else score_t3 / 100.0
                anomalies.append(StylometricSentenceAnomaly(
                    sentence_index=s.index, word_count=s.word_count,
                    anomaly_score=round(conf, 2), reason=reason,
                ))

        return StylometricAnalysisResult(
            score_t3=score_t3, burstiness=burstiness, mean_sentence_length=mu,
            std_sentence_length=sigma, type_token_ratio=ttr, total_words=total_words,
            unique_words=unique_words, is_ai_monotonous=is_ai, sentence_anomalies=anomalies,
        )
