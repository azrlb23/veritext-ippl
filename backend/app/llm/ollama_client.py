from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.llm.gemini_client import clean_llm_json

logger = logging.getLogger(__name__)


class OllamaLocalClient:
    """Local OpenAI-compatible Ollama client for LLM fallback."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout_s: int | None = None,
    ) -> None:
        self.model = model or settings.OLLAMA_MODEL
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.timeout_s = (
            timeout_s if timeout_s is not None else max(settings.WEB_SCAN_TIMEOUT_S, 45)
        )

    def _post_chat(self, prompt: str, temperature: float) -> str | None:
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        try:
            with httpx.Client(timeout=float(self.timeout_s)) as client:
                response = client.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                logger.warning(
                    "Ollama client returned status %s: %s",
                    response.status_code,
                    response.text[:200],
                )
                return None

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return None
            content = choices[0].get("message", {}).get("content", "").strip()
            return content or None
        except (httpx.HTTPError, ValueError, TypeError, KeyError, RuntimeError) as exc:
            logger.warning("Ollama client error (%s: %s)", type(exc).__name__, exc)
            return None

    def generate_json(self, prompt: str) -> dict[str, Any] | None:
        content = self._post_chat(prompt, temperature=0.1)
        if not content:
            return None
        try:
            return clean_llm_json(content)
        except (ValueError, TypeError, KeyError, RuntimeError) as exc:
            logger.warning("Ollama JSON parse error (%s: %s)", type(exc).__name__, exc)
            return None

    def generate_text(self, prompt: str) -> str | None:
        return self._post_chat(prompt, temperature=0.2)
