from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1 import auth_google_signup
from app.api.v1 import billing as billing_router
from app.core.config import settings
from app.core.security import create_signup_ticket, get_password_hash
from app.models.audit import AuditTask
from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.invoice import Invoice
from app.models.user import User
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.auth import GoogleCompleteRequest, UserLoginRequest
from app.schemas.billing import MidtransWebhookPayload
from app.services.admin_monitoring_service import get_system_health_metrics
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.document_service import DocumentService


class _FakeResult:
    def __init__(self, items=None, scalar_val=None):
        self._items = items or []
        self._scalar = scalar_val

    def scalar(self):
        return self._scalar

    def scalar_one_or_none(self):
        return self._items[0] if self._items else self._scalar

    def scalars(self):
        return self

    def all(self):
        return self._items


class _FakeDB:
    def __init__(self, handler=None):
        self._handler = handler or (lambda s: _FakeResult())
        self.added = []
        self.committed = False
        self.flushed = False

    async def execute(self, stmt):
        return self._handler(stmt)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True
        for obj in self.added:
            if hasattr(obj, "id") and getattr(obj, "id", None) is None:
                obj.id = uuid.uuid4()

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        pass


@pytest.mark.asyncio
async def test_health_metrics_reads_task_counts_and_redis_ping():
    call_idx = 0

    def handler(_stmt):
        nonlocal call_idx
        call_idx += 1
        if call_idx == 1:
            return _FakeResult(scalar_val=1)
        if call_idx in (2, 3, 4):
            return _FakeResult(scalar_val=10)
        return _FakeResult(items=[("PROCESSING", 3), ("QUEUED", 7)])

    db = _FakeDB(handler)
    fake_client = MagicMock()
    fake_client.ping = AsyncMock(return_value=True)
    fake_client.aclose = AsyncMock()

    with patch("redis.asyncio.from_url", return_value=fake_client):
        metrics = await get_system_health_metrics(db)

    assert metrics.celery_active_tasks == 3
    assert metrics.queue_depth == 7
    assert metrics.redis_status == "HEALTHY"


@pytest.mark.asyncio
async def test_health_metrics_redis_down_fallback():
    db = _FakeDB(lambda _s: _FakeResult(scalar_val=0))
    with patch("redis.asyncio.from_url", side_effect=ConnectionError("refused")):
        metrics = await get_system_health_metrics(db)
    assert metrics.redis_status == "DOWN"


@pytest.mark.asyncio
async def test_get_wallet_returns_recent_transactions_and_webhook_logs_audit():
    user_id = uuid.uuid4()
    wallet = TokenWallet(id=uuid.uuid4(), user_id=user_id, balance=20, updated_at=datetime.now(timezone.utc))
    tx = TokenTransaction(
        id=uuid.uuid4(),
        wallet_id=wallet.id,
        transaction_type="CREDIT_TOPUP",
        amount=15,
        balance_after=20,
        created_at=datetime.now(timezone.utc),
    )

    with (
        patch.object(BillingService, "get_wallet", new=AsyncMock(return_value=wallet)),
        patch.object(BillingService, "get_recent_transactions", new=AsyncMock(return_value=[tx])),
    ):
        resp = await billing_router.get_wallet(current_user=SimpleNamespace(id=user_id), db=_FakeDB())

    assert len(resp.data.recent_transactions) == 1
    assert resp.data.recent_transactions[0].transaction_type == "CREDIT_TOPUP"

    order_id = "VT-LOG-001"
    sig = hashlib.sha512(f"{order_id}20025000.00{settings.MIDTRANS_SERVER_KEY}".encode()).hexdigest()
    inv = Invoice(
        id=uuid.uuid4(), user_id=user_id, order_id=order_id,
        token_amount=15, gross_amount=25000, status="PENDING", package_name="Starter",
    )
    user = User(id=user_id, full_name="A", email="a@test.id", password_hash="x", role="FREE")
    idx = 0

    def wh_handler(_stmt):
        nonlocal idx
        idx += 1
        if idx == 1:
            return _FakeResult([inv])
        if idx == 2:
            return _FakeResult([wallet])
        return _FakeResult([user])

    wh_db = _FakeDB(wh_handler)
    payload = MidtransWebhookPayload(
        order_id=order_id, status_code="200", gross_amount="25000.00",
        signature_key=sig, transaction_status="settlement", fraud_status="accept",
    )
    await BillingService.process_midtrans_webhook(wh_db, payload)
    logs = [x for x in wh_db.added if isinstance(x, AuditLog)]
    assert len(logs) == 1
    assert logs[0].action_type == "BILLING_TOPUP"


@pytest.mark.asyncio
async def test_document_delete_revokes_active_celery_tasks_and_logs_purge():
    doc = Document(id=uuid.uuid4(), user_id=uuid.uuid4(), original_filename="skripsi.pdf", stored_filename="")
    db = _FakeDB(lambda _s: _FakeResult(items=["celery-task-123"]))
    mock_celery = MagicMock()

    with patch("app.workers.celery_app.celery_app", mock_celery):
        await DocumentService.delete_document(db, doc)

    mock_celery.control.revoke.assert_called_once_with("celery-task-123", terminate=True)
    logs = [x for x in db.added if isinstance(x, AuditLog)]
    assert len(logs) == 1
    assert logs[0].action_type == "DOCUMENT_PURGE"
    assert db.committed is True


@pytest.mark.asyncio
async def test_authenticate_user_records_auth_login_audit_log():
    user = User(
        id=uuid.uuid4(),
        full_name="Test User",
        email="login@test.id",
        password_hash=get_password_hash("sandikuat123"),
        role="FREE",
        is_active=True,
        failed_login_count=0,
    )
    db = _FakeDB(lambda _s: _FakeResult(items=[user]))
    req = UserLoginRequest(email="login@test.id", password="sandikuat123")
    _, access_tok, _ = await AuthService.authenticate_user(db, req, user_agent="pytest", ip_address="127.0.0.1")
    assert access_tok
    logs = [x for x in db.added if isinstance(x, AuditLog)]
    assert len(logs) == 1
    assert logs[0].action_type == "AUTH_LOGIN"
    assert logs[0].actor_ip == "127.0.0.1"


@pytest.mark.asyncio
async def test_save_uploaded_file_and_create_task_logs_audit_submit():
    user_id = uuid.uuid4()
    wallet = TokenWallet(id=uuid.uuid4(), user_id=user_id, balance=10)
    db = _FakeDB(lambda _s: _FakeResult(items=[wallet]))
    fake_file = SimpleNamespace(filename="bab1.pdf", content_type="application/pdf")

    with (
        patch("app.services.document_service.validate_file"),
        patch("app.services.document_service.stage_upload", new=AsyncMock(return_value=("stored.pdf", 1024, "abc", 500, 1))),
        patch("app.services.document_service.debit_wallet", new=AsyncMock(return_value=wallet)),
        patch("app.workers.tasks.preprocess_and_audit.delay", return_value=SimpleNamespace(id="celery-new-1")),
    ):
        doc, task = await DocumentService.save_uploaded_file_and_create_task(db, user_id, fake_file)

    assert doc.original_filename == "bab1.pdf"
    assert task.celery_task_id == "celery-new-1"
    logs = [x for x in db.added if isinstance(x, AuditLog)]
    assert len(logs) == 2
    by_type = {x.action_type: x for x in logs}
    assert set(by_type) == {"AUDIT_SUBMIT", "TOKEN_DEBIT"}
    assert by_type["AUDIT_SUBMIT"].meta_data["token_cost"] == 1
    assert by_type["TOKEN_DEBIT"].meta_data["amount"] == 1


@pytest.mark.asyncio
async def test_google_complete_aligned_with_8_char_password_rule():
    ticket = create_signup_ticket(email="google8@test.id", name="Google User")
    db = _FakeDB(lambda _s: _FakeResult(items=[]))
    req = GoogleCompleteRequest(ticket=ticket, full_name="Google User", password="sandikuat")
    resp = await auth_google_signup.google_complete(req=req, db=db)
    assert resp.success is True
    assert resp.data.user.email == "google8@test.id"
