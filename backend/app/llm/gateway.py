from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from app.core.config import settings
from app.llm.deepseek_client import DeepSeekRouterClient
from app.llm.gemini_client import GeminiFlashClient
from app.llm.ollama_client import OllamaLocalClient

if TYPE_CHECKING:
    from app.engine.preprocessor import SentenceSpan

logger = logging.getLogger(__name__)


def _normalize_result(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    if not raw or not isinstance(raw, dict):
        return None
    try:
        ai_prob = max(0.0, min(100.0, float(raw.get("ai_probability", 0.0))))
        suspicious = raw.get("suspicious_sentences", [])
        return {
            "ai_probability": ai_prob,
            "suspicious_sentences": suspicious if isinstance(suspicious, list) else [],
        }
    except (ValueError, TypeError, KeyError):
        return None


class DualEngineLLMGateway:
    def __init__(
        self,
        gemini_client: GeminiFlashClient | None = None,
        deepseek_client: DeepSeekRouterClient | None = None,
        ollama_client: OllamaLocalClient | None = None,
        strategy: str | None = None,
        nemotron_client: DeepSeekRouterClient | None = None,
    ) -> None:
        self.gemini = gemini_client or GeminiFlashClient()
        self.deepseek = deepseek_client or DeepSeekRouterClient()
        self.nemotron = nemotron_client or (
            DeepSeekRouterClient(
                api_key=settings.OPENROUTER_API_KEY,
                model=settings.OPENROUTER_MODEL,
                base_url="https://openrouter.ai/api/v1",
            )
            if settings.ROUTER9_API_KEY and settings.OPENROUTER_API_KEY
            else None
        )
        self.ollama = ollama_client or OllamaLocalClient()
        self.strategy = strategy or settings.LLM_FAILOVER_STRATEGY

    def _client_order(self, preferred_engine: str | None = None) -> list[tuple[Any, str]]:
        gemini_entry = (self.gemini, f"Gemini ({self.gemini.model})")
        deepseek_entry = (self.deepseek, f"DeepSeek ({self.deepseek.model})")
        nemotron_entries = [(self.nemotron, f"Nemotron ({self.nemotron.model})")] if self.nemotron else []
        ollama_entry = (self.ollama, f"Ollama ({self.ollama.model})")
        overrides = {
            "ollama": [ollama_entry, gemini_entry, deepseek_entry, *nemotron_entries],
            "gemini": [gemini_entry, deepseek_entry, *nemotron_entries, ollama_entry],
            "deepseek": [deepseek_entry, *nemotron_entries, gemini_entry, ollama_entry],
            "nemotron": [*nemotron_entries, deepseek_entry, gemini_entry, ollama_entry],
        }
        pref = (preferred_engine or "").strip().lower()
        if pref in overrides:
            return overrides[pref]
        if self.strategy == "gemini_first":
            return [gemini_entry, deepseek_entry, *nemotron_entries, ollama_entry]
        return [deepseek_entry, *nemotron_entries, gemini_entry, ollama_entry]

    def build_judge_prompt(self, sentences: list[SentenceSpan]) -> str:
        lines = []
        for s in sentences:
            if s.is_citation or s.word_count < 3:
                continue
            cleaned = s.text.replace("\n", " ").strip()
            lines.append(f"[{s.index}] {cleaned}")

        sentences_block = "\n".join(lines)
        return (
            "Anda adalah evaluator orisinalitas teks independen berstandar tinggi. "
            "Tugas Anda menganalisis apakah kalimat-kalimat naskah berikut ditulis secara organik oleh manusia "
            "atau dihasilkan/dibantu secara dominan oleh AI / Large Language Model (seperti ChatGPT, Claude, Gemini).\n\n"
            "Karakteristik tulisan AI:\n"
            "- Struktur sintaksis terlalu seragam dan formulaik.\n"
            "- Frasa transisi generik berulang (misal: 'dalam era digital ini', 'penting untuk dicatat bahwa', 'memainkan peran vital').\n"
            "- Minim ketidakteraturan gaya bahasa alami khas manusia.\n\n"
            "Daftar kalimat naskah:\n"
            f"{sentences_block}\n\n"
            "KEMBALIKAN HANYA JSON MURNI tanpa markdown atau penjelasan luar, dengan format skema:\n"
            "{\n"
            '  "ai_probability": <float 0.0 sampai 100.0>,\n'
            '  "suspicious_sentences": [\n'
            "    {\n"
            '      "sentence_index": <int nomor indeks kalimat>,\n'
            '      "reason": <string alasan ringkas dalam bahasa Indonesia>,\n'
            '      "anomaly_score": <float 0.0 sampai 1.0>\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    def evaluate_sentences(
        self, sentences: list[SentenceSpan]
    ) -> tuple[dict[str, Any] | None, str]:
        meaningful = [s for s in sentences if not s.is_citation and s.word_count >= 3]
        if not meaningful:
            return None, ""

        sample = meaningful[: settings.WEB_SCAN_MAX_SENTENCES]
        prompt = self.build_judge_prompt(sample)

        for client, name in self._client_order():
            raw = client.generate_json(prompt)
            normalized = _normalize_result(raw)
            if normalized is not None:
                return normalized, name

        return None, ""

    def generate_text_with_failover(
        self, prompt: str, preferred_engine: str | None = None
    ) -> tuple[str | None, str]:
        for client, name in self._client_order(preferred_engine):
            text = client.generate_text(prompt)
            if text:
                return text, name

        return None, ""
