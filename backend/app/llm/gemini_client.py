from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


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

    def generate_json(self, prompt: str, max_retries: int = 2) -> dict[str, Any] | None:
        if not self.api_key or not self.api_key.strip():
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1},
        }

        for attempt in range(max_retries + 1):
            try:
                with httpx.Client(timeout=float(self.timeout_s)) as client:
                    response = client.post(url, headers=headers, params=params, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        return None
                    parts = candidates[0].get("content", {}).get("parts", [])
                    return clean_llm_json(parts[0].get("text", "")) if parts else None

                if response.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    time.sleep(1.0 * (attempt + 1))
                    continue

                logger.warning(f"Gemini API returned status {response.status_code}")
                return None

            except (httpx.TimeoutException, httpx.NetworkError):
                if attempt < max_retries:
                    time.sleep(1.0 * (attempt + 1))
                    continue
                return None
            except (httpx.HTTPError, ValueError, TypeError, KeyError, RuntimeError) as exc:
                logger.warning(f"Gemini API call failed: {exc}")
                return None
        return None

    def generate_text(self, prompt: str) -> str | None:
        if not self.api_key or not self.api_key.strip():
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }

        try:
            with httpx.Client(timeout=float(self.timeout_s)) as client:
                response = client.post(url, headers=headers, params=params, json=payload)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
                return parts[0].get("text", "").strip() or None if parts else None
            return None
        except (httpx.HTTPError, ValueError, TypeError, KeyError, RuntimeError) as exc:
            logger.warning(f"Gemini generate_text failed: {exc}")
            return None
