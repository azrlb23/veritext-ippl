from __future__ import annotations

from unittest.mock import patch

from app.engine.evasion_guard import detect_style_shift_blocks, normalize_evasion
from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.tier2_indobert import IndoBertScorer
from app.engine.tier2_reranker import SemanticReranker
from app.engine.tier3_patterns import detect_sentence_ai_signals
from app.llm.funnel_judge import build_funnel_batches, evaluate_funnel_parallel


def _span(idx: int, text: str) -> SentenceSpan:
    return SentenceSpan(index=idx, text=text, start_char=0, end_char=len(text), word_count=len(text.split()))


def test_evasion_guard_normalizes_and_flags_zw_and_homoglyph():
    clean = "Sistem analisis teks akademik modern."
    zw_text = "Sis\u200btem ana\u200blisis teks aka\u200bdemik modern."
    cyr_text = "Sist\u0435m \u0430n\u0430lisis t\u0435ks ak\u0430d\u0435mik m\u043ed\u0435rn."

    assert normalize_evasion(zw_text) == clean
    assert normalize_evasion(cyr_text) == clean
    assert TextPreprocessor.clean_for_lexical(zw_text) == TextPreprocessor.clean_for_lexical(clean)
    assert TextPreprocessor.clean_for_lexical(cyr_text) == TextPreprocessor.clean_for_lexical(clean)

    zw_sigs = dict((k, sc) for k, sc, _ in detect_sentence_ai_signals(zw_text))
    cyr_sigs = dict((k, sc) for k, sc, _ in detect_sentence_ai_signals(cyr_text))
    assert zw_sigs["evasion_zw"] >= 0.90
    assert cyr_sigs["evasion_homoglyph"] >= 0.90


def test_wp_aisigns_chatbot_vague_buzzword_and_puffery():
    md_sigs = dict((k, sc) for k, sc, _ in detect_sentence_ai_signals("**Keamanan:** Sistem menerapkan enkripsi berlapis."))
    greet_sigs = dict((k, sc) for k, sc, _ in detect_sentence_ai_signals("Tentu, berikut adalah ringkasan metode penelitian."))
    assert md_sigs["chatbot_artifact"] == 0.95
    assert greet_sigs["chatbot_artifact"] == 0.95

    no_cite = detect_sentence_ai_signals("Para ahli berpendapat bahwa sistem ini efektif.")
    with_cite = detect_sentence_ai_signals("Para ahli berpendapat bahwa sistem ini efektif (Santoso, 2024).")
    assert dict((k, sc) for k, sc, _ in no_cite)["vague_attribution"] == 0.72
    assert "vague_attribution" not in {k for k, _, _ in with_cite}

    buzz_3 = detect_sentence_ai_signals("Pendekatan komprehensif dan holistik menghasilkan inovasi transformatif.")
    buzz_1 = detect_sentence_ai_signals("Pendekatan komprehensif diterapkan pada pengujian laboratorium.")
    assert dict((k, sc) for k, sc, _ in buzz_3)["ai_vocab_density"] == 0.76
    assert "ai_vocab_density" not in {k for k, _, _ in buzz_1}

    puff = detect_sentence_ai_signals("Inovasi ini meninggalkan warisan mendalam bagi dunia pendidikan.")
    assert dict((k, sc) for k, sc, _ in puff)["puffery"] == 0.74


def test_detect_style_shift_blocks_flags_repetitive_second_block():
    human_sents = [
        "Hujan turun sore ini.",
        "Kampus tampak sepi sekali.",
        "Kami duduk di kantin.",
        "Kopi panas terasa nikmat.",
        "Diskusi skripsi mulai ramai.",
        "Data survei belum lengkap.",
        "Dosen meminta revisi bab dua.",
        "Waktu pengumpulan tinggal seminggu.",
        "Rekan kelompok segera menyusul.",
        "Lampiran tabel perlu diperiksa.",
    ]
    ai_block = [
        f"Secara keseluruhan dapat disimpulkan bahwa optimalisasi sistem informasi akademik berbasis kecerdasan buatan memainkan peran krusial dalam meningkatkan efisiensi layanan evaluasi kualitas naskah ilmiah modern pada bagian ke-{i}."
        for i in range(12)
    ]
    spans = [_span(i, t) for i, t in enumerate(human_sents + ai_block)]
    flagged, hints = detect_style_shift_blocks(spans, block_size=10)

    assert any(idx >= 10 for idx in flagged)
    assert not any(idx < 10 for idx in flagged)
    assert len(hints) >= 1


def test_cross_lingual_accept_mask_uses_similarity_gate_without_indobert():
    pairs = [
        (
            "Sistem kecerdasan buatan ini mendeteksi kemiripan teks akademik secara akurat.",
            "This artificial intelligence system detects academic text similarity accurately.",
        ),
        (
            "Metode penelitian kualitatif berfokus pada wawancara mendalam terhadap responden.",
            "Quantitative financial modeling relies on stochastic differential equations.",
        ),
    ]
    with (
        patch.object(SemanticReranker, "score_pairs", return_value=[0.9, 0.9]),
        patch.object(IndoBertScorer, "accept_mask") as indobert_mock,
    ):
        mask = SemanticReranker.accept_mask(pairs, similarities=[0.85, 0.76])

    assert mask == [True, False]
    assert not indobert_mock.called


def test_build_funnel_batches_and_gray_zone_dual_judge():
    spans = [_span(i, f"Kalimat akademik nomor {i} membahas metodologi penelitian kuantitatif.") for i in range(80)]
    batches = build_funnel_batches(spans, priority_indices={10, 45, 75}, max_batches=3, batch_size=25)

    assert len(batches) == 3
    all_indices = {s.index for b in batches for s in b}
    assert {10, 45, 75}.issubset(all_indices)
    assert batches[0][0].index < 27 and batches[1][0].index >= 26 and batches[2][-1].index >= 75

    class _MockGateway:
        def _client_order(self):
            return [(object(), "Gemini"), (object(), "DeepSeek")]

        def evaluate_batch(self, batch, stage1_hints=None, skip_first=False):
            if skip_first:
                return {"ai_probability": 70.0, "suspicious_sentences": [{"sentence_index": batch[0].index, "reason": "AI", "anomaly_score": 0.8}]}, "DeepSeek"
            return {"ai_probability": 50.0, "suspicious_sentences": []}, "Gemini"

    res, evaluator = evaluate_funnel_parallel(_MockGateway(), spans, priority_indices={10, 45, 75})
    assert res is not None
    assert res["ai_probability"] == 60.0
    assert evaluator == "Gemini + DeepSeek"
