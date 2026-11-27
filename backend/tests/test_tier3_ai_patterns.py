from __future__ import annotations

from app.engine.preprocessor import SentenceSpan
from app.engine.tier3_patterns import detect_sentence_ai_signals, has_label_colon_pattern
from app.engine.tier3_stylometric import StylometricEngine
from app.llm.deepseek_client import DeepSeekRouterClient
from app.llm.gemini_client import GeminiFlashClient
from app.llm.gateway import DualEngineLLMGateway


def _span(idx: int, text: str) -> SentenceSpan:
    return SentenceSpan(
        index=idx,
        text=text,
        start_char=0,
        end_char=len(text),
        word_count=len(text.split()),
        is_citation=False,
    )


def test_em_dash_and_spaced_double_hyphen_detection() -> None:
    em_text = "Pendekatan ini — meskipun terlihat sederhana — mampu meningkatkan akurasi evaluasi secara menyeluruh."
    double_hyphen_text = "Sistem ini -- sebagaimana dirancang sebelumnya -- bekerja secara otomatis untuk memvalidasi dokumen."
    en_dash_range = "Penelitian ini dilakukan pada rentang tahun 2020\u20132024 di laboratorium komputer kampus."
    hyphen_word = "Aplikasi berbasis-web ini mempermudah mahasiswa memeriksa draf skripsi sebelum sidang akhir."

    em_signals = detect_sentence_ai_signals(em_text)
    assert any(k == "em_dash" and sc >= 0.75 for k, sc, _ in em_signals)

    dh_signals = detect_sentence_ai_signals(double_hyphen_text)
    assert any(k == "em_dash" and sc >= 0.75 for k, sc, _ in dh_signals)

    assert detect_sentence_ai_signals(en_dash_range) == []
    assert detect_sentence_ai_signals(hyphen_word) == []

    short_human = "Data dikumpulkan."
    long_human = (
        "Meskipun banyak kendala teknis yang muncul di lapangan saat tahap pengambilan sampel awal, "
        "seluruh tim peneliti tetap memvalidasi setiap instrumen ukur secara cermat dan berulang kali "
        "demi menjamin keabsahan temuan empiris dalam laporan penelitian akhir mahasiswa."
    )
    engine = StylometricEngine()
    res = engine.analyze_document(
        f"{em_text} {en_dash_range} {short_human} {long_human}",
        [_span(0, em_text), _span(1, en_dash_range), _span(2, short_human), _span(3, long_human)],
    )
    flagged = {a.sentence_index: a for a in res.sentence_anomalies}
    assert 0 in flagged and flagged[0].anomaly_score >= 0.75
    assert 1 not in flagged
    assert 3 not in flagged


def test_label_colon_pattern_positive_and_exclusions() -> None:
    pos_plain = "Keamanan Data: Sistem ini menerapkan enkripsi menyeluruh untuk melindungi seluruh berkas naskah akademik mahasiswa."
    pos_numbered = "1. Efisiensi Proses: Penerapan indeks vektor mempercepat pencarian kemiripan semantik pada korpus rujukan ilmiah."
    neg_figure = "Gambar 1: Arsitektur sistem deteksi plagiarisme hibrida empat lapis pada platform VeriText AI."
    neg_source = "Sumber: Data primer hasil kuesioner mahasiswa semester akhir tahun akademik berjalan di fakultas."
    neg_short = "Catatan Penting: Ringkasan singkat saja."
    neg_url = "https://veritext.id: Tautan portal verifikasi sertifikat digital resmi yang tersedia untuk seluruh pengguna."

    assert has_label_colon_pattern(pos_plain) is True
    assert has_label_colon_pattern(pos_numbered) is True
    assert has_label_colon_pattern(neg_figure) is False
    assert has_label_colon_pattern(neg_source) is False
    assert has_label_colon_pattern(neg_short) is False
    assert has_label_colon_pattern(neg_url) is False


def test_combined_structural_signals_merge_reasons_and_elevate_score() -> None:
    s0 = "Keamanan Data: Sistem ini — tanpa kompromi — menerapkan enkripsi berlapis untuk melindungi dokumen penelitian mahasiswa."
    s1 = "Efisiensi Arsitektur: Pendekatan modular ini tidak hanya mempercepat pemrosesan teks tetapi juga menjaga konsistensi hasil."
    s2 = "Peneliti menguji prototipe tersebut secara langsung."
    sentences = [_span(0, s0), _span(1, s1), _span(2, s2)]
    full_text = " ".join(s.text for s in sentences)

    engine = StylometricEngine()
    result = engine.analyze_document(full_text, sentences)

    assert result.score_t3 >= 35.0
    assert result.is_ai_monotonous is True

    by_idx = {a.sentence_index: a for a in result.sentence_anomalies}
    assert 0 in by_idx
    assert ";" in by_idx[0].reason
    assert "em-dash" in by_idx[0].reason.lower()
    assert "titik dua" in by_idx[0].reason.lower()
    assert by_idx[0].anomaly_score >= 0.80
    assert 1 in by_idx


def test_gateway_build_judge_prompt_includes_em_dash_and_label_colon_criteria() -> None:
    gateway = DualEngineLLMGateway(
        gemini_client=GeminiFlashClient(api_key="mock"),
        deepseek_client=DeepSeekRouterClient(api_key="mock"),
    )
    prompt = gateway.build_judge_prompt([_span(0, "Keamanan Data: Sistem ini — secara otomatis — memvalidasi integritas teks.")])

    assert "titik dua" in prompt
    assert "em-dash (\u2014)" in prompt
