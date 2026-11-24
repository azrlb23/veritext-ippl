import os
import re
import sys
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.api.v1.reports import preview_pdf
from app.models.user import User
from app.services.annotated_pdf_service import _markup_paragraph, build_annotated_pdf_response


async def _read_stream(resp) -> bytes:
    return b"".join([p if isinstance(p, bytes) else p.encode("utf-8") async for p in resp.body_iterator])


def _sent(idx: int, orig: str, curr: str | None = None, modified: bool = False, start: int = 0, end: int = 20):
    return SimpleNamespace(
        id=uuid.uuid4(), sentence_index=idx, sentence_text=orig, original_text=orig,
        current_text=curr or orig, is_modified=modified, start_char=start, end_char=end,
    )


def test_markup_paragraph_escapes_xml_and_maps_colors():
    text = "Cek <x & y>\nBaris dua\nTiga\nEmpat"
    annos = [
        {"start": 100, "end": 111, "color": "RED"},
        {"start": 112, "end": 121, "color": "ORANGE"},
        {"start": 122, "end": 126, "tier": "T3"},
        {"start": 127, "end": 132, "color": "RESOLVED_GREEN"},
    ]
    markup = _markup_paragraph(text, 100, annos)
    assert '<font backColor="#FEE2E2">Cek &lt;x &amp; y&gt;</font>' in markup
    assert '<font backColor="#FFEDD5">Baris dua</font>' in markup
    assert '<font backColor="#FEF9C3">Tiga</font>' in markup
    assert '<font backColor="#DCFCE7">Empat</font>' in markup
    assert "<br/>" in markup


async def test_annotated_pdf_produces_valid_inline_pdf_with_highlights():
    s0 = _sent(0, "Bab 1 Pendahuluan", start=0, end=17)
    s1 = _sent(1, "Nilai a < b & c > d terdeteksi leksikal.", start=20, end=60)
    s2 = _sent(2, "Kalimat semantik oranye.", start=62, end=86)
    s3 = _sent(3, "Kalimat stilometri kuning.", start=88, end=114)
    s4 = _sent(4, "Kalimat lama.", "Kalimat baru hasil revisi <aman & sah>.", True, 116, 129)
    annos = [
        {"sentence_id": str(s1.id), "start": 20, "end": 60, "color": "RED", "tier": "T1", "text_snippet": s1.sentence_text},
        {"sentence_id": str(s2.id), "start": 62, "end": 86, "color": "ORANGE", "tier": "T2", "text_snippet": s2.sentence_text},
        {"sentence_id": str(s3.id), "start": 88, "end": 114, "color": "YELLOW", "tier": "T3", "text_snippet": s3.sentence_text},
        {"sentence_id": str(s4.id), "start": 116, "end": 129, "color": "RESOLVED_GREEN", "tier": "T1", "text_snippet": s4.current_text},
    ]
    uid = uuid.uuid4()
    task = SimpleNamespace(id=uuid.uuid4(), user_id=uid, user=SimpleNamespace(id=uid, role="FREE"), document=None)
    report = SimpleNamespace(id=uuid.uuid4(), audit_task_id=task.id, document_title="Naskah <Uji> & PDF.docx", heatmap_annotations=annos, audit_task=task)

    resp = build_annotated_pdf_response(report, [s0, s1, s2, s3, s4])
    raw_pdf = await _read_stream(resp)
    assert resp.media_type == "application/pdf"
    assert resp.headers.get("content-disposition") == 'inline; filename="preview.pdf"'
    assert raw_pdf.startswith(b"%PDF")
    assert re.search(rb"/Type\s*/Page(?![a-zA-Z])", raw_pdf)


def test_annotated_pdf_raises_400_for_empty_document():
    task = SimpleNamespace(id=uuid.uuid4(), user_id=uuid.uuid4(), user=None, document=None)
    report = SimpleNamespace(id=uuid.uuid4(), audit_task_id=task.id, document_title="Kosong.docx", heatmap_annotations=[], audit_task=task)
    with pytest.raises(HTTPException) as exc:
        build_annotated_pdf_response(report, [])
    assert exc.value.status_code == 400
    assert "EMPTY_DOCUMENT" in exc.value.detail


async def test_preview_pdf_endpoint_allows_free_owner():
    free_user = User(id=uuid.uuid4(), role="FREE")
    s0 = _sent(0, "Paragraf uji <a & b>.", start=0, end=21)
    task = SimpleNamespace(id=uuid.uuid4(), user_id=free_user.id, user=free_user, document=None)
    report = SimpleNamespace(id=uuid.uuid4(), audit_task_id=task.id, document_title="Uji.docx", heatmap_annotations=[], audit_task=task)

    db = AsyncMock()
    res_report = MagicMock(scalar_one_or_none=MagicMock(return_value=report))
    res_sents = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[s0]))))
    db.execute.side_effect = [res_report, res_sents]

    resp = await preview_pdf(report.id, current_user=free_user, db=db)
    raw_pdf = await _read_stream(resp)
    assert resp.headers.get("content-disposition") == 'inline; filename="preview.pdf"'
    assert raw_pdf.startswith(b"%PDF")
