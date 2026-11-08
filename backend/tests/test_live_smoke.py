import uuid
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.engine.preprocessor import SentenceSpan
from app.llm.gateway import DualEngineLLMGateway
from app.main import app
from app.models.audit import AuditReport, AuditSentence
from app.models.user import User
from app.models.wallet import TokenWallet
from app.services.assistant_service import AssistantService


def test_live_server_health_and_root():
    client = TestClient(app)
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "healthy"

    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["status"] == "ONLINE"


def test_openapi_schema_routes_and_admin_readonly():
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})

    expected_prefixes = [
        "/api/v1/auth/", "/api/v1/documents", "/api/v1/audits",
        "/api/v1/chat/", "/api/v1/reports", "/api/v1/billing/", "/api/v1/admin/",
    ]
    for prefix in expected_prefixes:
        matching = [p for p in paths if p.startswith(prefix)]
        assert len(matching) > 0, f"Expected route prefix {prefix} not mounted in OpenAPI"

    admin_paths = [p for p in paths if p.startswith("/api/v1/admin/")]
    assert len(admin_paths) >= 5
    for p in admin_paths:
        methods = set(paths[p].keys()) - {"parameters"}
        assert methods == {"get"}, f"Admin route {p} exposed non-GET methods: {methods}"


def test_dual_engine_llm_gateway_and_assistant_e2e():
    gemini_mock = MagicMock()
    deepseek_mock = MagicMock()
    gemini_mock.model = "gemini-2.5-flash"
    deepseek_mock.model = "deepseek-v4.1-flash"
    gemini_mock.generate_json.return_value = {"ai_probability": 12.5, "suspicious_sentences": []}
    gemini_mock.generate_text.return_value = (
        '[{"option_id": 1, "style": "Formal", "text": "Hasil kajian menunjukkan.", "predicted_score": 7.0}]'
    )

    gateway = DualEngineLLMGateway(gemini_client=gemini_mock, deepseek_client=deepseek_mock, strategy="gemini_first")

    spans = [
        SentenceSpan(
            index=0,
            text="Penelitian ini menganalisis model hybrid.",
            start_char=0,
            end_char=42,
            word_count=6,
            is_citation=False,
        )
    ]
    eval_res, engine = gateway.evaluate_sentences(spans)
    assert eval_res is not None
    assert eval_res["ai_probability"] == 12.5
    assert "Gemini" in engine

    text_res, engine_text = gateway.generate_text_with_failover("Minta parafrase.")
    assert text_res is not None
    assert "Gemini" in engine_text

    variations, active_eng = AssistantService.generate_paraphrase_variations(
        "Penelitian ini menganalisis model hybrid.", "SENTENCE", gateway=gateway
    )
    assert len(variations) >= 1
    assert "Gemini" in active_eng

    AssistantService.check_academic_guardrail("Mohon evaluasi parafrase ini.")

    user = User(role="PREMIUM")
    wallet = TokenWallet(balance=3, ai_trial_remaining=0, ai_chat_allowance_remaining=0)
    trial, bal, allow, deducted = AssistantService.consume_ai_quota(user, wallet)
    assert (trial, bal, allow, deducted) == (0, 2, 9, True)

    sent_id = uuid.uuid4()
    sentence = AuditSentence(
        id=sent_id, sentence_text="Original", current_text="Original", match_type="RED", similarity_score=85.0
    )
    report = AuditReport(score_composite=85.0)
    result = AssistantService.apply_paraphrase_in_place(sentence, "Hasil kajian menunjukkan.", [sentence], report)
    assert result["match_type"] == "RESOLVED_GREEN"
    assert result["new_similarity"] == 6.0
    assert report.score_composite == 6.0
