from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.database import get_db
from app.main import app
from app.models.audit import AuditReport, AuditSentence, AuditTask
from app.services.assistant_batch_service import fetch_priority_sentences
from app.services.local_similarity_check import measure_paraphrase_similarity


class _FakeResult:
    def __init__(self, items=None):
        self._items = items or []

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None

    def scalars(self):
        return self

    def all(self):
        return list(self._items)


class _FakeDB:
    def __init__(self, responses):
        self._responses = list(responses)

    async def execute(self, _stmt):
        return self._responses.pop(0)


def test_measure_paraphrase_similarity_identical_vs_rewritten():
    orig = "Penerapan algoritma pembelajaran mesin meningkatkan akurasi klasifikasi dokumen ilmiah secara signifikan."
    same = measure_paraphrase_similarity(orig, orig)
    assert same["lexical_overlap_pct"] == 100.0 and same["word_overlap_pct"] == 100.0
    assert same["is_improved"] is False

    rewritten = "Kajian empiris membuktikan metode komputasi modern mampu menajamkan ketepatan pemilahan naskah akademik."
    diff = measure_paraphrase_similarity(orig, rewritten)
    assert diff["lexical_overlap_pct"] < 35.0 and diff["word_overlap_pct"] < 35.0
    assert diff["is_improved"] is True


def test_check_similarity_endpoint_returns_api_response():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid.uuid4(), role="FREE")
    try:
        resp = TestClient(app).post("/api/v1/chat/check-similarity", json={
            "original_text": "Sistem evaluasi otomatis mengidentifikasi kesamaan leksikal pada naskah.",
            "rewritten_text": "Perangkat lunak audit mendeteksi kemiripan susunan frasa dalam tulisan.",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True and body["data"]["lexical_overlap_pct"] < 35.0 and body["data"]["is_improved"] is True
    finally:
        app.dependency_overrides.pop(get_current_user, None)


async def test_fetch_priority_sentences_orders_and_filters():
    user_id, doc_id = uuid.uuid4(), uuid.uuid4()
    report = AuditReport(id=uuid.uuid4())
    task = AuditTask(id=uuid.uuid4(), document_id=doc_id, user_id=user_id, status="SUCCESS", report=report)
    sentences = [
        AuditSentence(id=uuid.uuid4(), sentence_index=0, sentence_text="Y1", match_type="YELLOW", similarity_score=95.0, is_modified=False),
        AuditSentence(id=uuid.uuid4(), sentence_index=1, sentence_text="O1", match_type="ORANGE", similarity_score=80.0, is_modified=False),
        AuditSentence(id=uuid.uuid4(), sentence_index=2, sentence_text="R2", match_type="RED", similarity_score=70.0, is_modified=False),
        AuditSentence(id=uuid.uuid4(), sentence_index=3, sentence_text="R1", current_text="R1 cur", match_type="RED", similarity_score=92.0, is_modified=False),
        AuditSentence(id=uuid.uuid4(), sentence_index=4, sentence_text="M1", match_type="RED", similarity_score=99.0, is_modified=True),
        AuditSentence(id=uuid.uuid4(), sentence_index=5, sentence_text="N1", match_type="NONE", similarity_score=10.0, is_modified=False),
    ]
    res = await fetch_priority_sentences(_FakeDB([_FakeResult([task]), _FakeResult(sentences)]), user_id, doc_id, limit=3)
    assert res["audit_task_id"] == str(task.id) and res["report_id"] == str(report.id)
    assert [i["sentence_id"] for i in res["items"]] == [str(sentences[3].id), str(sentences[2].id), str(sentences[1].id)]
    assert res["items"][0]["text"] == "R1 cur"


async def test_fetch_priority_sentences_404_and_http_endpoint():
    with pytest.raises(HTTPException) as exc:
        await fetch_priority_sentences(_FakeDB([_FakeResult([])]), uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404

    user, doc_id = SimpleNamespace(id=uuid.uuid4(), role="FREE"), uuid.uuid4()
    task = AuditTask(id=uuid.uuid4(), document_id=doc_id, user_id=user.id, status="SUCCESS")
    s_red = AuditSentence(id=uuid.uuid4(), sentence_index=0, sentence_text="Flagged", match_type="RED", similarity_score=88.0, is_modified=False)
    http_db = _FakeDB([_FakeResult([task]), _FakeResult([s_red])])

    async def _override_db():
        yield http_db

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = _override_db
    try:
        resp = TestClient(app).get(f"/api/v1/chat/priority-sentences?document_id={doc_id}&limit=10")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["audit_task_id"] == str(task.id) and data["report_id"] is None
        assert len(data["items"]) == 1 and data["items"][0]["match_type"] == "RED"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db, None)
