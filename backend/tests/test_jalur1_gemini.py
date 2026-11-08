from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import httpx

from app.core.config import settings
from app.engine.ai_detector import GeminiAIDetector
from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.tier4_aggregator import HybridAggregator
from app.engine.web_scanner import GeminiWebScanner, WebMatchResult


class TestJalur1GeminiAIAndWebScanner(unittest.TestCase):
    """Pengujian Komprehensif Jalur 1: Detektor AI Gemini Flash & Pemindai Plagiarisme Web Publik."""

    def setUp(self):
        GeminiWebScanner.clear_cache()
        self.preprocessor = TextPreprocessor()

    def tearDown(self):
        GeminiWebScanner.clear_cache()

    # =========================================================================
    # 1. TEST SUITE: GeminiAIDetector
    # =========================================================================

    def test_gemini_ai_detector_happy_path(self):
        """Detektor AI Gemini berhasil mem-parse JSON response dan menghasilkan skor hybrid."""
        mock_response_data = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{\n  "ai_probability": 88.0,\n  "suspicious_sentences": [\n    {\n      "sentence_index": 0,\n      "reason": "Struktur transisi AI monoton",\n      "anomaly_score": 0.92\n    }\n  ]\n}'
                            }
                        ]
                    }
                }
            ]
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response_data

        detector = GeminiAIDetector(api_key="test-key-mock", model="gemini-2.0-flash", openrouter_key="")

        sentences = [
            SentenceSpan(index=0, text="Dalam era digital ini, kecerdasan buatan memainkan peran krusial bagi kehidupan.", start_char=0, end_char=80, word_count=12, is_citation=False),
            SentenceSpan(index=1, text="Penelitian ini menggunakan metodologi studi kasus kualitatif di lapangan.", start_char=81, end_char=153, word_count=9, is_citation=False),
        ]
        doc_text = "Dalam era digital ini, kecerdasan buatan memainkan peran krusial bagi kehidupan. Penelitian ini menggunakan metodologi studi kasus kualitatif di lapangan."

        with patch("httpx.Client.post", return_value=mock_resp):
            result = detector.analyze_document(original_text=doc_text, sentences=sentences)

        self.assertGreater(result.score_t3, 50.0)
        self.assertTrue(result.is_ai_monotonous)
        self.assertTrue(any(a.sentence_index == 0 for a in result.sentence_anomalies))
        first_anomaly = next(a for a in result.sentence_anomalies if a.sentence_index == 0)
        self.assertIn("Struktur transisi AI monoton", first_anomaly.reason)
        self.assertGreaterEqual(first_anomaly.anomaly_score, 0.90)

    def test_openrouter_ai_detector_happy_path(self):
        """Detektor AI OpenRouter (Nemotron/Qwen) berhasil mem-parse JSON response OpenAI-compatible format."""
        mock_response_data = {
            "choices": [
                {
                    "message": {
                        "content": '{\n  "ai_probability": 85.0,\n  "suspicious_sentences": [\n    {\n      "sentence_index": 0,\n      "reason": "Frasa transisi khas LLM",\n      "anomaly_score": 0.90\n    }\n  ]\n}'
                    }
                }
            ]
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response_data

        detector = GeminiAIDetector(openrouter_key="mock-openrouter-key", openrouter_model="nvidia/nemotron-3.5-lightning:free")

        sentences = [
            SentenceSpan(index=0, text="Dalam era modern ini, kecerdasan buatan telah mengubah paradigma komputasi.", start_char=0, end_char=75, word_count=10, is_citation=False),
            SentenceSpan(index=1, text="Kami melakukan observasi langsung selama tiga hari di laboratorium.", start_char=76, end_char=143, word_count=9, is_citation=False),
        ]
        doc_text = "Dalam era modern ini, kecerdasan buatan telah mengubah paradigma komputasi. Kami melakukan observasi langsung selama tiga hari di laboratorium."

        with patch("httpx.Client.post", return_value=mock_resp):
            result = detector.analyze_document(original_text=doc_text, sentences=sentences)

        self.assertGreater(result.score_t3, 50.0)
        self.assertTrue(result.is_ai_monotonous)
        self.assertTrue(any(a.sentence_index == 0 for a in result.sentence_anomalies))
        first_anomaly = next(a for a in result.sentence_anomalies if a.sentence_index == 0)
        self.assertIn("Frasa transisi khas LLM", first_anomaly.reason)

    def test_gemini_ai_detector_fallback_on_empty_api_key(self):
        """Jika GEMINI_API_KEY dan OPENROUTER_API_KEY kosong, detektor otomatis fallback ke stilometri lokal tanpa error."""
        detector = GeminiAIDetector(api_key="", model="gemini-2.0-flash", openrouter_key="")
        sentences = [
            SentenceSpan(index=0, text="Kalimat pembuka sederhana dari mahasiswa asli.", start_char=0, end_char=46, word_count=6, is_citation=False),
        ]
        doc_text = "Kalimat pembuka sederhana dari mahasiswa asli."

        # Tidak boleh melempar error dan harus mengembalikan StylometricAnalysisResult
        result = detector.analyze_document(original_text=doc_text, sentences=sentences)
        self.assertIsNotNone(result)
        self.assertIsInstance(result.score_t3, float)

    def test_gemini_ai_detector_fallback_on_network_timeout(self):
        """Jika request timeout, detektor otomatis fallback ke stilometri lokal."""
        detector = GeminiAIDetector(api_key="valid-mock-key", model="gemini-2.0-flash")
        sentences = [
            SentenceSpan(index=0, text="Kalimat analisis dokumen yang sedang diuji.", start_char=0, end_char=43, word_count=6, is_citation=False),
        ]
        doc_text = "Kalimat analisis dokumen yang sedang diuji."

        with patch("httpx.Client.post", side_effect=httpx.TimeoutException("Mocked timeout")):
            result = detector.analyze_document(original_text=doc_text, sentences=sentences)

        self.assertIsNotNone(result)
        self.assertIsInstance(result.score_t3, float)

    def test_gemini_ai_detector_handles_markdown_code_fences(self):
        """Detektor AI mampu mem-parse JSON yang terbungkus code block markdown ```json ... ```."""
        mock_response_data = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "```json\n{\n  \"ai_probability\": 72.5,\n  \"suspicious_sentences\": []\n}\n```"
                            }
                        ]
                    }
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response_data

        detector = GeminiAIDetector(api_key="test-key-mock")
        sentences = [
            SentenceSpan(index=0, text="Studi kasus perancangan arsitektur mikrolayanan.", start_char=0, end_char=48, word_count=6, is_citation=False),
        ]

        with patch("httpx.Client.post", return_value=mock_resp):
            raw_res = detector.detect_gemini(sentences)

        self.assertIsNotNone(raw_res)
        self.assertEqual(raw_res["ai_probability"], 72.5)

    # =========================================================================
    # 2. TEST SUITE: GeminiWebScanner
    # =========================================================================

    def test_gemini_web_scanner_sentence_filtering(self):
        """Pemindai web mengabaikan sitasi, judul bab, dan kalimat terlalu pendek (<6 kata)."""
        scanner = GeminiWebScanner(api_key="test-key")

        s_citation = SentenceSpan(index=0, text="Smith et al. (2023) menyatakan hasil uji.", start_char=0, end_char=42, word_count=7, is_citation=True)
        s_short = SentenceSpan(index=1, text="Uji coba sistem.", start_char=43, end_char=59, word_count=3, is_citation=False)
        s_heading = SentenceSpan(index=2, text="BAB 1 PENDAHULUAN DAN LATAR BELAKANG", start_char=60, end_char=96, word_count=6, is_citation=False)
        s_valid = SentenceSpan(index=3, text="Algoritma machine learning dapat diterapkan untuk mengklasifikasikan dokumen secara otomatis.", start_char=97, end_char=191, word_count=10, is_citation=False)

        self.assertFalse(scanner._is_meaningful_sentence(s_citation))
        self.assertFalse(scanner._is_meaningful_sentence(s_short))
        self.assertFalse(scanner._is_meaningful_sentence(s_heading))
        self.assertTrue(scanner._is_meaningful_sentence(s_valid))

    def test_gemini_web_scanner_cross_check_anti_hallucination(self):
        """Verifikasi silang lokal menolak kutipan yang tidak relevan (halusinasi) dan menerima yang cocok."""
        scanner = GeminiWebScanner(api_key="test-key")

        sentence = "Pancasila adalah dasar filsafat negara Republik Indonesia yang resmi ditetapkan pada tahun 1945."

        # Kasus A: Cuplikan verbatim tinggi dari Wikipedia (harus Tier 1)
        snippet_verbatim = "Pancasila merupakan dasar filsafat negara Republik Indonesia yang ditetapkan pada tanggal 18 Agustus 1945."
        lex, _sem, is_ok, tier = scanner.verify_snippet_cross_check(sentence, snippet_verbatim)
        self.assertTrue(is_ok)
        self.assertEqual(tier, "T1")
        self.assertGreaterEqual(lex, 0.60)

        # Kasus B: Cuplikan parafrasa semantik (harus Tier 2)
        snippet_paraphrase = "Falsafah landasan negara Republik Indonesia secara sah disahkan pada tahun 1945."
        _lex2, _sem2, is_ok2, tier2 = scanner.verify_snippet_cross_check(sentence, snippet_paraphrase)
        self.assertTrue(is_ok2)
        self.assertEqual(tier2, "T2")

        # Kasus C: Cuplikan sama sekali tidak berkaitan (halusinasi LLM) -> harus ditolak
        snippet_unrelated = "Resep memasak rendang daging sapi khas Minangkabau dengan santan kental dan rempah pilihan."
        _lex3, _sem3, is_ok3, tier3 = scanner.verify_snippet_cross_check(sentence, snippet_unrelated)
        self.assertFalse(is_ok3)
        self.assertEqual(tier3, "")

    def test_gemini_web_scanner_scan_with_caching(self):
        """Pemindai web menyimpan hasil ke cache sehingga kalimat identik tidak memanggil API berulang."""
        scanner = GeminiWebScanner(api_key="test-key")

        mock_gemini_return = [
            {
                "sentence_index": 0,
                "source_title": "Wikipedia Ensiklopedia Bebas",
                "source_url": "https://id.wikipedia.org/wiki/Pancasila",
                "matched_snippet": "Pancasila adalah dasar filsafat negara Republik Indonesia yang resmi.",
            }
        ]

        sentences = [
            SentenceSpan(
                index=0,
                text="Pancasila adalah dasar filsafat negara Republik Indonesia yang resmi.",
                start_char=0,
                end_char=70,
                word_count=9,
                is_citation=False,
            )
        ]

        with patch.object(scanner, "_call_gemini_search", return_value=mock_gemini_return) as mock_call:
            # Panggilan pertama: harus memanggil Gemini
            res1 = scanner.scan(sentences)
            self.assertEqual(len(res1), 1)
            self.assertEqual(res1[0].source_url, "https://id.wikipedia.org/wiki/Pancasila")
            self.assertEqual(mock_call.call_count, 1)

            # Panggilan kedua dengan kalimat yang sama: harus dilayani oleh cache!
            res2 = scanner.scan(sentences)
            self.assertEqual(len(res2), 1)
            self.assertEqual(mock_call.call_count, 1)  # Tidak bertambah!

    def test_gemini_web_scanner_fallback_when_disabled(self):
        """Jika WEB_SCAN_ENABLED bernilai False atau key kosong, mengembalikan list kosong dengan aman."""
        with patch.object(settings, "WEB_SCAN_ENABLED", False):
            scanner = GeminiWebScanner(api_key="valid-key")
            sentences = [
                SentenceSpan(index=0, text="Kalimat panjang yang diuji pada pemindaian web dokumen.", start_char=0, end_char=54, word_count=8, is_citation=False)
            ]
            res = scanner.scan(sentences)
            self.assertEqual(res, [])

    # =========================================================================
    # 3. TEST SUITE: HybridAggregator Integration with Jalur 1
    # =========================================================================

    def test_hybrid_aggregator_integrates_web_matches_and_ai(self):
        """HybridAggregator berhasil menggabungkan temuan web publik dan evaluasi AI ke dalam anotasi heatmap & matched sources."""
        mock_web_matches = [
            WebMatchResult(
                sentence_index=0,
                similarity=0.95,
                source_url="https://id.wikipedia.org/wiki/Kecerdasan_buatan",
                source_title="Kecerdasan Buatan - Wikipedia",
                matched_snippet="Kecerdasan buatan adalah kecerdasan yang ditambahkan kepada suatu sistem yang bisa diatur.",
                tier="T1",
            )
        ]

        mock_web_scanner = MagicMock()
        mock_web_scanner.scan.return_value = mock_web_matches

        mock_ai_detector = MagicMock()
        from app.engine.tier3_stylometric import (
            StylometricAnalysisResult,
            StylometricSentenceAnomaly,
        )
        mock_ai_detector.analyze_document.return_value = StylometricAnalysisResult(
            score_t3=60.0,
            burstiness=0.15,
            mean_sentence_length=12.0,
            std_sentence_length=1.5,
            type_token_ratio=0.55,
            total_words=24,
            unique_words=14,
            is_ai_monotonous=True,
            sentence_anomalies=[
                StylometricSentenceAnomaly(
                    sentence_index=1,
                    word_count=12,
                    anomaly_score=0.85,
                    reason="Transisi AI monoton terdeteksi",
                )
            ],
        )

        aggregator = HybridAggregator(
            ai_detector=mock_ai_detector,
            web_scanner=mock_web_scanner,
        )

        text = (
            "Kecerdasan buatan adalah kecerdasan yang ditambahkan kepada suatu sistem yang bisa diatur. "
            "Dalam era digital modern ini, penting untuk dicatat bahwa teknologi memainkan peran penting."
        )

        result = aggregator.run_pipeline(original_text=text, audit_depth="FULL")

        self.assertGreater(len(result.heatmap_annotations), 0)
        self.assertGreater(result.score_composite, 0.0)

        # Cek apakah anotasi web memiliki source_url
        web_anno = next((a for a in result.heatmap_annotations if a.get("source_url")), None)
        self.assertIsNotNone(web_anno)
        self.assertEqual(web_anno["source_url"], "https://id.wikipedia.org/wiki/Kecerdasan_buatan")
        self.assertEqual(web_anno["tier"], "T1")

        # Cek apakah matched_sources mencantumkan sumber internet publik beserta link
        matched_web_source = next((s for s in result.matched_sources if s.get("source_url")), None)
        self.assertIsNotNone(matched_web_source)
        self.assertEqual(matched_web_source["source_url"], "https://id.wikipedia.org/wiki/Kecerdasan_buatan")
        self.assertEqual(matched_web_source["category"], "Sumber Internet Publik")

    def test_hybrid_aggregator_tier1_only_skips_web_scan(self):
        """Mode TIER1_ONLY melewati web scan dan deteksi AI untuk efisiensi kuota 1 token."""
        mock_web_scanner = MagicMock()
        mock_ai_detector = MagicMock()

        aggregator = HybridAggregator(
            ai_detector=mock_ai_detector,
            web_scanner=mock_web_scanner,
        )

        text = "Kalimat pengujian untuk mode cepat satu token."
        result = aggregator.run_pipeline(original_text=text, audit_depth="TIER1_ONLY")

        self.assertEqual(result.audit_depth, "TIER1_ONLY")
        self.assertEqual(result.score_semantic, 0.0)
        self.assertEqual(result.score_stylometric, 0.0)
        mock_web_scanner.scan.assert_not_called()
        mock_ai_detector.analyze_document.assert_not_called()


    def test_gemini_ai_detector_handles_trailing_commas_and_string_indices(self):
        """Detektor AI mampu mem-parse JSON dengan trailing comma dan string sentence_index ('ID: 0')."""
        mock_response_data = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{\n  "ai_probability": 85.0,\n  "suspicious_sentences": [\n    {\n      "sentence_index": "ID: 0",\n      "reason": "Frasa klise AI",\n      "anomaly_score": 0.88,\n    },\n  ],\n}'
                            }
                        ]
                    }
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response_data

        detector = GeminiAIDetector(api_key="test-key-mock")
        sentences = [
            SentenceSpan(index=0, text="Dalam era digital ini, AI memainkan peran krusial bagi kehidupan kita bersama.", start_char=0, end_char=82, word_count=13, is_citation=False),
        ]

        with patch("httpx.Client.post", return_value=mock_resp):
            result = detector.analyze_document("Dalam era digital ini...", sentences)

        self.assertGreater(result.score_t3, 50.0)
        self.assertEqual(len(result.sentence_anomalies), 1)
        self.assertEqual(result.sentence_anomalies[0].sentence_index, 0)

    def test_gemini_ai_detector_retry_on_429(self):
        """Detektor AI melakukan retry dengan backoff saat menghadapi HTTP 429 lalu sukses."""
        resp_429 = MagicMock()
        resp_429.status_code = 429
        resp_429.text = "Rate limit exceeded"

        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": '{"ai_probability": 60.0, "suspicious_sentences": []}'}
                        ]
                    }
                }
            ]
        }

        detector = GeminiAIDetector(api_key="test-key-mock")
        sentences = [
            SentenceSpan(index=0, text="Kalimat pengujian retry rate limit Gemini.", start_char=0, end_char=42, word_count=6, is_citation=False),
        ]

        with patch("httpx.Client.post", side_effect=[resp_429, resp_200]) as mock_post, \
             patch("time.sleep", return_value=None):
            raw = detector.detect_gemini(sentences)

        self.assertIsNotNone(raw)
        self.assertEqual(raw["ai_probability"], 60.0)
        self.assertEqual(mock_post.call_count, 2)

    def test_gemini_web_scanner_scan_with_deduplication(self):
        """Pemindai web mengelompokkan kalimat identik dalam dokumen sehingga hanya 1 representasi dikirim ke API."""
        scanner = GeminiWebScanner(api_key="test-key")

        # Dua span dengan teks identik
        s0 = SentenceSpan(index=0, text="Pancasila adalah dasar filsafat negara Republik Indonesia yang sah.", start_char=0, end_char=68, word_count=9, is_citation=False)
        s5 = SentenceSpan(index=5, text="Pancasila adalah dasar filsafat negara Republik Indonesia yang sah.", start_char=200, end_char=268, word_count=9, is_citation=False)

        mock_gemini_return = [
            {
                "sentence_index": 0,
                "source_title": "Wikipedia",
                "source_url": "https://id.wikipedia.org/wiki/Pancasila",
                "matched_snippet": "Pancasila adalah dasar filsafat negara Republik Indonesia yang sah.",
            }
        ]

        with patch.object(scanner, "_call_gemini_search", return_value=mock_gemini_return) as mock_call:
            results = scanner.scan([s0, s5])

            # Kedua span (index 0 dan 5) harus ada di hasil
            self.assertEqual(len(results), 2)
            indices = {r.sentence_index for r in results}
            self.assertEqual(indices, {0, 5})
            # Namun panggilan ke Gemini hanya 1 kali untuk representatif batch!
            self.assertEqual(mock_call.call_count, 1)

    def test_gemini_web_scanner_does_not_poison_cache_on_failure(self):
        """Saat seluruh pemanggilan pencarian web gagal (mengembalikan None), kalimat TIDAK di-cache sebagai None."""
        scanner = GeminiWebScanner(api_key="test-key")
        s = SentenceSpan(index=0, text="Algoritma pencarian heuristik diterapkan dalam permainan catur komputer.", start_char=0, end_char=73, word_count=9, is_citation=False)

        # Simulasikan seluruh pemanggilan search gagal (mengembalikan None)
        with patch.object(scanner, "_call_gemini_search", return_value=None), patch.object(scanner, "_call_ddg_search", return_value=None):
            res = scanner.scan([s])
            self.assertEqual(res, [])

        h = scanner._sentence_hash(s.text)
        # Hash tidak boleh tersimpan sebagai None di cache!
        self.assertNotIn(h, scanner._cache)
        self.assertFalse(scanner.last_scan_available)

    def test_web_scanner_duckduckgo_fallback_when_gemini_fails(self):
        """Saat Gemini search gagal (mis. rate limit 429), scanner otomatis fallback ke DuckDuckGo search."""
        scanner = GeminiWebScanner(api_key="test-key")
        s = SentenceSpan(index=0, text="Algoritma pencarian heuristik diterapkan dalam permainan catur komputer.", start_char=0, end_char=73, word_count=9, is_citation=False)

        ddg_results = [
            {
                "sentence_index": 0,
                "source_url": "https://example.com/catur-heuristik",
                "source_title": "Heuristik Catur",
                "snippet": "Algoritma pencarian heuristik diterapkan dalam permainan catur komputer modern untuk memperkirakan langkah terbaik.",
            }
        ]

        with patch.object(scanner, "_call_gemini_search", return_value=None), patch.object(scanner, "_call_ddg_search", return_value=ddg_results):
            res = scanner.scan([s])

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].source_url, "https://example.com/catur-heuristik")
        self.assertGreaterEqual(res[0].similarity, 0.70)

    def test_gemini_web_scanner_extracts_from_grounding_metadata(self):
        """Jika LLM tidak menghasilkan JSON terstruktur, ekstraksi fallback dari groundingMetadata tetap bekerja."""
        scanner = GeminiWebScanner(api_key="test-key")
        s = SentenceSpan(index=0, text="Pancasila adalah pilar ideologis negara Indonesia merdeka.", start_char=0, end_char=58, word_count=7, is_citation=False)

        cand = {
            "content": {
                "parts": [
                    {"text": "Berdasarkan penelusuran, kalimat ini ditemukan di ensiklopedia bebas."}
                ]
            },
            "groundingMetadata": {
                "groundingChunks": [
                    {
                        "web": {
                            "uri": "https://id.wikipedia.org/wiki/Pancasila",
                            "title": "Pancasila Ensiklopedia",
                        }
                    }
                ],
                "groundingSupports": [
                    {
                        "groundingChunkIndices": [0],
                        "segment": {
                            "text": "Pancasila adalah pilar ideologis negara Indonesia merdeka.",
                        },
                    }
                ],
            },
        }

        extracted = scanner._extract_matches_from_response(cand, [s])
        self.assertGreater(len(extracted), 0)
        self.assertEqual(extracted[0]["sentence_index"], 0)
        self.assertEqual(extracted[0]["source_url"], "https://id.wikipedia.org/wiki/Pancasila")

    def test_gemini_web_scanner_retry_on_transient_error(self):
        """Pemindai web melakukan retry saat menghadapi status 503 lalu berhasil pada attempt kedua."""
        scanner = GeminiWebScanner(api_key="test-key")
        s = SentenceSpan(index=0, text="Pancasila adalah dasar filsafat negara Republik Indonesia yang sah.", start_char=0, end_char=68, word_count=9, is_citation=False)

        resp_503 = MagicMock()
        resp_503.status_code = 503
        resp_503.text = "Service Unavailable"

        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '[{"sentence_index": 0, "source_title": "Wiki", "source_url": "https://id.wikipedia.org", "matched_snippet": "Pancasila adalah dasar filsafat negara Republik Indonesia yang sah."}]'
                            }
                        ]
                    }
                }
            ]
        }

        with patch("httpx.Client.post", side_effect=[resp_503, resp_200]) as mock_post, \
             patch("time.sleep", return_value=None):
            matches = scanner._call_gemini_search([s])

        self.assertIsNotNone(matches)
        self.assertEqual(len(matches), 1)
        self.assertEqual(mock_post.call_count, 2)

    def test_hybrid_aggregator_unions_corpus_and_web_scores_without_clobbering(self):
        """HybridAggregator menggabungkan kecocokan korpus dan temuan web secara union sehingga skor merefleksikan seluruh kalimat plagiat."""
        mock_web_matches = [
            WebMatchResult(
                sentence_index=1,  # Kalimat kedua cocok di web
                similarity=0.90,
                source_url="https://jurnal.ugm.ac.id/artikel-1",
                source_title="Jurnal UGM",
                matched_snippet="Ini kalimat kedua yang ditemukan di publikasi online.",
                tier="T1",
            )
        ]

        mock_web_scanner = MagicMock()
        mock_web_scanner.scan.return_value = mock_web_matches
        mock_web_scanner.last_scan_available = True
        mock_web_scanner.last_scan_note = None

        mock_ai_detector = MagicMock()
        from app.engine.tier3_stylometric import StylometricAnalysisResult
        mock_ai_detector.analyze_document.return_value = StylometricAnalysisResult(
            score_t3=10.0,
            burstiness=0.45,
            mean_sentence_length=15.0,
            std_sentence_length=6.0,
            type_token_ratio=0.75,
            total_words=20,
            unique_words=18,
            is_ai_monotonous=False,
            sentence_anomalies=[],
        )

        aggregator = HybridAggregator(
            ai_detector=mock_ai_detector,
            web_scanner=mock_web_scanner,
        )

        # Mock tier 1 lexical agar kalimat indeks 0 cocok di korpus
        from app.engine.tier1_lexical import LexicalAnalysisResult, SentenceLexicalMatch
        aggregator.tier1_engine.analyze_document = MagicMock(return_value=LexicalAnalysisResult(
            score_t1=50.0,
            doc_fingerprints=[(12345, 0), (67890, 10)],
            matched_fingerprints={12345},
            sentence_matches=[
                SentenceLexicalMatch(
                    sentence_index=0,
                    matching_fingerprints=5,
                    total_fingerprints=5,
                    similarity=1.0,
                    matched_corpus_doc_id="doc-local-1",
                    matched_source_title="Dokumen Lokal 1",
                )
            ],
            corpus_contributions={"doc-local-1": {"title": "Dokumen Lokal 1", "match_count": 5}},
        ))

        text = "Kalimat pertama cocok dengan korpus lokal. Kalimat kedua ditemukan di publikasi online internet."
        result = aggregator.run_pipeline(text, audit_depth="FULL")

        # 2 dari 2 kalimat cocok (1 korpus, 1 web) -> score_t1 harus 100%!
        self.assertEqual(result.score_lexical, 100.0)
        # Anotasi heatmap harus memuat kedua kalimat (satu dari web T1, satu dari korpus T1)
        self.assertEqual(len(result.heatmap_annotations), 2)
        urls = {a.get("source_url") for a in result.heatmap_annotations}
        self.assertIn("https://jurnal.ugm.ac.id/artikel-1", urls)

    def test_hybrid_aggregator_notes_when_web_scan_unavailable(self):
        """Saat pemindaian web tidak tersedia, HybridAggregator menyertakan catatan sistem di matched_sources."""
        mock_web_scanner = MagicMock()
        mock_web_scanner.scan.return_value = []
        mock_web_scanner.last_scan_available = False
        mock_web_scanner.last_scan_note = "Kunci API Gemini tidak dikonfigurasi."

        mock_ai_detector = MagicMock()
        from app.engine.tier3_stylometric import StylometricAnalysisResult
        mock_ai_detector.analyze_document.return_value = StylometricAnalysisResult(
            score_t3=0.0,
            burstiness=0.5,
            mean_sentence_length=10.0,
            std_sentence_length=4.0,
            type_token_ratio=0.8,
            total_words=10,
            unique_words=8,
            is_ai_monotonous=False,
            sentence_anomalies=[],
        )

        aggregator = HybridAggregator(
            ai_detector=mock_ai_detector,
            web_scanner=mock_web_scanner,
        )

        text = "Kalimat pengujian ketika pemindaian web tidak tersedia."
        result = aggregator.run_pipeline(text, audit_depth="FULL")

        self.assertFalse(result.web_scan_available)
        self.assertIsNotNone(result.web_scan_note)
        self.assertIn("Kunci API Gemini tidak dikonfigurasi", result.web_scan_note)

    def test_worker_refunds_one_token_when_web_scan_unavailable_in_full_audit(self):
        """Worker Celery mengembalikan 1 token ke wallet jika audit FULL dijalankan saat web scan tidak tersedia."""
        import uuid
        from app.models.audit import AuditTask
        from app.models.document import Document
        from app.models.wallet import TokenWallet, TokenTransaction
        from app.workers.tasks import execute_audit_pipeline

        test_user_id = uuid.uuid4()
        test_doc_id = uuid.uuid4()
        test_task_id = uuid.uuid4()

        wallet = TokenWallet(user_id=test_user_id, balance=5)
        doc = Document(
            id=test_doc_id,
            original_filename="Skripsi_Jalur1.txt",
            stored_filename="skripsi_jalur1.txt",
            mime_type="text/plain",
        )
        task = AuditTask(
            id=test_task_id,
            document_id=test_doc_id,
            user_id=test_user_id,
            audit_depth="FULL",
            status="QUEUED",
        )

        class MockSession:
            def __init__(self):
                self.records = {}
                self.tx_added = []
            def query(self, *entities):
                sess = self
                model = entities[0] if entities else None
                class QueryMock:
                    def filter(self, *conds):
                        return self
                    def order_by(self, *a):
                        return self
                    def first(self):
                        for r in sess.records.values():
                            if isinstance(r, model):
                                return r
                        return None
                    def delete(self):
                        return 0
                    def all(self):
                        return []
                    def join(self, *a, **k):
                        return self
                return QueryMock()
            def add(self, obj):
                self.records[id(obj)] = obj
                if isinstance(obj, TokenTransaction):
                    self.tx_added.append(obj)
            def commit(self):
                pass
            def rollback(self):
                pass

        mock_db = MockSession()
        mock_db.add(wallet)
        mock_db.add(doc)
        mock_db.add(task)

        # Mock HybridAggregator to simulate web_scan_available=False
        from app.engine.tier4_aggregator import HybridAuditResult
        mock_audit_res = HybridAuditResult(
            score_lexical=0.0,
            score_semantic=0.0,
            score_stylometric=0.0,
            score_composite=0.0,
            audit_depth="FULL",
            sentences=[],
            heatmap_annotations=[],
            matched_sources=[],
            web_scan_available=False,
            web_scan_note="Pemindaian web tidak tersedia",
        )

        with patch("app.engine.tier4_aggregator.HybridAggregator.run_pipeline", return_value=mock_audit_res):
            res = execute_audit_pipeline(mock_db, str(test_task_id), str(test_doc_id))

        self.assertEqual(res["status"], "SUCCESS")
        # Saldo awal 5, dikembalikan 1 token menjadi 6
        self.assertEqual(wallet.balance, 6)
        # Transaksi pengembalian token harus tercatat
        self.assertEqual(len(mock_db.tx_added), 1)
        refund_tx = mock_db.tx_added[0]
        self.assertEqual(refund_tx.transaction_type, "CREDIT_REFUND")
        self.assertEqual(refund_tx.amount, 1)


if __name__ == "__main__":
    unittest.main()

