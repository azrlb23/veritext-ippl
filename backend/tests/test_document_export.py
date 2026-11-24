import io
import os
import sys
import types
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import docx
import pytest
from fastapi import HTTPException

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.api.v1.chat import apply_paraphrase
from app.api.v1.reports import export_document
from app.models.user import User
from app.models.wallet import TokenWallet
from app.schemas.chat import ApplyParaphraseRequest
from app.services.assistant_service import AssistantService
from app.services.document_export_service import build_revised_document_response, verify_export_integrity


async def _read_stream(resp) -> bytes:
    return b"".join([p if isinstance(p, bytes) else p.encode("utf-8") async for p in resp.body_iterator])


def _make_report(doc=None, owner_id=None):
    uid = owner_id or uuid.uuid4()
    task = SimpleNamespace(id=uuid.uuid4(), user_id=uid, user=SimpleNamespace(id=uid, role="PREMIUM"), document=doc)
    return SimpleNamespace(id=uuid.uuid4(), audit_task_id=task.id, document_title="Skripsi Uji.docx", audit_task=task)


def _sent(idx, orig, curr=None, modified=False, start=0, end=20):
    return SimpleNamespace(
        id=uuid.uuid4(), sentence_index=idx, sentence_text=orig, original_text=orig,
        current_text=curr or orig, is_modified=modified, start_char=start, end_char=end,
    )


async def test_export_docx_from_original_file_and_structured_fallback(tmp_path):
    src = tmp_path / "asal.docx"
    d = docx.Document()
    d.add_paragraph("Bab Satu Pendahuluan")
    d.add_paragraph("Kalimat lama yang terdeteksi plagiat.")
    d.save(str(src))

    s0 = _sent(0, "Bab Satu Pendahuluan", start=0, end=20)
    s1 = _sent(1, "Kalimat lama yang terdeteksi plagiat.", "Kalimat baru hasil parafrase akademik.", True, 22, 59)
    doc_meta = SimpleNamespace(storage_path=str(src), stored_filename="asal.docx", mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    with patch("app.services.report_text_builder.settings.UPLOAD_DIR", str(tmp_path)):
        resp_orig = build_revised_document_response(_make_report(doc_meta), [s0, s1], "docx")
    text_orig = "\n".join(p.text for p in docx.Document(io.BytesIO(await _read_stream(resp_orig))).paragraphs)
    assert "Kalimat baru hasil parafrase akademik." in text_orig
    assert "Kalimat lama yang terdeteksi plagiat." not in text_orig

    resp_fb = build_revised_document_response(_make_report(None), [s0, s1], "docx")
    text_fb = "\n".join(p.text for p in docx.Document(io.BytesIO(await _read_stream(resp_fb))).paragraphs)
    assert "Kalimat baru hasil parafrase akademik." in text_fb


async def test_export_pdf_produces_valid_pdf_bytes():
    s0 = _sent(0, "Pendahuluan Riset", start=0, end=17)
    s1 = _sent(1, "Kalimat lama.", "Kalimat revisi terverifikasi untuk ekspor PDF.", True, 19, 32)
    resp = build_revised_document_response(_make_report(None), [s0, s1], "pdf")
    raw_pdf = await _read_stream(resp)
    assert raw_pdf.startswith(b"%PDF")
    assert b"/Type /Page" in raw_pdf
    assert resp.media_type == "application/pdf"


def test_verify_export_integrity_rejects_corrupt_or_missing_sentence():
    buf = io.BytesIO()
    d = docx.Document()
    d.add_paragraph("Hanya teks pembuka saja.")
    d.save(buf)
    with pytest.raises(HTTPException) as exc_missing:
        verify_export_integrity(buf.getvalue(), "docx", ["Kalimat revisi yang wajib ada."], "Hanya teks pembuka saja.")
    assert exc_missing.value.status_code == 500
    assert "EXPORT_INTEGRITY_FAILED" in exc_missing.value.detail

    for bad_bytes, fmt in ((b"bukan-docx", "docx"), (b"bukan-pdf", "pdf"), (b"", "pdf")):
        with pytest.raises(HTTPException) as exc_bad:
            verify_export_integrity(bad_bytes, fmt, [], "Isi dokumen sah.")
        assert exc_bad.value.status_code == 500


async def test_free_user_blocked_from_paraphrase_and_export_403():
    free_user = User(id=uuid.uuid4(), role="FREE")
    wallet = TokenWallet(balance=5, ai_trial_remaining=3, ai_chat_allowance_remaining=0)
    for mode in ("SENTENCE", "PARAGRAPH", "FULL_PAGE"):
        with pytest.raises(HTTPException) as exc_q:
            AssistantService.check_ai_quota_available(free_user, wallet, mode=mode)
        assert exc_q.value.status_code == 403
        with pytest.raises(HTTPException) as exc_c:
            AssistantService.consume_ai_quota(free_user, wallet, mode=mode)
        assert exc_c.value.status_code == 403

    with pytest.raises(HTTPException) as exc_apply:
        await apply_paraphrase(ApplyParaphraseRequest(sentence_id=uuid.uuid4(), selected_text="Baru."), current_user=free_user, db=AsyncMock())
    assert exc_apply.value.status_code == 403

    report = _make_report(owner_id=free_user.id)
    db_mock = AsyncMock()
    db_mock.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=report))
    with pytest.raises(HTTPException) as exc_exp:
        await export_document(report.id, format="docx", current_user=free_user, db=db_mock)
    assert exc_exp.value.status_code == 403


def test_paraphrase_falls_back_to_local_transformers_when_gateway_fails():
    mock_gw = MagicMock()
    mock_gw.generate_text_with_failover.return_value = (None, "")
    fake_mod = types.ModuleType("app.llm.local_paraphraser")
    fake_mod.generate_local_paraphrases = lambda text, count=3: [
        {"option_id": i + 1, "style": "Lokal", "text": f"Variasi {i + 1}: {text}", "predicted_score": 8.0}
        for i in range(count)
    ]
    with patch.dict(sys.modules, {"app.llm.local_paraphraser": fake_mod}):
        vars_, engine = AssistantService.generate_paraphrase_variations("Teks akademik.", gateway=mock_gw)
    assert len(vars_) == 3
    assert engine == "Transformers (Local)"
