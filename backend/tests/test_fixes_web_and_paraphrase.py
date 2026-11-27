from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from app.core.config import settings
from app.engine.ai_detector import GeminiAIDetector
from app.llm.deepseek_client import DeepSeekRouterClient
from app.services.assistant_service import AssistantService


def test_ddgs_import_succeeds() -> None:
    from ddgs import DDGS

    assert DDGS is not None


def test_paraphrase_prompt_locks_original_language() -> None:
    captured_prompts: list[str] = []
    mock_variations = [
        {"option_id": 1, "style": "Formal", "text": "Kalimat formal.", "predicted_score": 8.5},
        {"option_id": 2, "style": "Ringkas", "text": "Kalimat ringkas.", "predicted_score": 8.0},
        {"option_id": 3, "style": "Analitis", "text": "Kalimat analitis.", "predicted_score": 8.3},
    ]

    def fake_generate(prompt: str, preferred_engine: str = "auto") -> tuple[str, str]:
        _ = preferred_engine
        captured_prompts.append(prompt)
        return json.dumps(mock_variations), "DeepSeek (test)"

    mock_gw = MagicMock()
    mock_gw.generate_text_with_failover.side_effect = fake_generate

    variations, engine = AssistantService.generate_paraphrase_variations(
        "Penelitian ini mengkaji efektivitas deteksi plagiarisme akademik.",
        mode="SENTENCE",
        gateway=mock_gw,
    )

    assert len(variations) == 3
    assert engine == "DeepSeek (test)"
    assert len(captured_prompts) == 1
    prompt = captured_prompts[0]
    assert "WAJIB pertahankan bahasa yang sama persis dengan teks asli" in prompt
    assert "bahasa Indonesia akademik baku" in prompt
    assert "jangan diterjemahkan ke bahasa lain" in prompt


def test_gemini_ai_detector_default_aligns_with_router9() -> None:
    with (
        patch.object(settings, "ROUTER9_API_KEY", "r9-test-key"),
        patch.object(settings, "ROUTER9_MODEL", "deepseek/deepseek-v4.1-flash"),
        patch.object(settings, "ROUTER9_BASE_URL", "http://localhost:20128/v1"),
        patch.object(settings, "OPENROUTER_API_KEY", "or-fallback-key"),
        patch.object(settings, "OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free"),
    ):
        detector = GeminiAIDetector()
        client = DeepSeekRouterClient()

        assert detector.deepseek_client.api_key == "r9-test-key"
        assert detector.deepseek_client.api_key == client.api_key
        assert detector.deepseek_client.model == client.model
        assert detector.deepseek_client.base_url == client.base_url
        assert detector.openrouter_key == "r9-test-key"

        explicit = GeminiAIDetector(
            openrouter_key="explicit-or-key",
            openrouter_model="custom/model",
        )
        assert explicit.deepseek_client.api_key == "explicit-or-key"
        assert explicit.deepseek_client.model == "custom/model"
        assert explicit.openrouter_key == "explicit-or-key"
