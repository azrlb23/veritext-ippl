from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1 import chat as chat_router
from app.core.config import settings
from app.engine.ai_detector import GeminiAIDetector
from app.engine.preprocessor import SentenceSpan
from app.models.audit import AuditReport, AuditSentence, AuditTask
from app.models.user import User
from app.models.wallet import TokenTransaction, TokenWallet
from app.schemas.billing import MidtransWebhookPayload
from app.services.assistant_service import AssistantService
from app.services.audit_service import AuditService
from app.services.billing_service import BillingService
from app.services.report_view_helper import build_report_pdf_response, check_report_authorization
from app.workers.task_helpers import _refund_audit_debit, handle_web_scan_refund


class _FakeResult:
    def __init__(self, items):
        self._items = items

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None

    def scalars(self):
        return self

    def all(self):
        return self._items


class _FakeAsyncDB:
    def __init__(self, handler):
        self._handler = handler
        self.added = []
        self.committed = False
        self.flushed = False

    async def execute(self, stmt):
        return self._handler(stmt)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True

    async def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_webhook_upgrades_free_user_to_premium_with_row_lock():
    from app.models.invoice import Invoice

    user_id = uuid.uuid4()
    order_id = "VT-UPGRADE-001"
    raw = f"{order_id}20025000.00{settings.MIDTRANS_SERVER_KEY}"
    sig = hashlib.sha512(raw.encode("utf-8")).hexdigest()

    invoice = Invoice(
        id=uuid.uuid4(),
        user_id=user_id,
        order_id=order_id,
        token_amount=15,
        gross_amount=25000,
        status="PENDING",
        package_name="Starter",
    )
    wallet = TokenWallet(id=uuid.uuid4(), user_id=user_id, balance=5)
    user = User(id=user_id, full_name="Free User", email="f@test.id", password_hash="x", role="FREE")
    stmts = []

    def handler(stmt):
        stmts.append(stmt)
        idx = len(stmts)
        if idx == 1:
            return _FakeResult([invoice])
        if idx == 2:
            return _FakeResult([wallet])
        return _FakeResult([user])

    db = _FakeAsyncDB(handler)
    payload = MidtransWebhookPayload(
        order_id=order_id,
        status_code="200",
        gross_amount="25000.00",
        signature_key=sig,
        transaction_status="settlement",
        fraud_status="accept",
    )
    ok = await BillingService.process_midtrans_webhook(db, payload)
    assert ok is True
    assert user.role == "PREMIUM"
    assert wallet.balance == 20
    assert getattr(stmts[2], "_for_update_arg", None) is not None


@pytest.mark.asyncio
async def test_cancel_task_uses_debit_amount_and_prevents_double_refund():
    user_id = uuid.uuid4()
    task = AuditTask(id=uuid.uuid4(), user_id=user_id, audit_depth="FULL", status="QUEUED")
    wallet = TokenWallet(id=uuid.uuid4(), user_id=user_id, balance=1)
    debit_tx = TokenTransaction(
        wallet_id=wallet.id, transaction_type="DEBIT_AUDIT", amount=-5, balance_after=1, reference_id=task.id
    )
    calls = 0

    def handler(_stmt):
        nonlocal calls
        calls += 1
        if calls == 1:
            return _FakeResult([task])
        if calls == 2:
            return _FakeResult([wallet])
        if calls == 3:
            return _FakeResult([debit_tx])
        return _FakeResult([])

    db = _FakeAsyncDB(handler)
    assert await AuditService.cancel_task(db, task.id, user_id) is True
    assert wallet.balance == 6
    refund_txs = [t for t in db.added if isinstance(t, TokenTransaction)]
    assert len(refund_txs) == 1
    assert refund_txs[0].amount == 5

    # Double refund blocked when CREDIT_REFUND already exists
    task2 = AuditTask(id=task.id, user_id=user_id, audit_depth="PROCESSING", status="PROCESSING")
    existing_refund = TokenTransaction(
        wallet_id=wallet.id, transaction_type="CREDIT_REFUND", amount=5, balance_after=6, reference_id=task.id
    )
    calls2 = 0

    def handler2(_stmt):
        nonlocal calls2
        calls2 += 1
        if calls2 == 1:
            return _FakeResult([task2])
        if calls2 == 2:
            return _FakeResult([wallet])
        if calls2 == 3:
            return _FakeResult([debit_tx])
        return _FakeResult([existing_refund])

    db2 = _FakeAsyncDB(handler2)
    await AuditService.cancel_task(db2, task2.id, user_id)
    assert wallet.balance == 6
    assert db2.added == []


def test_pdf_download_rejects_free_user_with_403():
    free_user = User(id=uuid.uuid4(), full_name="Free", role="FREE")
    task = AuditTask(id=uuid.uuid4(), user_id=free_user.id, user=free_user)
    report = AuditReport(id=uuid.uuid4(), verification_uuid=uuid.uuid4(), audit_task=task)

    check_report_authorization(report, free_user, allow_free=True)
    with pytest.raises(HTTPException) as exc1:
        check_report_authorization(report, free_user, allow_free=False)
    assert exc1.value.status_code == 403

    with pytest.raises(HTTPException) as exc2:
        build_report_pdf_response(report, current_user=free_user)
    assert exc2.value.status_code == 403


def test_worker_refund_helpers_use_for_update():
    task = AuditTask(id=uuid.uuid4(), user_id=uuid.uuid4(), audit_depth="FULL")
    wallet = TokenWallet(id=uuid.uuid4(), user_id=task.user_id, balance=2)
    debit = TokenTransaction(wallet_id=wallet.id, transaction_type="DEBIT_AUDIT", amount=-3, balance_after=2)

    q_task = MagicMock()
    q_task.filter.return_value.with_for_update.return_value.first.return_value = task
    q_debit = MagicMock()
    q_debit.filter.return_value.first.return_value = debit
    q_none = MagicMock()
    q_none.filter.return_value.first.return_value = None
    q_wallet = MagicMock()
    q_wallet.filter.return_value.with_for_update.return_value.first.return_value = wallet

    db = MagicMock()
    db.query.side_effect = [q_task, q_wallet, q_debit, q_none]
    _refund_audit_debit(db, task, "failed")
    assert wallet.balance == 5
    q_task.filter.return_value.with_for_update.assert_called_once()
    q_wallet.filter.return_value.with_for_update.assert_called_once()

    q_none2 = MagicMock()
    q_none2.filter.return_value.first.return_value = None
    q_wallet2 = MagicMock()
    q_wallet2.filter.return_value.with_for_update.return_value.first.return_value = wallet
    db2 = MagicMock()
    db2.query.side_effect = [q_none2, q_wallet2]
    res_obj = MagicMock(web_scan_available=False, web_scan_note="off")
    handle_web_scan_refund(db2, task, res_obj, MagicMock())
    assert wallet.balance == 6
    q_wallet2.filter.return_value.with_for_update.assert_called_once()


def test_apply_paraphrase_recomputes_composite_and_shifts_offsets():
    s1 = AuditSentence(
        id=uuid.uuid4(), sentence_index=0, sentence_text="Old text.", current_text="Old text.",
        match_type="RED", similarity_score=80.0, start_char=0, end_char=9,
    )
    s2 = AuditSentence(
        id=uuid.uuid4(), sentence_index=1, sentence_text="Second sentence.", current_text="Second sentence.",
        match_type="ORANGE", similarity_score=70.0, start_char=10, end_char=26,
    )
    report = AuditReport(
        score_lexical=80.0, score_semantic=70.0, score_stylometric=20.0, score_composite=67.5,
        heatmap_annotations=[
            {"start": 0, "end": 9, "color": "RED", "similarity": 80.0, "text_snippet": "Old text."},
            {"start": 10, "end": 26, "color": "ORANGE", "similarity": 70.0, "text_snippet": "Second sentence."},
        ],
    )
    new_text = "Kalimat pengganti baru yang berbeda."
    delta = len(new_text) - len("Old text.")
    res = AssistantService.apply_paraphrase_in_place(s1, new_text, [s1, s2], report)

    assert report.score_lexical == 0.0
    assert report.score_semantic == 70.0
    expected_comp = round(0.50 * 0.0 + 0.35 * 70.0 + 0.15 * 20.0, 2)
    assert report.score_composite == expected_comp
    assert res["new_composite_score"] == expected_comp
    assert s2.start_char == 10 + delta
    assert s2.end_char == 26 + delta
    assert report.heatmap_annotations[0]["color"] == "RESOLVED_GREEN"
    assert report.heatmap_annotations[0]["text_snippet"] == new_text
    assert report.heatmap_annotations[0]["end"] == 9 + delta
    assert report.heatmap_annotations[1]["start"] == 10 + delta
    assert report.heatmap_annotations[1]["end"] == 26 + delta


@pytest.mark.asyncio
async def test_chat_sentence_idor_returns_404():
    db = _FakeAsyncDB(lambda _stmt: _FakeResult([]))
    with pytest.raises(HTTPException) as exc:
        await chat_router._get_owned_sentence(db, uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404


def test_ai_detector_delegates_to_gateway_and_default_model():
    assert settings.GEMINI_MODEL == "gemini-3.8-flash"
    detector = GeminiAIDetector(api_key="k", openrouter_key="")
    spans = [SentenceSpan(index=0, text="Kalimat uji yang cukup panjang.", start_char=0, end_char=31, word_count=5, is_citation=False)]
    with patch.object(detector.gateway, "evaluate_sentences", return_value=({"ai_probability": 80.0, "suspicious_sentences": []}, "Gemini (gemini-3.8-flash)")) as mock_eval:
        res = detector.analyze_document("Kalimat uji yang cukup panjang.", spans)
    mock_eval.assert_called_once_with(spans)
    assert res.score_t3 > 0.0


def test_execute_audit_pipeline_persists_sentence_match_and_0_to_100_similarity():
    from app.models.document import Document
    from app.workers import tasks as worker_tasks

    task_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    task = AuditTask(id=task_id, document_id=doc_id, user_id=uuid.uuid4(), audit_depth="FULL", status="QUEUED")
    doc = Document(id=doc_id, user_id=task.user_id, original_filename="test.txt", stored_filename="missing.txt", mime_type="text/plain")
    db_sentences = []

    class _Query:
        def __init__(self, model):
            self.model = model

        def filter(self, *_args):
            return self

        def first(self):
            if self.model is AuditTask:
                return task
            if self.model is Document:
                return doc
            return None

        def delete(self):
            return 0

        def all(self):
            return db_sentences if self.model is AuditSentence else []

    class _SyncDB:
        def query(self, model):
            return _Query(model)

        def add(self, obj):
            if isinstance(obj, AuditSentence):
                db_sentences.append(obj)

        def commit(self):
            pass

        def rollback(self):
            pass

    fake_result = MagicMock(
        score_lexical=45.0,
        score_semantic=30.0,
        score_stylometric=20.0,
        score_composite=36.0,
        web_scan_available=True,
        matched_sources=[],
        heatmap_annotations=[
            {"start": 0, "end": 18, "color": "RED", "similarity": 0.85},
            {"start": 19, "end": 40, "color": "ORANGE", "similarity": 0.78},
        ],
    )
    fake_spans = [
        SentenceSpan(index=0, text="Kalimat pertama.", start_char=0, end_char=16, word_count=2, is_citation=False),
        SentenceSpan(index=1, text="Kalimat kedua panjang.", start_char=19, end_char=41, word_count=3, is_citation=False),
    ]
    with (
        patch.object(worker_tasks.TextPreprocessor, "segment_sentences", return_value=fake_spans),
        patch.object(worker_tasks, "load_corpus_indexes", return_value=({}, [])),
        patch.object(worker_tasks, "HybridAggregator") as mock_agg,
    ):
        mock_agg.return_value.run_pipeline.return_value = fake_result
        worker_tasks.execute_audit_pipeline(_SyncDB(), str(task_id), str(doc_id))

    assert db_sentences[0].match_type == "RED"
    assert db_sentences[0].similarity_score == 85.0
    assert db_sentences[1].match_type == "ORANGE"
    assert db_sentences[1].similarity_score == 78.0


@pytest.mark.asyncio
async def test_refund_failed_dispatch_is_atomic_and_idempotent():
    from app.services.upload_charging import refund_failed_dispatch

    user_id, task_id = uuid.uuid4(), uuid.uuid4()
    wallet = TokenWallet(id=uuid.uuid4(), user_id=user_id, balance=4)
    stmts = []

    def handler(stmt):
        stmts.append(stmt)
        if len(stmts) == 1:
            return _FakeResult([wallet])
        return _FakeResult([])

    db = _FakeAsyncDB(handler)
    await refund_failed_dispatch(db, task_id, user_id, 2)
    assert wallet.balance == 6
    assert getattr(stmts[0], "_for_update_arg", None) is not None
    refunds = [x for x in db.added if isinstance(x, TokenTransaction)]
    assert len(refunds) == 1 and refunds[0].transaction_type == "CREDIT_REFUND" and refunds[0].amount == 2

    existing = TokenTransaction(wallet_id=wallet.id, transaction_type="CREDIT_REFUND", amount=2, reference_id=task_id)
    calls2 = 0

    def handler2(_stmt):
        nonlocal calls2
        calls2 += 1
        return _FakeResult([wallet] if calls2 == 1 else [existing])

    db2 = _FakeAsyncDB(handler2)
    await refund_failed_dispatch(db2, task_id, user_id, 2)
    assert wallet.balance == 6 and db2.added == []


@pytest.mark.asyncio
async def test_audit_and_document_dispatch_failure_refunds_and_returns_503(monkeypatch):
    from unittest.mock import AsyncMock

    from app.models.document import Document
    from app.schemas.audit import AuditStartRequest
    from app.services.document_service import DocumentService

    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    user_id = uuid.uuid4()
    doc = Document(id=uuid.uuid4(), user_id=user_id, original_filename="paper.txt", word_count=300, status="READY")
    wallet = TokenWallet(id=uuid.uuid4(), user_id=user_id, balance=5)
    events = []

    class _SeqDB(_FakeAsyncDB):
        async def commit(self):
            events.append("commit")
            self.committed = True

        async def refresh(self, _obj):
            pass

    calls = 0

    def audit_handler(_stmt):
        nonlocal calls
        calls += 1
        if calls == 1:
            return _FakeResult([doc])
        if calls in (2, 3):
            return _FakeResult([wallet])
        return _FakeResult([])

    db = _SeqDB(audit_handler)

    def fail_delay(*_args):
        events.append("delay")
        raise RuntimeError("broker offline")

    with patch("app.workers.tasks.preprocess_and_audit.delay", side_effect=fail_delay):
        with pytest.raises(HTTPException) as exc:
            await AuditService.create_audit_task(db, user_id, AuditStartRequest(document_id=doc.id, audit_depth="FULL"), user_role="PREMIUM")
    assert exc.value.status_code == 503
    assert events[:2] == ["commit", "delay"]
    assert wallet.balance == 5
    tasks = [x for x in db.added if isinstance(x, AuditTask)]
    assert tasks[0].status == "FAILED"

    wallet2 = TokenWallet(id=uuid.uuid4(), user_id=user_id, balance=5)
    doc_calls = 0

    def doc_handler(_stmt):
        nonlocal doc_calls
        doc_calls += 1
        return _FakeResult([wallet2] if doc_calls in (1, 2) else [])

    db_doc = _SeqDB(doc_handler)
    fake_file = MagicMock(filename="naskah.txt", content_type="text/plain")
    with (
        patch("app.services.document_service.validate_file"),
        patch("app.services.document_service.stage_upload", new=AsyncMock(return_value=("s.txt", 10, "h", 300, 1))),
        patch("app.workers.tasks.preprocess_and_audit.delay", side_effect=RuntimeError("broker offline")),
    ):
        with pytest.raises(HTTPException) as exc2:
            await DocumentService.save_uploaded_file_and_create_task(db_doc, user_id, fake_file, user_role="PREMIUM")
    assert exc2.value.status_code == 503
    assert wallet2.balance == 5


@pytest.mark.asyncio
async def test_cancel_task_locks_audit_task_and_start_audit_enforces_limits():
    from unittest.mock import AsyncMock

    from app.api.v1 import audits as audits_router
    from app.schemas.audit import AuditStartRequest

    user_id = uuid.uuid4()
    task = AuditTask(
        id=uuid.uuid4(), document_id=uuid.uuid4(), user_id=user_id,
        audit_depth="FULL", status="QUEUED", progress_pct=0, created_at=datetime.now(timezone.utc),
    )
    stmts = []

    def handler(stmt):
        stmts.append(stmt)
        return _FakeResult([task] if len(stmts) == 1 else [])

    db = _FakeAsyncDB(handler)
    await AuditService.cancel_task(db, task.id, user_id)
    assert getattr(stmts[0], "_for_update_arg", None) is not None

    user = User(id=user_id, full_name="Tester", role="PREMIUM")
    req = AuditStartRequest(document_id=uuid.uuid4(), audit_depth="FULL")
    with (
        patch("app.api.v1.audits.enforce_rate_limit", new=AsyncMock()) as mock_rl,
        patch("app.api.v1.audits.enforce_active_audit_limit", new=AsyncMock()) as mock_al,
        patch("app.api.v1.audits.AuditService.create_audit_task", new=AsyncMock(return_value=task)),
    ):
        resp = await audits_router.start_audit(req=req, current_user=user, db=db)
    assert resp.success is True
    mock_rl.assert_awaited_once_with(user_id, "upload")
    mock_al.assert_awaited_once_with(db, user_id)
