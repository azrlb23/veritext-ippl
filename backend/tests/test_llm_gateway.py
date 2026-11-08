from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from app.engine.preprocessor import SentenceSpan
from app.llm.deepseek_client import DeepSeekRouterClient
from app.llm.gateway import DualEngineLLMGateway
from app.llm.gemini_client import GeminiFlashClient, clean_llm_json


class TestLLMGatewayAndClients(unittest.TestCase):
    def test_clean_llm_json(self):
        raw = "```json\n{\"ai_probability\": 75.0, \"suspicious_sentences\": [],}\n```"
        parsed = clean_llm_json(raw)
        self.assertEqual(parsed["ai_probability"], 75.0)

    def test_gemini_client_generate_json(self):
        client = GeminiFlashClient(api_key="mock-key", model="gemini-2.5-flash")
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": '{"ai_probability": 80.0}'}]}}]
        }
        with patch("httpx.Client.post", return_value=mock_resp):
            res = client.generate_json("test prompt")
        self.assertIsNotNone(res)
        self.assertEqual(res["ai_probability"], 80.0)

    def test_deepseek_client_generate_json(self):
        client = DeepSeekRouterClient(api_key="mock-key", model="deepseek-v4.1-flash")
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '{"ai_probability": 70.0}'}}]
        }
        with patch("httpx.Client.post", return_value=mock_resp):
            res = client.generate_json("test prompt")
        self.assertIsNotNone(res)
        self.assertEqual(res["ai_probability"], 70.0)

    def test_gateway_failover_gemini_to_deepseek(self):
        gemini = GeminiFlashClient(api_key="mock-key")
        deepseek = DeepSeekRouterClient(api_key="mock-key")
        gateway = DualEngineLLMGateway(gemini_client=gemini, deepseek_client=deepseek, strategy="gemini_first")

        with patch.object(gemini, "generate_json", return_value=None), \
             patch.object(deepseek, "generate_json", return_value={"ai_probability": 65.0, "suspicious_sentences": []}):
            sentences = [
                SentenceSpan(index=0, text="Kalimat pembuka yang cukup panjang.", start_char=0, end_char=35, word_count=5, is_citation=False)
            ]
            data, engine_name = gateway.evaluate_sentences(sentences)
            self.assertIsNotNone(data)
            self.assertEqual(data["ai_probability"], 65.0)
            self.assertIn("DeepSeek", engine_name)

    def test_gateway_generate_text_failover(self):
        gemini = GeminiFlashClient(api_key="mock-key")
        deepseek = DeepSeekRouterClient(api_key="mock-key")
        gateway = DualEngineLLMGateway(gemini_client=gemini, deepseek_client=deepseek, strategy="gemini_first")

        with patch.object(gemini, "generate_text", return_value=None), \
             patch.object(deepseek, "generate_text", return_value="Parafrase hasil DeepSeek"):
            text, engine = gateway.generate_text_with_failover("Parafrase kalimat ini")
            self.assertEqual(text, "Parafrase hasil DeepSeek")
            self.assertIn("DeepSeek", engine)


if __name__ == "__main__":
    unittest.main()
