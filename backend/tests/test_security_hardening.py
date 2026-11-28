from __future__ import annotations

import logging
import socket
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from app.api.deps import get_current_user
from app.core import email as email_mod
from app.core.database import get_db
from app.core.rate_limiter import extract_client_ip
from app.core.url_guard import escape_ilike, extract_report_allowed_urls, is_safe_public_url
from app.llm.gemini_client import GeminiFlashClient
from app.main import app
from app.models.user import User
from app.models.wallet import TokenWallet
from app.schemas.billing import MidtransWebhookPayload
from app.schemas.chat import ApplyParaphraseRequest, ParaphraseRequest
from app.services import billing_webhook_helper as billing_helper
from app.services.assistant_service import AssistantService


def test_ssrf_guard_blocks_private_and_allows_public():
    for url in ("http://127.0.0.1/x", "http://169.254.169.254/latest/meta-data", "http://localhost:8000", "ftp://example.com"):
        assert is_safe_public_url(url) is False
    fake_addr = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
    with patch("app.core.url_guard.socket.getaddrinfo", return_value=fake_addr):
        assert is_safe_public_url("https://example.com/paper") is True
    assert is_safe_public_url("http://93.184.216.34/doc") is True


def test_extract_report_allowed_urls():
    report = SimpleNamespace(
        matched_sources=[{"source_url": "https://a.example/1"}],
        heatmap_annotations=[{"url": "https://b.example/2", "secondary_sources": [{"source_url": "https://c.example/3"}]}],
    )
    assert extract_report_allowed_urls(report) == {"https://a.example/1", "https://b.example/2", "https://c.example/3"}


def test_rate_limiter_extract_client_ip():
    req_real = SimpleNamespace(headers={"x-real-ip": "203.0.113.10", "x-forwarded-for": "198.51.100.1, 192.0.2.5"}, client=SimpleNamespace(host="127.0.0.1"))
    assert extract_client_ip(req_real) == "203.0.113.10"
    req_xff = SimpleNamespace(headers={"x-forwarded-for": "198.51.100.1, 192.0.2.5"}, client=SimpleNamespace(host="127.0.0.1"))
    assert extract_client_ip(req_xff) == "192.0.2.5"


def test_midtrans_prod_fail_closed(monkeypatch):
    monkeypatch.setattr(billing_helper.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(billing_helper.settings, "MIDTRANS_SIGNATURE_KEY", "")
    monkeypatch.setattr(billing_helper.settings, "MIDTRANS_SERVER_KEY", "SB-Mid-server-DemoServerKey")
    payload = MidtransWebhookPayload(order_id="ORD-1", status_code="200", gross_amount="25000", signature_key="sig", transaction_status="settlement")
    with pytest.raises(HTTPException) as exc:
        billing_helper.verify_midtrans_signature(payload)
    assert exc.value.status_code == 500


def test_paraphrase_schema_and_paywall():
    with pytest.raises(ValidationError):
        ParaphraseRequest(sentence_id=uuid.uuid4(), mode="CUSTOM")
    with pytest.raises(ValidationError):
        ApplyParaphraseRequest(sentence_id=uuid.uuid4(), selected_text="no")
    user = User(role="FREE")
    wallet = TokenWallet(ai_trial_remaining=3, balance=0, ai_chat_allowance_remaining=0)
    with pytest.raises(HTTPException) as exc:
        AssistantService.check_ai_quota_available(user, wallet, mode="UNKNOWN")
    assert exc.value.status_code == 403


def test_chat_sentence_idor_returns_404_before_llm():
    user = User(id=uuid.uuid4(), role="FREE", email="u@example.com", is_active=True)
    wallet = TokenWallet(user_id=user.id, ai_trial_remaining=3, balance=0, ai_chat_allowance_remaining=0)
    db = SimpleNamespace(execute=AsyncMock(side_effect=[SimpleNamespace(scalar_one_or_none=lambda: wallet), SimpleNamespace(scalar_one_or_none=lambda: None)]))

    async def _override_db():
        yield db

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = _override_db
    try:
        with patch("app.api.v1.chat.DualEngineLLMGateway") as mock_gw:
            resp = TestClient(app).post("/api/v1/chat/message", json={"sentence_id": str(uuid.uuid4()), "prompt": "Bantu perbaiki kalimat ini."})
        assert resp.status_code == 404
        mock_gw.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_escape_ilike():
    assert escape_ilike(r"a\b%c_d") == r"a\\b\%c\_d"


def test_gemini_client_uses_header_not_query_param():
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {"candidates": []}
    mock_http = MagicMock()
    mock_http.post.return_value = mock_resp
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_http
    with patch("app.llm.gemini_client.httpx.Client", return_value=mock_cm):
        res = GeminiFlashClient(api_key="secret-key", model="gemini-3.6-flash", timeout_s=5)._post_model("gemini-3.6-flash", {"contents": []})
    assert res == {"candidates": []}
    _, kwargs = mock_http.post.call_args
    assert kwargs["headers"] == {"Content-Type": "application/json", "x-goog-api-key": "secret-key"}
    assert "params" not in kwargs


def test_email_prod_redaction_and_html_escape(monkeypatch, caplog, capsys):
    monkeypatch.setattr(email_mod.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(email_mod.settings, "SMTP_HOST", "")
    with caplog.at_level(logging.INFO, logger=email_mod.logger.name):
        sent = email_mod.send_password_reset_email("u@example.com", "https://app.test/reset?t=secret", user_name="User", otp_code="654321")
    assert sent is False
    combined = caplog.text + capsys.readouterr().out
    assert "654321" not in combined
    assert "https://app.test/reset?t=secret" not in combined

    monkeypatch.setattr(email_mod.settings, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(email_mod.settings, "SMTP_PORT", 587)
    monkeypatch.setattr(email_mod.settings, "SMTP_TLS", True)
    monkeypatch.setattr(email_mod.settings, "SMTP_USER", "")
    monkeypatch.setattr(email_mod.settings, "SMTP_PASSWORD", "")
    smtp_srv = MagicMock()
    with patch("app.core.email.smtplib.SMTP", return_value=smtp_srv):
        ok = email_mod.send_password_reset_email("u@example.com", "https://app.test/reset", user_name="<script>alert(1)</script>", otp_code="123456")
    assert ok is True
    html_body = smtp_srv.send_message.call_args[0][0].get_payload()[1].get_payload()
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_body
    assert "<script>" not in html_body
