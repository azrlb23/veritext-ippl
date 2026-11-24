from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx

from app.llm import local_paraphraser
from app.llm.gateway import DualEngineLLMGateway
from app.llm.ollama_client import OllamaLocalClient


def test_gateway_text_failover_falls_back_to_ollama() -> None:
    gemini = MagicMock(model="gemini-mock")
    gemini.generate_text.return_value = None
    deepseek = MagicMock(model="deepseek-mock")
    deepseek.generate_text.return_value = None
    ollama = MagicMock(model="qwen2.5:7b")
    ollama.generate_text.return_value = "Jawaban dari Ollama lokal"

    gateway = DualEngineLLMGateway(
        gemini_client=gemini,
        deepseek_client=deepseek,
        ollama_client=ollama,
        strategy="gemini_first",
    )
    text, engine = gateway.generate_text_with_failover("Jelaskan metode penelitian.")

    assert text == "Jawaban dari Ollama lokal"
    assert engine == "Ollama (qwen2.5:7b)"
    gemini.generate_text.assert_called_once()
    deepseek.generate_text.assert_called_once()
    ollama.generate_text.assert_called_once()


def test_gateway_evaluate_sentences_falls_back_to_ollama() -> None:
    gemini = MagicMock(model="gemini-mock")
    gemini.generate_json.return_value = None
    deepseek = MagicMock(model="deepseek-mock")
    deepseek.generate_json.return_value = None
    ollama = MagicMock(model="qwen2.5:7b")
    ollama.generate_json.return_value = {"ai_probability": 42.5, "suspicious_sentences": []}

    gateway = DualEngineLLMGateway(gemini_client=gemini, deepseek_client=deepseek, ollama_client=ollama)
    span = SimpleNamespace(index=0, text="Kalimat akademik yang cukup panjang untuk diuji.", is_citation=False, word_count=7)
    result, engine = gateway.evaluate_sentences([span])

    assert result == {"ai_probability": 42.5, "suspicious_sentences": []}
    assert engine == "Ollama (qwen2.5:7b)"


def test_ollama_client_success_and_connection_error() -> None:
    client = OllamaLocalClient(model="qwen2.5:7b", base_url="http://localhost:11434/v1", timeout_s=30)

    ok_text_resp = MagicMock(status_code=200)
    ok_text_resp.json.return_value = {"choices": [{"message": {"content": "  Halo akademik  "}}]}

    ok_json_resp = MagicMock(status_code=200)
    ok_json_resp.json.return_value = {
        "choices": [{"message": {"content": '```json\n{"ai_probability": 15.0, "suspicious_sentences": []}\n```'}}]
    }

    with patch("app.llm.ollama_client.httpx.Client") as mock_http:
        http_inst = mock_http.return_value.__enter__.return_value
        http_inst.post.side_effect = [ok_text_resp, ok_json_resp, httpx.ConnectError("refused"), httpx.ConnectError("refused")]

        assert client.generate_text("Uji teks") == "Halo akademik"
        assert client.generate_json("Uji json") == {"ai_probability": 15.0, "suspicious_sentences": []}
        assert client.generate_text("Uji gagal") is None
        assert client.generate_json("Uji gagal json") is None


def test_generate_local_paraphrases_returns_three_variations() -> None:
    local_paraphraser._MODEL_CACHE.clear()
    mock_tokenizer = MagicMock()
    mock_tokenizer.return_value = {"input_ids": [[1, 2, 3]]}
    mock_tokenizer.decode.side_effect = [
        "Penelitian ini menganalisis dampak kebijakan publik.",
        "Studi ini menelaah implikasi kebijakan publik.",
        "Kajian ini mengevaluasi pengaruh kebijakan publik.",
    ]
    mock_model = MagicMock()
    mock_model.generate.return_value = [[10], [20], [30]]

    with patch.object(local_paraphraser, "_load_paraphrase_model", return_value=(mock_tokenizer, mock_model)):
        results = local_paraphraser.generate_local_paraphrases("Riset ini meneliti efek kebijakan publik.", count=3)

    assert len(results) == 3
    assert [r["option_id"] for r in results] == [1, 2, 3]
    assert [r["style"] for r in results] == ["Formal", "Ringkas", "Akademik"]
    assert all(isinstance(r["predicted_score"], float) and r["text"] for r in results)
    called_prompt = mock_tokenizer.call_args[0][0]
    assert called_prompt.startswith("paraphrase: ")


def test_generate_local_paraphrases_handles_load_failure() -> None:
    local_paraphraser._MODEL_CACHE.clear()
    with patch.object(local_paraphraser, "_load_paraphrase_model", side_effect=RuntimeError("offline")):
        assert local_paraphraser.generate_local_paraphrases("Kalimat uji.", count=3) == []
