from __future__ import annotations

import io
import json
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import docx
import pytest
from fastapi import HTTPException

from app.models.audit import AuditReport, AuditSentence, AuditTask
from app.models.document import Document
from app.services.assistant_service import AssistantService
from app.services.chat_context import load_audited_sentences_map, load_focus_sentence_context, select_relevant_sentences
from app.services.document_export_service import build_revised_document_response
from app.services.paraphrase_prompt import build_paraphrase_prompt
from app.services.report_text_builder import build_structured_report_view


def _sent(idx: int, text: str, match: str = "NONE", sim: float = 0.0, start: int = 0) -> AuditSentence:
    return AuditSentence(
        id=uuid.uuid4(), sentence_index=idx, sentence_text=text, current_text=text,
        match_type=match, similarity_score=sim, is_modified=False, start_char=start, end_char=start + len(text),
    )


def test_apply_paraphrase_rejects_identical_and_high_similarity_400():
    orig = "Penerapan algoritma pembelajaran mesin meningkatkan akurasi klasifikasi dokumen ilmiah secara signifikan."
    s1 = _sent(0, orig, match="RED", sim=90.0)
    with pytest.raises(HTTPException) as exc_same:
        AssistantService.apply_paraphrase_in_place(s1, orig, [s1], AuditReport(score_lexical=90.0, score_composite=45.0))
    assert exc_same.value.status_code == 400 and "PARAPHRASE_TOO_SIMILAR" in exc_same.value.detail

    almost = "Penerapan algoritma pembelajaran mesin meningkatkan akurasi klasifikasi dokumen ilmiah signifikan."
    with pytest.raises(HTTPException) as exc_high:
        AssistantService.apply_paraphrase_in_place(s1, almost, [s1], AuditReport(score_lexical=90.0, score_composite=45.0))
    assert exc_high.value.status_code == 400 and "PARAPHRASE_TOO_SIMILAR" in exc_high.value.detail


def test_yellow_stylometric_recompute_and_ai_flag_clearing():
    s_red = _sent(0, "Kalimat plagiat yang juga memiliki gaya AI.", match="RED", sim=88.0, start=0)
    s_yel = _sent(1, "Dalam era digital ini, hal tersebut memainkan peran vital.", match="YELLOW", sim=72.0, start=44)
    annos = [
        {"sentence_id": str(s_red.id), "start": 0, "end": 43, "color": "RED", "ai_flag": True, "ai_reason": "em_dash", "ai_score": 80.0, "reason": "T1"},
        {"sentence_id": str(s_yel.id), "start": 44, "end": 102, "color": "YELLOW", "ai_flag": True, "ai_reason": "transition", "ai_score": 72.0, "reason": "T3"},
    ]
    report = AuditReport(score_lexical=80.0, score_semantic=0.0, score_stylometric=60.0, score_composite=49.0, heatmap_annotations=annos)

    res1 = AssistantService.apply_paraphrase_in_place(s_red, "Gagasan utama disusun ulang dengan rujukan primer.", [s_red, s_yel], report)
    assert report.score_lexical == 0.0 and report.score_stylometric == 60.0
    assert "ai_flag" not in report.heatmap_annotations[0] and "ai_reason" not in report.heatmap_annotations[0]
    assert res1["new_similarity"] == 0.0

    res2 = AssistantService.apply_paraphrase_in_place(s_yel, "Perkembangan teknologi informasi memengaruhi tata kelola riset.", [s_red, s_yel], report)
    assert res2["new_similarity"] == 0.0 and report.score_stylometric == 0.0 and report.score_composite == 0.0
    assert "ai_flag" not in report.heatmap_annotations[1] and "ai_score" not in report.heatmap_annotations[1]


async def test_paragraph_scope_absorbs_neighbors_without_duplication(tmp_path):
    s0 = _sent(0, "Kalimat pertama tentang metode.", match="RED", sim=85.0, start=0)
    s1 = _sent(1, "Kalimat kedua tentang data.", match="ORANGE", sim=78.0, start=32)
    s2 = _sent(2, "Kalimat ketiga tentang hasil.", match="NONE", sim=0.0, start=60)
    docx_path = tmp_path / "uji.docx"
    d = docx.Document()
    d.add_paragraph("Kalimat pertama tentang metode. Kalimat kedua tentang data. Kalimat ketiga tentang hasil.")
    d.save(str(docx_path))

    doc_meta = Document(stored_filename="uji.docx", mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    task = AuditTask(id=uuid.uuid4(), document_id=uuid.uuid4(), user_id=uuid.uuid4(), sentences=[s0, s1, s2], document=doc_meta)
    report = AuditReport(audit_task_id=task.id, audit_task=task, score_lexical=50.0, score_semantic=40.0, score_stylometric=0.0, score_composite=39.0)

    res = AssistantService.apply_paraphrase_in_place(s1, "Paragraf gabungan baru yang orisinal.", [s0, s1, s2], report, mode="PARAGRAPH")
    assert res["current_text"] == "Paragraf gabungan baru yang orisinal."
    assert s0.is_modified and s0.current_text == "" and s2.is_modified and s2.current_text == ""
    assert report.document_text == "Paragraf gabungan baru yang orisinal."

    with patch("app.services.report_text_builder.settings.UPLOAD_DIR", str(tmp_path)):
        structured, _ = build_structured_report_view(report, [], [s0, s1, s2])
        assert structured == "Paragraf gabungan baru yang orisinal."
        resp = build_revised_document_response(report, [s0, s1, s2], "docx")
    raw = b"".join([p if isinstance(p, bytes) else p.encode("utf-8") async for p in resp.body_iterator])
    assert "\n".join(p.text for p in docx.Document(io.BytesIO(raw)).paragraphs) == "Paragraf gabungan baru yang orisinal."


def test_anti_aisigns_prompt_and_real_predicted_score():
    prompt = build_paraphrase_prompt("Teks sumber penelitian.", "SENTENCE")
    assert "em-dash" in prompt and "WP:AISIGNS" in prompt
    orig = "Penerapan metode kuantitatif meningkatkan validitas penelitian."
    mock_gw = MagicMock()
    mock_gw.generate_text_with_failover.return_value = (
        json.dumps([
            {"option_id": 1, "style": "Formal", "text": orig, "predicted_score": 5.0},
            {"option_id": 2, "style": "Ringkas", "text": "Pendekatan numerik memperkuat keabsahan kajian.", "predicted_score": 9.0},
            {"option_id": 3, "style": "Analitis", "text": "Analisis statistik memperkokoh keakuratan studi.", "predicted_score": 9.0},
        ]),
        "Gemini",
    )
    vars_, _ = AssistantService.generate_paraphrase_variations(orig, gateway=mock_gw)
    assert vars_[0]["predicted_score"] == 100.0 and vars_[1]["predicted_score"] < 30.0


async def test_focus_context_audited_map_and_prefilter():
    s0 = _sent(0, "Kalimat pembuka.", start=0)
    s1 = _sent(1, "Kalimat fokus bermasalah.", match="RED", sim=86.0, start=17)
    s2 = _sent(2, "Kalimat penutup.", start=43)
    s0.audit_task_id = s1.audit_task_id = s2.audit_task_id = uuid.uuid4()
    res_focus = MagicMock(scalar_one_or_none=MagicMock(return_value=s1))
    res_nbrs = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[s0, s1, s2]))))
    db = MagicMock(execute=AsyncMock(side_effect=[res_focus, res_nbrs]))
    ctx = await load_focus_sentence_context(db, uuid.uuid4(), s1.id)
    assert "Kalimat fokus bermasalah." in ctx and "Kalimat pembuka." in ctx and "86.0%" in ctx

    doc_id = uuid.uuid4()
    task = SimpleNamespace(id=s1.audit_task_id, document_id=doc_id)
    db2 = MagicMock(execute=AsyncMock(side_effect=[
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[task])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[s0, s1, s2])))),
    ]))
    amap = await load_audited_sentences_map(db2, uuid.uuid4(), [doc_id])
    assert amap[doc_id] == ["Kalimat pembuka.", "Kalimat fokus bermasalah.", "Kalimat penutup."]

    many = [f"Kalimat umum nomor {i}." for i in range(150)]
    many[75] = "Algoritma Winnowing mendeteksi plagiarisme leksikal."
    picked = select_relevant_sentences("Bagaimana algoritma Winnowing bekerja?", many, top_k=2)
    assert many[75] in picked
