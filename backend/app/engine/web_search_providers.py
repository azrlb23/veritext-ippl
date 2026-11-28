from __future__ import annotations

import concurrent.futures
import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

from app.engine.preprocessor import SentenceSpan, TextPreprocessor

logger = logging.getLogger(__name__)


def call_gemini_search_api(
    api_key: str,
    model: str,
    timeout_s: int,
    batch_sentences: list[SentenceSpan],
    extractor_fn: Callable[[dict[str, Any], list[SentenceSpan]], list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]] | None, str | None]:
    """Mengirim batch kalimat ke Gemini dengan Google Search Grounding tool."""
    lines = [f"[ID: {s.index}] {s.text.replace(chr(10), ' ').strip()}" for s in batch_sentences]
    prompt = (
        "Anda adalah asisten verifikasi plagiarisme web berstandar ketat. "
        "Tugas Anda: telusuri web publik menggunakan Google Search untuk setiap kalimat naskah berikut, "
        "dan cari apakah kalimat tersebut terdapat pada artikel jurnal, berita, Wikipedia, atau situs web publik.\n\n"
        f"Daftar kalimat:\n{chr(10).join(lines)}\n\n"
        "Untuk SETIAP kalimat yang terbukti memiliki kecocokan di internet, kembalikan data dalam format JSON array:\n"
        "```json\n[\n  {\n    \"sentence_index\": <int ID kalimat>,\n"
        "    \"source_title\": \"<string judul artikel atau halaman web>\",\n"
        "    \"source_url\": \"<string URL sumber asli https://...>\",\n"
        "    \"matched_snippet\": \"<string kutipan asli dari situs web tersebut>\"\n  }\n]\n```\n"
        "Jika tidak ada kecocokan di internet untuk suatu kalimat, jangan masukkan ke daftar array. "
        "KEMBALIKAN HANYA BLOK JSON."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    payload = {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            with httpx.Client(timeout=float(timeout_s)) as client:
                resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return [], None
                return extractor_fn(candidates[0], batch_sentences), None
            elif resp.status_code == 400 and "google_search" in resp.text:
                payload["tools"] = [{"googleSearch": {}}]
                continue
            elif resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
                time.sleep(1.0 * (attempt + 1))
                continue
            else:
                return None, f"HTTP {resp.status_code}"
        except (httpx.TimeoutException, httpx.NetworkError) as net_err:
            if attempt < max_retries:
                time.sleep(1.0 * (attempt + 1))
                continue
            return None, type(net_err).__name__
        except Exception as exc:  # noqa: BLE001
            return None, type(exc).__name__
    return None, "Max retries exceeded"


def call_ddg_search_api(
    timeout_s: int, batch_sentences: list[SentenceSpan]
) -> list[dict[str, Any]] | None:
    """Fallback pencarian web paralel menggunakan DuckDuckGo Search."""
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            logger.warning("Package ddgs tidak terpasang.")
            return None

    req_timeout = max(1, min(timeout_s, 6))
    future_timeout = max(8, min(timeout_s, 15))
    queries = [
        (s, " ".join([w for w in TextPreprocessor.tokenize_words(s.text) if len(w) > 3][:8]))
        for s in batch_sentences
    ]
    queries = [(s, q) for s, q in queries if q]
    if not queries:
        return []

    def _query_one(span: SentenceSpan, query: str) -> list[dict[str, Any]]:
        try:
            client = DDGS(timeout=req_timeout)
        except TypeError:
            client = DDGS()
        items: list[dict[str, Any]] = []
        for r in list(client.text(query, max_results=3)):
            snippet = r.get("body", "") or r.get("snippet", "")
            url = r.get("href", "") or r.get("link", "")
            if snippet and url:
                items.append({
                    "sentence_index": span.index,
                    "source_url": url,
                    "source_title": r.get("title", ""),
                    "snippet": snippet,
                })
        return items

    results_list: list[dict[str, Any]] = []
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=min(6, max(1, len(batch_sentences)))
    )
    try:
        futures = [executor.submit(_query_one, s, q) for s, q in queries]
        try:
            for fut in concurrent.futures.as_completed(futures, timeout=future_timeout):
                try:
                    results_list.extend(fut.result())
                except Exception as ddg_err:  # noqa: BLE001
                    logger.debug("DDG search query error: %s", ddg_err)
        except concurrent.futures.TimeoutError:
            logger.debug("DDG batch search timeout after %ss", future_timeout)
            for fut in futures:
                if not fut.done():
                    fut.cancel()
        return results_list
    except Exception as exc:  # noqa: BLE001
        logger.warning("DuckDuckGo search fallback gagal: %s", exc)
        return None
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
