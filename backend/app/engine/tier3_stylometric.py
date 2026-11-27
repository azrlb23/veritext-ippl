import math
import re
from dataclasses import dataclass, field
from typing import ClassVar

from app.engine.evasion_guard import detect_style_shift_blocks
from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.tier3_patterns import AI_TRANSITION_MARKERS, detect_sentence_ai_signals


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
    stage1_hints: list[str] = field(default_factory=list)


def _escalate_consecutive_labels(
    valid_spans: list[SentenceSpan], sigs: dict[int, list[tuple[str, float, str]]]
) -> None:
    labeled = [
        (pos, s.index) for pos, s in enumerate(valid_spans)
        if any(k == "label_colon" for k, _, _ in sigs.get(s.index, []))
    ]
    escalated = {
        idx_a for i, (pos_a, idx_a) in enumerate(labeled)
        for j, (pos_b, idx_b) in enumerate(labeled)
        if i != j and (abs(idx_a - idx_b) <= 2 or abs(pos_a - pos_b) <= 2)
    }
    prefix = "Rangkaian pola label-titik dua beruntun khas AI"
    for idx in escalated:
        sigs[idx] = [
            ("label_colon", 0.90, f"{prefix}: {r}") if k == "label_colon" else (k, sc, r)
            for k, sc, r in sigs[idx]
        ]


def _build_stage1_hints(
    sigs: dict[int, list[tuple[str, float, str]]], win_cnt: int, shift_hints: list[str]
) -> list[str]:
    all_keys = [{k for k, _, _ in items} for items in sigs.values()]
    rules = [
        ({"evasion_zw", "evasion_homoglyph"}, "Evasion guard: {n} kalimat mengandung zero-width/homoglyph"),
        ({"chatbot_artifact"}, "Artefak chatbot/Markdown terdeteksi pada {n} kalimat"),
        ({"em_dash"}, "Penggunaan em-dash (—) pada {n} kalimat"),
        ({"label_colon"}, "Pola label-titik dua terdeteksi pada {n} kalimat"),
        ({"vague_attribution", "ai_vocab_density", "puffery"}, "Indikator WP:AISIGNS (atribusi kabur/klise/puffery) pada {n} kalimat"),
    ]
    hints = [tpl.format(n=cnt) for key_set, tpl in rules if (cnt := sum(bool(ks & key_set) for ks in all_keys))]
    if win_cnt:
        hints.append(f"Ritme monoton terdeteksi pada {win_cnt} kalimat dalam jendela lokal")
    return (hints + shift_hints)[:6]


class StylometricEngine:
    """Engine for stylometric syntax analysis and AI / LLM anomaly detection."""

    BURSTINESS_AI_THRESHOLD: float = 0.20
    AI_TRANSITION_MARKERS: ClassVar[list[str]] = AI_TRANSITION_MARKERS

    def __init__(self, burstiness_threshold: float = 0.20):
        self.burstiness_threshold = burstiness_threshold
        self.transition_regex = re.compile("|".join(self.AI_TRANSITION_MARKERS), re.IGNORECASE)

    def calculate_sentence_length_stats(self, sentences: list[SentenceSpan]) -> tuple[float, float, float]:
        """Calculates Mean (mu), Standard Deviation (sigma), and Burstiness Metric."""
        valid = [s.word_count for s in sentences if not s.is_citation and s.word_count > 0]
        if len(valid) < 2:
            return (float(valid[0]) if valid else 0.0), 0.0, 0.0
        mu = sum(valid) / len(valid)
        sigma = math.sqrt(sum((x - mu) ** 2 for x in valid) / len(valid))
        denom = sigma + mu
        return round(mu, 2), round(sigma, 2), round(0.0 if denom == 0.0 else (sigma - mu) / denom, 4)

    def calculate_type_token_ratio(self, original_text: str) -> tuple[float, int, int]:
        """Calculates Type-Token Ratio: TTR = Unique Words / Total Words."""
        tokens = TextPreprocessor.tokenize_words(original_text)
        if not tokens:
            return 0.0, 0, 0
        uniq = len(set(tokens))
        return round(uniq / len(tokens), 4), len(tokens), uniq

    def analyze_document(self, original_text: str, sentences: list[SentenceSpan]) -> StylometricAnalysisResult:
        """Executes full Tier 3 stylometric and AI structural anomaly evaluation."""
        if not sentences or not original_text.strip():
            return StylometricAnalysisResult(0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, False)
        mu, sigma, burstiness = self.calculate_sentence_length_stats(sentences)
        ttr, total_words, unique_words = self.calculate_type_token_ratio(original_text)
        b_norm = (self.burstiness_threshold - burstiness) / (self.burstiness_threshold + 0.60)
        b_factor = max(0.0, min(1.0, b_norm)) if burstiness < self.burstiness_threshold else 0.0
        valid_spans = [s for s in sentences if not s.is_citation and s.word_count > 0]
        sentence_signals: dict[int, list[tuple[str, float, str]]] = {}
        marker_hits = structural_hits = 0
        for s in valid_spans:
            if signals := detect_sentence_ai_signals(s.text):
                sentence_signals[s.index] = signals
                keys = {k for k, _, _ in signals}
                marker_hits += int("transition" in keys)
                structural_hits += int("em_dash" in keys or "label_colon" in keys)
        _escalate_consecutive_labels(valid_spans, sentence_signals)
        local_window_indices: set[int] = set()
        for i in range(max(0, len(valid_spans) - 4)):
            win = valid_spans[i : i + 5]
            l_mu, l_sigma, l_burst = self.calculate_sentence_length_stats(win)
            if l_burst < 0.12 and l_sigma <= 2.5 and l_mu >= 10.0:
                local_window_indices.update(s.index for s in win)
        shift_indices, shift_hints = detect_style_shift_blocks(valid_spans)
        valid_count = max(1, len(valid_spans))
        marker_f = min(1.0, marker_hits / max(1, len(sentences) * 0.25))
        struct_f = min(1.0, structural_hits / max(1.0, len(sentences) * 0.15))
        win_f = min(1.0, len(local_window_indices) / valid_count)
        ratio = sum(1 for s in valid_spans if abs(s.word_count - mu) <= 2.5) / valid_count
        unif_f = max(0.0, min(1.0, (ratio - 0.40) / 0.50)) if ratio > 0.40 else 0.0
        score_t3 = round(min(100.0, max(0.0, b_factor * 50.0 + unif_f * 20.0 + marker_f * 15.0 + struct_f * 30.0 + win_f * 15.0)), 2)
        is_ai = score_t3 >= 35.0 and (burstiness < self.burstiness_threshold or structural_hits >= 2 or bool(local_window_indices))
        anomalies: list[StylometricSentenceAnomaly] = []
        for s in valid_spans:
            if signals := sentence_signals.get(s.index):
                sc, reason = round(max(max(v for _, v, _ in signals), score_t3 / 100.0), 2), "; ".join(r for _, _, r in signals[:2])
            elif s.index in local_window_indices:
                sc, reason = round(max(0.70, score_t3 / 100.0), 2), "Blok paragraf monoton dengan ritme kalimat seragam khas AI"
            elif s.index in shift_indices:
                sc, reason = round(max(0.72, score_t3 / 100.0), 2), "Pergeseran gaya bahasa (style-shift) dan repetisi struktural mencolok dibanding bagian lain naskah"
            elif is_ai and abs(s.word_count - mu) <= 2.0:
                sc, reason = round(score_t3 / 100.0, 2), "Panjang kalimat monoton / seragam dengan irama sintaksis AI"
            else:
                continue
            anomalies.append(StylometricSentenceAnomaly(s.index, s.word_count, sc, reason))
        hints = _build_stage1_hints(sentence_signals, len(local_window_indices), shift_hints)
        return StylometricAnalysisResult(score_t3, burstiness, mu, sigma, ttr, total_words, unique_words, is_ai, anomalies, hints)
