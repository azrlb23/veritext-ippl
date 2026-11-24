from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

from app.engine import web_scanner as ws_mod
from app.engine.preprocessor import SentenceSpan
from app.engine.web_scanner import GeminiWebScanner, _sample_evenly
from app.engine.web_search_providers import call_ddg_search_api


def _make_sentences(count: int) -> list[SentenceSpan]:
    return [
        SentenceSpan(
            index=i,
            text=f"Kalimat akademik nomor {i} membahas metodologi penelitian kuantitatif modern secara rinci.",
            start_char=i * 90,
            end_char=i * 90 + 85,
            word_count=10,
            is_citation=False,
        )
        for i in range(count)
    ]


def _fast_scanner() -> GeminiWebScanner:
    sem = MagicMock()
    sem.embed_sentence.return_value = [1.0, 0.0]
    sem.cosine_similarity.return_value = 0.92
    return GeminiWebScanner(api_key="test-key", semantic_engine=sem)


def test_sample_evenly_covers_start_middle_and_end() -> None:
    items = _make_sentences(100)
    sampled = _sample_evenly(items, 10)
    assert len(sampled) == 10
    assert [s.index for s in sampled] == [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    assert _sample_evenly(items[:5], 10) == items[:5]
    assert _sample_evenly(items, 0) == []


def test_scan_processes_batches_in_parallel_and_merges_results() -> None:
    GeminiWebScanner.clear_cache()
    scanner = _fast_scanner()
    barrier, lock, call_count = threading.Barrier(2, timeout=2.0), threading.Lock(), 0

    def fake_gemini(batch: list[SentenceSpan]) -> list[dict]:
        nonlocal call_count
        with lock:
            call_count += 1
            order = call_count
        if order <= 2:
            barrier.wait()
        t = batch[0]
        return [{"sentence_index": t.index, "source_url": f"https://example.org/{t.index}", "source_title": f"Src {t.index}", "matched_snippet": t.text}]

    with patch.object(scanner, "_call_gemini_search", side_effect=fake_gemini):
        results = scanner.scan(_make_sentences(25))
    assert call_count == 3
    assert {r.sentence_index for r in results} == {0, 10, 20}
    assert scanner.last_scan_available is True


def test_scan_enforces_budget_and_keeps_partial_results() -> None:
    GeminiWebScanner.clear_cache()
    scanner = _fast_scanner()

    def slow_or_fast(batch: list[SentenceSpan]) -> list[dict]:
        if batch[0].index == 10:
            time.sleep(0.5)
        t = batch[0]
        return [{"sentence_index": t.index, "source_url": f"https://example.org/p-{t.index}", "source_title": "Parsial", "matched_snippet": t.text}]

    with patch.object(ws_mod, "WEB_SCAN_BUDGET_S", 0.12), patch.object(scanner, "_call_gemini_search", side_effect=slow_or_fast):
        results = scanner.scan(_make_sentences(20))
    assert [r.sentence_index for r in results] == [0]
    assert scanner.last_scan_available is True
    assert scanner.last_scan_note is not None and "batas waktu" in scanner.last_scan_note


def test_call_ddg_search_api_runs_queries_in_parallel() -> None:
    barrier, lock, calls = threading.Barrier(2, timeout=2.0), threading.Lock(), 0

    class FakeDDGS:
        def __init__(self, timeout: int | None = None) -> None:
            self.timeout = timeout

        def text(self, query: str, max_results: int = 3) -> list[dict]:
            nonlocal calls
            with lock:
                calls += 1
                idx = calls
            if idx <= 2:
                barrier.wait()
            return [{"body": f"Hasil untuk {query}", "href": f"https://ddg.test/{idx}", "title": "DDG"}]

    with patch("ddgs.DDGS", FakeDDGS):
        results = call_ddg_search_api(timeout_s=10, batch_sentences=_make_sentences(4))
    assert results is not None and len(results) == 4
    assert {r["sentence_index"] for r in results} == {0, 1, 2, 3}
