from __future__ import annotations

import hashlib
import logging
from typing import Any, ClassVar

from app.core.config import settings
from app.engine.preprocessor import SentenceSpan
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticEngine
from app.engine.web_search_providers import call_ddg_search_api, call_gemini_search_api
from app.engine.web_snippet_verifier import (
    WebMatchResult,
    extract_matches_from_response,
    is_meaningful_sentence,
    verify_snippet_cross_check,
)

logger = logging.getLogger(__name__)


class GeminiWebScanner:
    """Pemindai plagiarisme web publik menggunakan Gemini REST API + Google Search Grounding."""

    _cache: ClassVar[dict[str, WebMatchResult | None]] = {}

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
    def clear_cache(cls) -> None:
        cls._cache.clear()

    @staticmethod
    def _sentence_hash(text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

    def _is_meaningful_sentence(self, s: SentenceSpan) -> bool:
        return is_meaningful_sentence(s)

    def verify_snippet_cross_check(self, sentence_text: str, snippet: str) -> tuple[float, float, bool, str]:
        return verify_snippet_cross_check(sentence_text, snippet, self.lexical_engine, self.semantic_engine)

    def _extract_matches_from_response(self, cand: dict[str, Any], batch_sentences: list[SentenceSpan]) -> list[dict[str, Any]]:
        return extract_matches_from_response(cand, batch_sentences)

    def _call_gemini_search(self, batch_sentences: list[SentenceSpan]) -> list[dict[str, Any]] | None:
        matches, _ = call_gemini_search_api(self.api_key, self.model, self.timeout_s, batch_sentences, self._extract_matches_from_response)
        return matches

    def _call_ddg_search(self, batch_sentences: list[SentenceSpan]) -> list[dict[str, Any]] | None:
        return call_ddg_search_api(self.timeout_s, batch_sentences)

    def scan(self, sentences: list[SentenceSpan]) -> list[WebMatchResult]:
        self.last_scan_available, self.last_scan_note = True, None
        if not settings.WEB_SCAN_ENABLED:
            self.last_scan_available = False
            self.last_scan_note = "Pemindaian web dinonaktifkan di konfigurasi sistem."
            return []

        use_ddg_only = not (self.api_key and self.api_key.strip())
        meaningful = [s for s in sentences if self._is_meaningful_sentence(s)]
        if not meaningful:
            return []

        to_scan = meaningful[: settings.WEB_SCAN_MAX_SENTENCES]
        if len(meaningful) > settings.WEB_SCAN_MAX_SENTENCES:
            self.last_scan_note = f"{settings.WEB_SCAN_MAX_SENTENCES} dari {len(meaningful)} kalimat dipindai ke web; sisa naskah diperiksa dengan tier lokal."

        hash_to_spans: dict[str, list[SentenceSpan]] = {}
        for s in to_scan:
            hash_to_spans.setdefault(self._sentence_hash(s.text), []).append(s)

        verified_results: list[WebMatchResult] = []
        uncached: list[SentenceSpan] = []
        for h, spans in hash_to_spans.items():
            if h in self._cache:
                c = self._cache[h]
                if c is not None:
                    for s in spans:
                        verified_results.append(WebMatchResult(s.index, c.similarity, c.source_url, c.source_title, c.matched_snippet, c.tier))
            else:
                uncached.append(spans[0])

        if not uncached:
            return verified_results

        batch_size = 10
        has_failure, all_failed = False, True
        for i in range(0, len(uncached), batch_size):
            batch = uncached[i : i + batch_size]
            raw = self._call_gemini_search(batch) if not use_ddg_only else None
            if raw is None:
                raw = self._call_ddg_search(batch)
            if raw is None:
                has_failure = True
                continue
            all_failed = False
            matched_hashes = set()
            b_by_idx = {s.index: s for s in batch}
            for it in raw:
                try:
                    s_idx = int(it.get("sentence_index"))
                    if s_idx not in b_by_idx:
                        continue
                    s_rep = b_by_idx[s_idx]
                    snip, url = str(it.get("matched_snippet") or it.get("snippet", "")).strip(), str(it.get("source_url", "")).strip()
                    title = str(it.get("source_title", "Sumber Web Publik")).strip()
                    if not url or not snip:
                        continue
                    lex_s, sem_s, ok, tier = self.verify_snippet_cross_check(s_rep.text, snip)
                    h = self._sentence_hash(s_rep.text)
                    if ok:
                        sim = round(max(lex_s, sem_s), 2)
                        self._cache[h] = WebMatchResult(s_rep.index, sim, url, title, snip, tier)
                        matched_hashes.add(h)
                        for st in hash_to_spans.get(h, [s_rep]):
                            verified_results.append(WebMatchResult(st.index, sim, url, title, snip, tier))
                except Exception as err:  # noqa: BLE001
                    logger.debug("Snippet verification error: %s", err)
            for s_item in batch:
                h = self._sentence_hash(s_item.text)
                if h not in matched_hashes and h not in self._cache:
                    self._cache[h] = None

        if all_failed and uncached:
            self.last_scan_available = False
            self.last_scan_note = "Pemindaian web tidak tersedia karena kendala jaringan atau batas kuota API."
        elif has_failure and not self.last_scan_note:
            self.last_scan_note = "Sebagian kalimat naskah tidak dapat dipindai ke web dan diperiksa oleh tier lokal."
        return verified_results


__all__ = ["GeminiWebScanner", "WebMatchResult"]
