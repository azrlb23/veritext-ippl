from __future__ import annotations

import logging
import re
from typing import Any

from app.core.config import settings
from app.engine.preprocessor import SentenceSpan
from app.engine.tier3_stylometric import (
    StylometricAnalysisResult,
    StylometricEngine,
    StylometricSentenceAnomaly,
)
from app.llm.deepseek_client import DeepSeekRouterClient
from app.llm.gateway import DualEngineLLMGateway
from app.llm.gemini_client import GeminiFlashClient

logger = logging.getLogger(__name__)


class GeminiAIDetector:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        openrouter_key: str | None = None,
        openrouter_model: str | None = None,
        timeout_s: int | None = None,
        stylometric_engine: StylometricEngine | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.openrouter_key = openrouter_key if openrouter_key is not None else settings.OPENROUTER_API_KEY
        self.openrouter_model = openrouter_model or settings.OPENROUTER_MODEL or "nvidia/nemotron-3.5-lightning:free"
        self.timeout_s = timeout_s or settings.WEB_SCAN_TIMEOUT_S
        self.stylometric_engine = stylometric_engine or StylometricEngine()
        self.gemini_client = GeminiFlashClient(self.api_key, self.model, self.timeout_s)
        self.deepseek_client = DeepSeekRouterClient(
            api_key=self.openrouter_key, model=self.openrouter_model, timeout_s=self.timeout_s
        )
        self.gateway = DualEngineLLMGateway(self.gemini_client, self.deepseek_client)

    def _prepare_prompt(self, sentences: list[SentenceSpan]) -> str:
        return self.gateway.build_judge_prompt(sentences)

    def detect_openrouter(self, sentences: list[SentenceSpan]) -> dict[str, Any] | None:
        if not self.openrouter_key or not self.openrouter_key.strip():
            return None
        valid = [s for s in sentences if not s.is_citation and s.word_count >= 3]
        if not valid:
            return None
        raw = self.deepseek_client.generate_json(self._prepare_prompt(valid[: settings.WEB_SCAN_MAX_SENTENCES]))
        if not raw:
            return None
        return {
            "ai_probability": max(0.0, min(100.0, float(raw.get("ai_probability", 0.0)))),
            "suspicious_sentences": raw.get("suspicious_sentences", []),
        }

    def detect_gemini(self, sentences: list[SentenceSpan]) -> dict[str, Any] | None:
        if not self.api_key or not self.api_key.strip():
            return None
        valid = [s for s in sentences if not s.is_citation and s.word_count >= 3]
        if not valid:
            return None
        raw = self.gemini_client.generate_json(self._prepare_prompt(valid[: settings.WEB_SCAN_MAX_SENTENCES]))
        if not raw:
            return None
        return {
            "ai_probability": max(0.0, min(100.0, float(raw.get("ai_probability", 0.0)))),
            "suspicious_sentences": raw.get("suspicious_sentences", []),
        }

    def analyze_document(
        self, original_text: str, sentences: list[SentenceSpan]
    ) -> StylometricAnalysisResult:
        local_res = self.stylometric_engine.analyze_document(original_text, sentences)
        if not sentences or not original_text.strip():
            return local_res

        llm_data, evaluator_name = None, "LLM"
        if self.openrouter_key:
            llm_data = self.detect_openrouter(sentences)
            if llm_data:
                evaluator_name = f"OpenRouter ({self.openrouter_model})"
        if not llm_data and self.api_key:
            llm_data = self.detect_gemini(sentences)
            if llm_data:
                evaluator_name = f"Gemini ({self.model})"
        if not llm_data:
            return local_res

        prob = float(llm_data.get("ai_probability", 0.0))
        comp = round(min(100.0, max(0.0, 0.65 * prob + 0.35 * local_res.score_t3)), 2)
        anomalies = self._merge_anomalies(
            local_res.sentence_anomalies, sentences, llm_data.get("suspicious_sentences", []), evaluator_name
        )
        return StylometricAnalysisResult(
            score_t3=comp, burstiness=local_res.burstiness,
            mean_sentence_length=local_res.mean_sentence_length,
            std_sentence_length=local_res.std_sentence_length,
            type_token_ratio=local_res.type_token_ratio, total_words=local_res.total_words,
            unique_words=local_res.unique_words, is_ai_monotonous=comp >= 35.0,
            sentence_anomalies=anomalies,
        )

    def _merge_anomalies(
        self,
        local_anomalies: list[StylometricSentenceAnomaly],
        sentences: list[SentenceSpan],
        suspicious: list[dict[str, Any]],
        evaluator_name: str,
    ) -> list[StylometricSentenceAnomaly]:
        mapping = {a.sentence_index: a for a in local_anomalies}
        by_idx = {s.index: s for s in sentences}
        for item in suspicious:
            try:
                raw_idx = item.get("sentence_index")
                if raw_idx is None:
                    continue
                match = re.search(r"\d+", str(raw_idx))
                if not match or int(match.group(0)) not in by_idx:
                    continue
                s_idx = int(match.group(0))
                s_span, reason = by_idx[s_idx], str(item.get("reason", "Indikasi pola tulisan AI generatif"))
                score = round(max(0.0, min(1.0, float(item.get("anomaly_score", 0.75)))), 2)
                if s_idx in mapping:
                    combined = round(max(mapping[s_idx].anomaly_score, score), 2)
                    conf_reason = f"{reason} (Dikonfirmasi evaluator {evaluator_name})"
                    mapping[s_idx] = StylometricSentenceAnomaly(
                        sentence_index=s_idx, word_count=s_span.word_count, anomaly_score=combined, reason=conf_reason
                    )
                else:
                    mapping[s_idx] = StylometricSentenceAnomaly(
                        sentence_index=s_idx, word_count=s_span.word_count, anomaly_score=score, reason=reason
                    )
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                logger.debug(f"Ignore anomaly: {exc}")
        return sorted(mapping.values(), key=lambda a: a.sentence_index)
