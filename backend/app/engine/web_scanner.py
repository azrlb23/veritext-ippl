from __future__ import annotations

import concurrent.futures
import hashlib
import logging
import time
from typing import Any, ClassVar

from app.core.config import settings
from app.engine.preprocessor import SentenceSpan
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticEngine
from app.engine.web_cache import BoundedTTLCache
from app.engine.web_search_providers import call_ddg_search_api, call_gemini_search_api
from app.engine.web_snippet_verifier import WebMatchResult, extract_matches_from_response, is_meaningful_sentence, verify_snippet_cross_check

logger = logging.getLogger(__name__)
WEB_SCAN_BUDGET_S: float = 45.0


def _sample_evenly(items: list[SentenceSpan], limit: int) -> list[SentenceSpan]:
    if limit <= 0:
        return []
    return items if len(items) <= limit else [items[int(i * len(items) / limit)] for i in range(limit)]


class GeminiWebScanner:
    """Pemindai plagiarisme web publik menggunakan Gemini REST API + Google Search Grounding."""

    _cache: ClassVar[BoundedTTLCache[WebMatchResult | None]] = BoundedTTLCache(max_size=2048, ttl_s=3600)

    def __init__(
        self, api_key: str | None = None, model: str | None = None, timeout_s: int | None = None,
        lexical_engine: WinnowingLexicalEngine | None = None, semantic_engine: SemanticEngine | None = None,
    ):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.timeout_s = timeout_s or settings.WEB_SCAN_TIMEOUT_S
        self.lexical_engine = lexical_engine or WinnowingLexicalEngine()
        self.semantic_engine = semantic_engine or SemanticEngine()
        self.last_scan_available: bool = True
        self.last_scan_note: str | None = None

    @classmethod
    def clear_cache(cls) -> None: cls._cache.clear()
    @staticmethod
    def _sentence_hash(text: str) -> str: return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()
    def _is_meaningful_sentence(self, s: SentenceSpan) -> bool: return is_meaningful_sentence(s)
    def verify_snippet_cross_check(self, sentence_text: str, snippet: str) -> tuple[float, float, bool, str]:
        return verify_snippet_cross_check(sentence_text, snippet, self.lexical_engine, self.semantic_engine)
    def _extract_matches_from_response(self, cand: dict[str, Any], batch_sentences: list[SentenceSpan]) -> list[dict[str, Any]]:
        return extract_matches_from_response(cand, batch_sentences)
    def _call_gemini_search(self, batch_sentences: list[SentenceSpan]) -> list[dict[str, Any]] | None:
        matches, _ = call_gemini_search_api(self.api_key, self.model, self.timeout_s, batch_sentences, self._extract_matches_from_response)
        return matches
    def _call_ddg_search(self, batch_sentences: list[SentenceSpan]) -> list[dict[str, Any]] | None:
        return call_ddg_search_api(self.timeout_s, batch_sentences)

    def _apply_batch_results(
        self, batch: list[SentenceSpan], raw: list[dict[str, Any]],
        hash_to_spans: dict[str, list[SentenceSpan]], verified_results: list[WebMatchResult],
    ) -> None:
        matched_hashes, b_by_idx = set(), {s.index: s for s in batch}
        for it in raw:
            try:
                s_idx = int(it.get("sentence_index"))
                if s_idx not in b_by_idx: continue
                s_rep = b_by_idx[s_idx]
                snip, url = str(it.get("matched_snippet") or it.get("snippet", "")).strip(), str(it.get("source_url", "")).strip()
                title = str(it.get("source_title", "Sumber Web Publik")).strip()
                if not url or not snip: continue
                lex_s, sem_s, ok, tier = self.verify_snippet_cross_check(s_rep.text, snip)
                h = self._sentence_hash(s_rep.text)
                if ok:
                    sim = round(max(lex_s, sem_s), 2)
                    self._cache.set(h, WebMatchResult(s_rep.index, sim, url, title, snip, tier))
                    matched_hashes.add(h)
                    verified_results.extend(WebMatchResult(st.index, sim, url, title, snip, tier) for st in hash_to_spans.get(h, [s_rep]))
            except Exception as err:  # noqa: BLE001
                logger.debug("Snippet verification error: %s", err)
        for s_item in batch:
            h = self._sentence_hash(s_item.text)
            if h not in matched_hashes and h not in self._cache:
                self._cache.set(h, None)

    def scan(self, sentences: list[SentenceSpan]) -> list[WebMatchResult]:
        self.last_scan_available, self.last_scan_note = True, None
        if not settings.WEB_SCAN_ENABLED:
            self.last_scan_available, self.last_scan_note = False, "Pemindaian web dinonaktifkan di konfigurasi sistem."
            return []
        use_ddg_only = not (self.api_key and self.api_key.strip())
        meaningful = [s for s in sentences if is_meaningful_sentence(s)]
        if not meaningful:
            return []
        to_scan = _sample_evenly(meaningful, settings.WEB_SCAN_MAX_SENTENCES)
        if len(meaningful) > settings.WEB_SCAN_MAX_SENTENCES:
            self.last_scan_note = f"{len(to_scan)} dari {len(meaningful)} kalimat dipindai ke web; sisa naskah diperiksa dengan tier lokal."
        hash_to_spans: dict[str, list[SentenceSpan]] = {}
        for s in to_scan:
            hash_to_spans.setdefault(self._sentence_hash(s.text), []).append(s)
        verified_results, uncached = [], []
        for h, spans in hash_to_spans.items():
            hit, c = self._cache.get(h)
            if hit and c is not None:
                verified_results.extend(WebMatchResult(s.index, c.similarity, c.source_url, c.source_title, c.matched_snippet, c.tier) for s in spans)
            elif not hit:
                uncached.append(spans[0])
        if not uncached:
            return verified_results
        batches = [uncached[i : i + 10] for i in range(0, len(uncached), 10)]
        def _fetch(b: list[SentenceSpan]) -> list[dict[str, Any]] | None:
            raw = self._call_gemini_search(b) if not use_ddg_only else None
            return raw if raw is not None else self._call_ddg_search(b)
        has_failure, all_failed, timed_out = False, True, False
        deadline = time.monotonic() + WEB_SCAN_BUDGET_S
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=min(8, max(1, len(batches))))
        fut_map: dict[concurrent.futures.Future[Any], list[SentenceSpan]] = {}
        try:
            fut_map = {executor.submit(_fetch, b): b for b in batches}
            try:
                for fut in concurrent.futures.as_completed(fut_map, timeout=WEB_SCAN_BUDGET_S):
                    try:
                        raw = fut.result()
                    except Exception:  # noqa: BLE001
                        raw = None
                    if raw is None: has_failure = True
                    else:
                        all_failed = False
                        self._apply_batch_results(fut_map[fut], raw, hash_to_spans, verified_results)
                    if time.monotonic() >= deadline:
                        timed_out = any(not f.done() for f in fut_map)
                        break
            except concurrent.futures.TimeoutError:
                timed_out = True
        finally:
            for f in fut_map: f.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
        if all_failed and uncached:
            self.last_scan_available = False
            self.last_scan_note = "Pemindaian web melewati batas waktu; dokumen diperiksa dengan tier lokal." if timed_out else "Pemindaian web tidak tersedia karena kendala jaringan atau batas kuota API."
        elif timed_out:
            self.last_scan_note = "Sebagian batch pemindaian web melewati batas waktu; hasil parsial digunakan bersama tier lokal."
        elif has_failure and not self.last_scan_note:
            self.last_scan_note = "Sebagian kalimat naskah tidak dapat dipindai ke web dan diperiksa oleh tier lokal."
        return verified_results


__all__ = ["GeminiWebScanner", "WebMatchResult"]
