from __future__ import annotations

from app.engine.preprocessor import SentenceSpan
from app.engine.tier1_lexical import SentenceLexicalMatch
from app.engine.tier2_semantic import SentenceSemanticMatch
from app.engine.tier3_stylometric import StylometricSentenceAnomaly
from app.engine.tier4_annotation_builder import build_heatmap_annotations


def _span(idx: int, start: int, end: int, text: str) -> SentenceSpan:
    return SentenceSpan(index=idx, text=text, start_char=start, end_char=end, word_count=6, is_citation=False)


def test_t1_with_tier3_anomaly_keeps_red_and_sets_ai_flag():
    sentences = [
        _span(0, 0, 30, "Kalimat pertama cocok leksikal."),
        _span(1, 31, 62, "Kalimat kedua cocok leksikal saja."),
    ]
    t1 = {
        0: SentenceLexicalMatch(sentence_index=0, matching_fingerprints=5, total_fingerprints=6, similarity=0.9, matched_source_title="Korpus A"),
        1: SentenceLexicalMatch(sentence_index=1, matching_fingerprints=5, total_fingerprints=6, similarity=0.85, matched_source_title="Korpus B"),
    }
    t3 = {
        0: StylometricSentenceAnomaly(sentence_index=0, word_count=6, anomaly_score=0.88, reason="Pola transisi monoton khas AI"),
    }

    annotations = build_heatmap_annotations(
        sentences=sentences, web_matches=[], tier1_matched_indices=t1,
        tier2_matched_indices={}, tier3_anomalies_by_index=t3,
        audit_depth="FULL", score_t3=65.0,
    )

    assert len(annotations) == 2
    assert annotations[0]["tier"] == "T1"
    assert annotations[0]["color"] == "RED"
    assert annotations[0]["ai_flag"] is True
    assert annotations[0]["ai_reason"] == "Pola transisi monoton khas AI"
    assert "ai_flag" not in annotations[1]


def test_t2_and_t3_set_ai_flag_and_respect_audit_depth():
    sentences = [
        _span(0, 0, 25, "Kalimat parafrasa semantik."),
        _span(1, 26, 50, "Kalimat pola AI murni."),
    ]
    t2 = {
        0: SentenceSemanticMatch(sentence_index=0, similarity=0.82, matched_source_title="Jurnal Semantik"),
    }
    t3 = {
        0: StylometricSentenceAnomaly(sentence_index=0, word_count=6, anomaly_score=0.75, reason="Struktur kalimat generik LLM"),
        1: StylometricSentenceAnomaly(sentence_index=1, word_count=6, anomaly_score=0.91, reason="Diksi seragam terdeteksi AI"),
    }

    full_annos = build_heatmap_annotations(
        sentences=sentences, web_matches=[], tier1_matched_indices={},
        tier2_matched_indices=t2, tier3_anomalies_by_index=t3,
        audit_depth="FULL", score_t3=50.0,
    )
    assert full_annos[0]["color"] == "ORANGE"
    assert full_annos[0]["ai_flag"] is True
    assert full_annos[0]["ai_reason"] == "Struktur kalimat generik LLM"
    assert full_annos[1]["color"] == "YELLOW"
    assert full_annos[1]["ai_flag"] is True
    assert full_annos[1]["ai_reason"] == "Diksi seragam terdeteksi AI"

    t1_only_annos = build_heatmap_annotations(
        sentences=sentences, web_matches=[], tier1_matched_indices={},
        tier2_matched_indices=t2, tier3_anomalies_by_index=t3,
        audit_depth="TIER1_ONLY", score_t3=0.0,
    )
    assert len(t1_only_annos) == 1
    assert "ai_flag" not in t1_only_annos[0]
