from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

GEMINI_FALLBACK_MODELS: tuple[str, ...] = (
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemma-4-26b-a4b-it",
)
_ENDPOINT_FMT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def clean_llm_json(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    text = re.sub(r",\s*([\]}])", r"\1", text)
    result = json.loads(text)
    return result if isinstance(result, dict) else {"raw": result}


class GeminiFlashClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_s: int | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.timeout_s = timeout_s or settings.WEB_SCAN_TIMEOUT_S

    def _candidate_models(self) -> list[str]:
        seen: list[str] = []
        for m in (self.model, *GEMINI_FALLBACK_MODELS):
            if m and m not in seen:
                seen.append(m)
        return seen

    def _post_model(self, model: str, payload: dict[str, Any], max_retries: int = 1) -> dict[str, Any] | None:
        url = _ENDPOINT_FMT.format(model=model)
        headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}
        for attempt in range(max_retries + 1):
            try:
                with httpx.Client(timeout=float(self.timeout_s)) as client:
                    response = client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    return response.json()
                if response.status_code in (500, 502, 503, 504) and attempt < max_retries:
                    time.sleep(0.5)
                    continue
                logger.warning("Gemini model %s status %s, beralih ke fallback", model, response.status_code)
                return None
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt < max_retries:
                    time.sleep(0.5)
                    continue
                logger.warning("Gemini model %s network/timeout: %s", model, type(exc).__name__)
                return None
            except (httpx.HTTPError, ValueError, TypeError, RuntimeError) as exc:
                logger.warning("Gemini model %s error: %s", model, type(exc).__name__)
                return None
        return None

    def generate_json(self, prompt: str, max_retries: int = 1) -> dict[str, Any] | None:
        if not self.api_key or not self.api_key.strip():
            return None
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1},
        }
        for model in self._candidate_models():
            data = self._post_model(model, payload, max_retries=max_retries)
            if not data:
                continue
            try:
                candidates = data.get("candidates", [])
                parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
                if parts:
                    return clean_llm_json(parts[0].get("text", ""))
            except (ValueError, TypeError, KeyError, IndexError) as exc:
                logger.warning("Gemini JSON parse gagal pada %s: %s", model, exc)
        return None

    def generate_text(self, prompt: str) -> str | None:
        if not self.api_key or not self.api_key.strip():
            return None
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
        for model in self._candidate_models():
            data = self._post_model(model, payload, max_retries=0)
            if not data:
                continue
            try:
                candidates = data.get("candidates", [])
                parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
                text = parts[0].get("text", "").strip() if parts else ""
                if text:
                    return text
            except (ValueError, TypeError, KeyError, IndexError):
                continue
        return None
