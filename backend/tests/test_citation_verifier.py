from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx

from app.engine.bibliography_parser import parse_bibliography_entries
from app.engine.citation_verifier import CitationFinding, CitationVerifier
from app.engine.tier4_aggregator import HybridAggregator
from app.engine.tier4_annotation_builder import build_heatmap_annotations
from app.engine.preprocessor import SentenceSpan


def _mock_resp(status_code: int, payload: dict | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload or {}
    return resp


def test_parse_bibliography_extracts_entries_dois_and_respects_boundaries():
    doc = (
        "Bab 1 Pendahuluan.\nDaftar Pustaka\n"
        "Pembahasan ini merujuk pada literatur terkini.\n\n"
        "Daftar Pustaka\n"
        "[1] Santoso, B. (2022). Deep Learning for Indonesian NLP. Journal of AI, 10(2). https://doi.org/10.1234/ai.2022.01.\n"
        "[2] Wijaya, R. (2021). \"Deteksi Plagiarisme Berbasis Semantik\". Prosiding Nasional.\n\n"
        "Lampiran\n"
        "Data mentah penelitian."
    )
    entries = parse_bibliography_entries(doc)
    assert len(entries) == 2
    assert entries[0].doi == "10.1234/ai.2022.01"
    assert "Deep Learning for Indonesian NLP" in entries[0].title_query
    assert entries[0].raw_text == doc[entries[0].start_char : entries[0].end_char]
    assert entries[1].doi is None
    assert entries[1].title_query == "Deteksi Plagiarisme Berbasis Semantik"
    assert parse_bibliography_entries("Naskah biasa tanpa daftar rujukan.") == []


def test_verify_doi_handles_verified_mismatched_unverified_and_timeout():
    doc = (
        "References\n"
        "[1] Doe, J. (2023). Neural Machine Translation Survey. doi: 10.1000/valid.1\n"
        "[2] Doe, J. (2023). Quantum Cryptography Protocol. doi: 10.1000/mismatch.2\n"
        "[3] Fake, A. (2024). Hallucinated Paper Title. doi: 10.9999/fake.404\n"
    )
    entries = parse_bibliography_entries(doc)
    verifier = CitationVerifier(timeout_s=1.0, overall_timeout_s=5.0)

    def fake_get(url: str, **kwargs):
        if "10.1000/valid.1" in url:
            return _mock_resp(200, {"message": {"title": ["Neural Machine Translation Survey"]}})
        if "10.1000/mismatch.2" in url:
            return _mock_resp(200, {"message": {"title": ["Organic Chemistry of Marine Algae"]}})
        return _mock_resp(404)

    with patch("app.engine.citation_api_clients.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = fake_get
        findings = verifier.verify_entries(entries)

    assert [f.status for f in findings] == ["VERIFIED", "MISMATCHED_DOI", "UNVERIFIED"]
    assert findings[1].confidence_score == 0.90
    assert findings[2].confidence_score == 0.85

    with patch("app.engine.citation_api_clients.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.TimeoutException("timeout")
        timeout_findings = verifier.verify_entries(entries[:1])
    assert timeout_findings[0].status == "UNKNOWN"


def test_verify_by_search_distinguishes_verified_unverified_and_timeout():
    doc = "Daftar Pustaka\n[1] Budi, S. (2020). Sistem Deteksi Plagiarisme Semantik Indonesia. Jurnal Ilmu Komputer.\n"
    entries = parse_bibliography_entries(doc)
    verifier = CitationVerifier(timeout_s=1.0, overall_timeout_s=5.0)

    with patch("app.engine.citation_api_clients.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = [
            _mock_resp(200, {"message": {"items": [{"title": ["Sistem Deteksi Plagiarisme Semantik Indonesia"], "DOI": "10.1/ok"}]}}),
            _mock_resp(200, {"results": []}),
        ]
        ok_res = verifier.verify_entries(entries)
    assert ok_res[0].status == "VERIFIED"

    with patch("app.engine.citation_api_clients.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = [
            _mock_resp(200, {"message": {"items": [{"title": ["Unrelated Astronomy Observation"]}]}}),
            _mock_resp(200, {"results": []}),
        ]
        bad_res = verifier.verify_entries(entries)
    assert bad_res[0].status == "UNVERIFIED"


def test_tier4_merges_unverified_citations_and_respects_tier1_only():
    text = "Kalimat pembuka penelitian.\n\nDaftar Pustaka\n[1] Penulis, A. (2024). Judul Fiktif. doi: 10.9999/fake.1"
    start = text.index("[1]")
    finding = CitationFinding(
        raw_text=text[start:], start_char=start, end_char=len(text),
        doi="10.9999/fake.1", status="UNVERIFIED",
        reason="DOI 10.9999/fake.1 tidak ditemukan di Crossref maupun OpenAlex (indikasi sitasi fiktif)",
        confidence_score=0.85,
    )
    spans = [SentenceSpan(index=0, text="Kalimat pembuka penelitian.", start_char=0, end_char=27, word_count=3)]
    full_annos = build_heatmap_annotations(spans, [], {}, {}, {}, "FULL", 0.0, citation_findings=[finding])
    assert len(full_annos) == 1
    assert full_annos[0]["tier"] == "T3"
    assert full_annos[0]["color"] == "YELLOW"
    assert full_annos[0]["ai_flag"] is True
    assert full_annos[0]["source_title"] == "Verifikasi Sitasi Daftar Pustaka"

    t1_annos = build_heatmap_annotations(spans, [], {}, {}, {}, "TIER1_ONLY", 0.0, citation_findings=[finding])
    assert t1_annos == []

    mock_verifier = MagicMock()
    mock_verifier.verify_document.return_value = [finding]
    mock_ai = MagicMock()
    mock_ai.analyze_document.return_value = MagicMock(score_t3=0.0, sentence_anomalies=[])
    agg = HybridAggregator(ai_detector=mock_ai, citation_verifier=mock_verifier)
    with patch("app.engine.tier4_aggregator.scan_web_sources", return_value=([], True, None)):
        res = agg.run_pipeline(text, audit_depth="FULL")
    assert any(a.get("source_title") == "Verifikasi Sitasi Daftar Pustaka" for a in res.heatmap_annotations)


def test_rejects_partial_overlap_fabrication_and_falls_back_on_crossref_429():
    doc = (
        "VI. DAFTAR PUSTAKA\n"
        "Fiktif, C. 2024. Quantum Entanglement in Indonesian Batik Pattern Recognition? Journal of Imaginary Science.\n"
        "Vaswani, A. (2017). Attention Is All You Need. https://doi.org/10.48550/arXiv.1706.03762\n"
    )
    entries = parse_bibliography_entries(doc)
    assert len(entries) == 2
    assert entries[0].title_query == "Quantum Entanglement in Indonesian Batik Pattern Recognition"

    verifier = CitationVerifier(timeout_s=1.0, overall_timeout_s=5.0)
    with patch("app.engine.citation_api_clients.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = [
            _mock_resp(200, {"message": {"items": [{"title": ["Indonesian Batik Pattern Recognition Using Siamese Network with Triplet Loss"]}]}}),
            _mock_resp(200, {"results": []}),
        ]
        res_search = verifier.verify_entries([entries[0]])
    assert res_search[0].status == "UNVERIFIED"

    with patch("app.engine.citation_api_clients.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = [
            _mock_resp(429, {}),
            _mock_resp(200, {"title": "Attention Is All You Need"}),
        ]
        res_doi = verifier.verify_entries([entries[1]])
    assert res_doi[0].status == "VERIFIED"
