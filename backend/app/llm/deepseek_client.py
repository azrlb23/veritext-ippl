from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.llm.gemini_client import clean_llm_json

logger = logging.getLogger(__name__)


class DeepSeekRouterClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_s: int | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else (
            settings.ROUTER9_API_KEY or settings.OPENROUTER_API_KEY
        )
        self.model = model or (
            settings.ROUTER9_MODEL if settings.ROUTER9_API_KEY else settings.OPENROUTER_MODEL
        )
        default_url = (
            settings.ROUTER9_BASE_URL if settings.ROUTER9_API_KEY else "https://openrouter.ai/api/v1"
        )
        self.base_url = (base_url or default_url).rstrip("/")
        self.timeout_s = timeout_s or settings.WEB_SCAN_TIMEOUT_S

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://veritext.ai",
            "X-Title": "VeriText AI Plagiarism Audit",
        }

    def generate_json(self, prompt: str) -> dict[str, Any] | None:
        if not self.api_key or not self.api_key.strip():
            return None

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        }

        try:
            with httpx.Client(timeout=float(self.timeout_s)) as client:
                response = client.post(url, headers=self._build_headers(), json=payload)

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if not content:
                    return None
                return clean_llm_json(content)

            logger.warning(f"Router client returned status {response.status_code}: {response.text[:200]}")
            return None
        except (httpx.HTTPError, ValueError, TypeError, KeyError, RuntimeError) as exc:
            logger.warning(f"Router client detection error ({type(exc).__name__}: {exc})")
            return None

    def generate_text(self, prompt: str) -> str | None:
        if not self.api_key or not self.api_key.strip():
            return None

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=float(self.timeout_s)) as client:
                response = client.post(url, headers=self._build_headers(), json=payload)
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    return None
                content = choices[0].get("message", {}).get("content", "").strip()
                return content or None
            return None
        except (httpx.HTTPError, ValueError, TypeError, KeyError, RuntimeError) as exc:
            logger.warning(f"Router client generate_text error: {exc}")
            return None
