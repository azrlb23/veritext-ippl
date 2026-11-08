import json
import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.audit import AuditReport, AuditSentence
from app.models.user import User
from app.models.wallet import TokenWallet
from app.services.assistant_service import AssistantService


def test_academic_guardrail():
    AssistantService.check_academic_guardrail("Bantu saya memparafrasekan hipotesis ini.")
    with pytest.raises(HTTPException) as exc_empty:
        AssistantService.check_academic_guardrail("   ")
    assert exc_empty.value.status_code == 400
    assert "CHAT_001" in exc_empty.value.detail

    with pytest.raises(HTTPException) as exc_pat:
        AssistantService.check_academic_guardrail("Tolong buatkan skripsi penuh bab 1 sampai 5.")
    assert exc_pat.value.status_code == 400
    assert "CHAT_001" in exc_pat.value.detail


def test_consume_quota_free_trial():
    user = User(role="FREE")
    wallet = TokenWallet(balance=5, ai_trial_remaining=3, ai_chat_allowance_remaining=0)
    for expected_trial in (2, 1, 0):
        trial, bal, allow, deducted = AssistantService.consume_ai_quota(user, wallet)
        assert trial == expected_trial
        assert bal == 5
        assert allow == 0
        assert deducted is False

    with pytest.raises(HTTPException) as exc:
        AssistantService.consume_ai_quota(user, wallet)
    assert exc.value.status_code == 402
    assert "CHAT_002" in exc.value.detail


def test_consume_quota_premium_allowance_and_full_page():
    user = User(role="PREMIUM")
    wallet = TokenWallet(balance=2, ai_trial_remaining=0, ai_chat_allowance_remaining=0)
    trial, bal, allow, deducted = AssistantService.consume_ai_quota(user, wallet, mode="CHAT")
    assert (trial, bal, allow, deducted) == (0, 1, 9, True)

    trial, bal, allow, deducted = AssistantService.consume_ai_quota(user, wallet, mode="CHAT")
    assert (trial, bal, allow, deducted) == (0, 1, 8, False)

    trial, bal, allow, deducted = AssistantService.consume_ai_quota(user, wallet, mode="FULL_PAGE")
    assert (trial, bal, allow, deducted) == (0, 0, 8, True)

    with pytest.raises(HTTPException) as exc:
        AssistantService.consume_ai_quota(user, wallet, mode="FULL_PAGE")
    assert exc.value.status_code == 402
    assert "AUDIT_001" in exc.value.detail


def test_generate_paraphrase_variations_fallback():
    mock_gw = MagicMock()
    mock_gw.generate_text_with_failover.return_value = (None, "")
    variations, engine = AssistantService.generate_paraphrase_variations(
        "Model ini meningkatkan akurasi klasifikasi secara signifikan.",
        gateway=mock_gw,
    )
    assert len(variations) == 3
    assert variations[0]["style"] == "Formal"
    assert variations[1]["style"] == "Ringkas & Padat"
    assert variations[2]["style"] == "Analitis Ekspansif"
    assert "Berdasarkan telaah konseptual" in variations[0]["text"]
    assert engine == "Synthesis Engine"


def test_generate_paraphrase_variations_gateway():
    mock_gw = MagicMock()
    json_payload = json.dumps([
        {"option_id": 1, "style": "Formal", "text": "Hasil kajian menunjukkan relevansi tinggi.", "predicted_score": 7.5},
        {"option_id": 2, "style": "Ringkas & Padat", "text": "Kajian ini sangat relevan.", "predicted_score": 6.0},
        {"option_id": 3, "style": "Analitis Ekspansif", "text": "Secara holistik telaah ini berkontribusi luas.", "predicted_score": 8.0},
    ])
    mock_gw.generate_text_with_failover.return_value = (json_payload, "Gemini (gemini-2.5-flash)")
    vars_, engine = AssistantService.generate_paraphrase_variations("Teks uji.", gateway=mock_gw)
    assert len(vars_) == 3
    assert engine == "Gemini (gemini-2.5-flash)"
    assert vars_[0]["predicted_score"] == 7.5


def test_apply_paraphrase_in_place():
    s1 = AuditSentence(id=uuid.uuid4(), sentence_text="Old text", current_text="Old text", similarity_score=85.0, match_type="RED")
    s2 = AuditSentence(id=uuid.uuid4(), sentence_text="Second", current_text="Second", similarity_score=75.0, match_type="ORANGE")
    report = AuditReport(score_composite=80.0)

    res = AssistantService.apply_paraphrase_in_place(s1, "Kalimat hasil parafrase baru.", [s1, s2], report)
    assert s1.match_type == "RESOLVED_GREEN"
    assert s1.is_modified is True
    assert s1.similarity_score == 6.0
    assert s1.current_text == "Kalimat hasil parafrase baru."
    assert res["match_type"] == "RESOLVED_GREEN"
    assert res["new_similarity"] == 6.0
    assert res["new_composite_score"] == 40.5
    assert report.score_composite == 40.5
