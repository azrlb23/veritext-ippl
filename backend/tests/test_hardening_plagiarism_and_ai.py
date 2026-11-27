from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.core.config import settings
from app.engine.preprocessor import SentenceSpan
from app.engine.tier1_filters import (
    has_lexical_evidence,
    is_heading_or_too_short,
    pick_best_matching_snippet,
)
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_reranker import SemanticReranker
from app.engine.tier3_patterns import detect_sentence_ai_signals
from app.engine.tier3_stylometric import StylometricEngine
from app.engine.web_snippet_verifier import verify_snippet_cross_check
from app.llm.gateway import DualEngineLLMGateway, _select_stratified_sample


def _span(idx: int, text: str) -> SentenceSpan:
    return SentenceSpan(idx, text, 0, len(text), len(text.split()), is_citation=False)


def test_tier1_has_lexical_evidence_rejects_scattered_and_accepts_contiguous():
    src = "Implementasi algoritma pengawasan kualitas udara perkotaan menggunakan sensor berbasis mikrokontroler modern."
    scattered = "Pengawasan terhadap kondisi perkotaan modern dapat dilakukan dengan berbagai metode observasi lapangan."
    contiguous = "Sistem pengawasan kualitas udara perkotaan dibangun untuk pemantauan waktu nyata."
    assert has_lexical_evidence(src, scattered) is False
    assert has_lexical_evidence(src, contiguous) is True


def test_tier1_skips_academic_boilerplate_and_picks_best_snippet():
    meta = "Bab ini membahas latar belakang masalah secara garis besar untuk penelitian ini."
    assert is_heading_or_too_short(meta) is True

    query = "Evaluasi model klasifikasi sentimen menggunakan arsitektur transformer pada ulasan produk."
    abstract = (
        "Penelitian terdahulu berfokus pada metode statistik sederhana untuk survei kepuasan pelanggan. "
        "Studi ini melakukan evaluasi model klasifikasi sentimen menggunakan arsitektur transformer pada ulasan produk lokal. "
        "Kesimpulan akhir menunjukkan peningkatan akurasi dibandingkan metode dasar."
    )
    best = pick_best_matching_snippet(query, abstract)
    assert "arsitektur transformer pada ulasan produk" in best


def test_web_verifier_rejects_loose_topic_and_accepts_t1_and_t2():
    lex = WinnowingLexicalEngine()
    sem = MagicMock()
    sem.embed_sentence.side_effect = lambda t: [1.0, 0.0] if "padi" in t else [0.0, 1.0]
    sem.cosine_similarity.side_effect = lambda a, b: 0.85 if a == b else 0.30

    query = "Deteksi penyakit daun padi menggunakan jaringan saraf konvolusional pada citra lapangan."
    loose = "Pertanian presisi membantu petani mengelola irigasi sawah secara berkelanjutan sepanjang musim."
    verbatim = "Penelitian deteksi penyakit daun padi menggunakan jaringan saraf konvolusional menunjukkan akurasi tinggi."
    paraphrase = "Identifikasi gangguan tanaman padi berbasis citra digital dilakukan memakai arsitektur deep learning."

    with patch.object(SemanticReranker, "accept_mask", return_value=[True]):
        _, _, ok_loose, tier_loose = verify_snippet_cross_check(query, loose, lex, sem)
        _, _, ok_t1, tier_t1 = verify_snippet_cross_check(query, verbatim, lex, sem)
        _, _, ok_t2, tier_t2 = verify_snippet_cross_check(query, paraphrase, lex, sem)

    assert (ok_loose, tier_loose) == (False, "")
    assert (ok_t1, tier_t1) == (True, "T1")
    assert (ok_t2, tier_t2) == (True, "T2")


def test_tier3_consecutive_label_colon_and_triad_signals():
    s0 = _span(0, "Keamanan Sistem: Seluruh jalur komunikasi data dienkripsi memakai protokol standar industri modern.")
    s1 = _span(1, "Kalimat penghubung singkat antara dua poin.")
    s2 = _span(2, "Skalabilitas Layanan: Arsitektur terdistribusi memastikan beban trafik tinggi tetap tertangani dengan stabil.")
    res = StylometricEngine().analyze_document(" ".join(s.text for s in (s0, s1, s2)), [s0, s1, s2])
    by_idx = {a.sentence_index: a for a in res.sentence_anomalies}
    assert by_idx[0].anomaly_score >= 0.90
    assert "Rangkaian pola label-titik dua beruntun khas AI" in by_idx[0].reason
    assert by_idx[2].anomaly_score >= 0.90

    triad_sigs = detect_sentence_ai_signals("Platform ini dirancang agar bekerja secara cepat, aman, dan efisien bagi pengguna.")
    assert any(k == "triad" for k, _, _ in triad_sigs)


def test_tier3_sliding_window_flags_monotonous_ai_block_in_mixed_document():
    mixed = [
        _span(0, "Hujan turun deras."),
        _span(1, "Banyak peneliti mencatat variasi pola penulisan manusia sering melompat antara ungkapan singkat hingga pemaparan panjang berlapis kompleks."),
        _span(2, "Sistem pemantauan kualitas udara berbasis sensor nirkabel mengirim data menuju server pusat."),
        _span(3, "Perangkat lunak analisis memproses seluruh sinyal masukan secara berkala setiap lima menit."),
        _span(4, "Basis data relasional menyimpan rekaman pengukuran suhu lingkungan untuk keperluan evaluasi lanjutan."),
        _span(5, "Antarmuka web menampilkan grafik perubahan konsentrasi partikel udara kepada para pengelola kota."),
        _span(6, "Modul peringatan dini mengirimkan notifikasi otomatis ketika ambang batas aman mulai terlampaui."),
        _span(7, "Catatan lapangan selesai."),
        _span(8, "Namun pengamatan langsung di lokasi industri memperlihatkan anomali pembacaan sensor akibat debu tebal."),
    ]
    res = StylometricEngine().analyze_document(" ".join(s.text for s in mixed), mixed)
    by_idx = {a.sentence_index: a for a in res.sentence_anomalies}
    for idx in range(2, 7):
        assert idx in by_idx
        assert "Blok paragraf monoton dengan ritme kalimat seragam khas AI" in by_idx[idx].reason


def test_llm_gateway_stratified_sample_covers_start_middle_and_end():
    sentences = [_span(i, f"Kalimat uji nomor {i} memiliki panjang kata cukup.") for i in range(100)]
    sample = _select_stratified_sample(sentences, 12)
    sample_indices = [s.index for s in sample]
    assert sample_indices[0] == 0
    assert sample_indices[-1] == 99
    assert any(40 <= idx <= 60 for idx in sample_indices)

    captured: list[str] = []
    mock_client = MagicMock()
    mock_client.model = "mock-llm"

    def _capture(prompt: str):
        captured.append(prompt)
        return {"ai_probability": 25.0, "suspicious_sentences": []}

    mock_client.generate_json.side_effect = _capture
    gateway = DualEngineLLMGateway(deepseek_client=mock_client, strategy="deepseek_first")
    with patch.object(settings, "WEB_SCAN_MAX_SENTENCES", 12):
        result, _ = gateway.evaluate_sentences(sentences)

    assert result is not None
    assert "[0]" in captured[0]
    assert "[99]" in captured[0]
    assert any(f"[{idx}]" in captured[0] for idx in range(40, 61))
