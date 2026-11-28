from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.audit import AuditReport
from app.services.chat_audit_context import (
    format_single_report_summary, load_audit_reports_context, load_chat_audit_bundle,
)
from app.services.chat_prompt import build_prompt, classify_task_and_engine


def test_format_single_report_summary_includes_scores_sources_citations_and_flags():
    report = AuditReport(
        score_composite=42.5,
        score_lexical=60.0,
        score_semantic=30.0,
        score_stylometric=20.0,
        matched_sources=[
            {"title": "Jurnal Informatika Nusantara", "contribution_pct": 24.5, "source_url": "https://example.org/j1"},
        ],
        heatmap_annotations=[
            {
                "tier": "T1", "color": "RED", "source_title": "Jurnal Informatika Nusantara",
                "reason": "Kecocokan leksikal langsung", "text_snippet": "Metode ini mengolah korpus teks ilmiah.",
            },
            {
                "tier": "T3", "color": "YELLOW", "source_title": "Verifikasi Sitasi Daftar Pustaka",
                "reason": "Sitasi UNVERIFIED pada DOI 10.9999/fake",
                "ai_reason": "Sitasi UNVERIFIED pada DOI 10.9999/fake",
                "text_snippet": "Sari, A. (2024). Analisis Semantik. DOI 10.9999/fake.",
            },
        ],
    )
    summary = format_single_report_summary("bab1.docx", report)
    assert 'Laporan Audit "bab1.docx"' in summary
    assert "Komposit 42.5%" in summary
    assert "T1 Leksikal 60.0%" in summary
    assert "T2 Semantik 30.0%" in summary
    assert "T3 Stilometri/AI 20.0%" in summary
    assert "Jurnal Informatika Nusantara: 24.5%" in summary
    assert "UNVERIFIED" in summary
    assert "Kecocokan leksikal langsung" in summary


async def test_load_audit_reports_context_appends_draft_comparison_for_two_docs():
    d1 = SimpleNamespace(id=uuid.uuid4(), original_filename="draf_v1.docx")
    d2 = SimpleNamespace(id=uuid.uuid4(), original_filename="draf_v2.docx")
    r1 = AuditReport(score_composite=55.0, score_lexical=70.0, score_semantic=45.0, score_stylometric=30.0, heatmap_annotations=[])
    r2 = AuditReport(
        score_composite=22.0, score_lexical=20.0, score_semantic=25.0, score_stylometric=10.0,
        heatmap_annotations=[{"color": "RESOLVED_GREEN", "tier": "T1", "text_snippet": "Sudah direvisi."}],
    )
    t1 = SimpleNamespace(document_id=d1.id, report=r1)
    t2 = SimpleNamespace(document_id=d2.id, report=r2)
    db = MagicMock()
    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[t1, t2])))))

    ctx = await load_audit_reports_context(db, uuid.uuid4(), [d1, d2])
    assert "Perbandingan Skor Antar-Draf:" in ctx
    assert "Draf 1 (draf_v1.docx): Komposit 55.0%" in ctx
    assert "Draf 2 (draf_v2.docx): Komposit 22.0%" in ctx
    assert "Resolved=1" in ctx


async def test_load_chat_audit_bundle_skips_db_for_idless_mock_docs():
    db = MagicMock(execute=AsyncMock())
    with patch("app.services.chat_audit_context.load_focus_sentence_context", AsyncMock()) as mock_focus:
        ctx, amap = await load_chat_audit_bundle(db, uuid.uuid4(), [object()], None)
    assert ctx == ""
    assert amap == {}
    mock_focus.assert_not_awaited()
    db.execute.assert_not_awaited()


def test_classify_task_and_engine_routes_workbench_modes_and_preserves_existing():
    assert classify_task_and_engine("Tolong bedah audit dan buat prioritas revisi.", True, doc_count=1) == ("AUDIT_COACH", "auto")
    assert classify_task_and_engine("Rapikan sitasi dan daftar pustaka ke format APA 7.", True, doc_count=1) == ("CITATION_ASSIST", "auto")
    assert classify_task_and_engine("Cek pola AI dan burstiness paragraf ini.", True, doc_count=1) == ("STYLE_REVIEW", "auto")
    assert classify_task_and_engine("Periksa ejaan EYD dan kalimat efektif di bab 2.", True, doc_count=1) == ("EYD_PROOFREAD", "auto")
    assert classify_task_and_engine("Bandingkan progres skor antar draf saya.", True, doc_count=2) == ("DRAFT_COMPARE", "auto")
    assert classify_task_and_engine("Bandingkan bagian ini dengan metode sebelumnya.", True, doc_count=1) == ("QA_DOCUMENT", "auto")
    assert classify_task_and_engine("Tolong parafrase kalimat ini agar lebih baku.", True, doc_count=1) == ("PARAPHRASE_TASK", "auto")
    assert classify_task_and_engine("Apa kesimpulan utama dari naskah ini?", True, doc_count=1) == ("QA_DOCUMENT", "auto")
    assert classify_task_and_engine(
        "jalankan sesuai saran anda",
        True,
        doc_count=1,
        history=[("USER", "Rapikan sitasi dan daftar pustaka."), ("ASSISTANT", "Pilih IEEE atau APA.")],
    ) == ("CITATION_ASSIST", "auto")


def test_build_prompt_includes_mode_specific_rules_and_audit_context():
    eyd_prompt = build_prompt("Cek ejaan", "Laporan Audit \"x.docx\": Komposit 20.0%", [], task_mode="EYD_PROOFREAD")
    assert "EYD Edisi V" in eyd_prompt
    assert 'Laporan Audit "x.docx"' in eyd_prompt

    cit_prompt = build_prompt("Rapikan dafpus", "Temuan sitasi UNVERIFIED", [], task_mode="CITATION_ASSIST")
    assert "APA 7" in cit_prompt and "IEEE" in cit_prompt

    style_prompt = build_prompt("Haluskan gaya", "Teks uji", [], task_mode="STYLE_REVIEW")
    assert "WP:AISIGNS" in style_prompt and "em-dash" in style_prompt


def test_format_single_report_summary_prioritizes_severe_red_over_earlier_yellow():
    yellows = [
        {"tier": "T3", "color": "YELLOW", "similarity": 0.72, "reason": "Pola AI", "text_snippet": f"Kalimat AI ke-{i}."}
        for i in range(6)
    ]
    late_red = {
        "tier": "T1", "color": "RED", "similarity": 0.95, "source_title": "Skripsi Bab 3",
        "reason": "Kecocokan leksikal tinggi", "text_snippet": "Kalimat plagiat berat di bab 3.",
    }
    report = AuditReport(score_composite=38.0, score_lexical=45.0, score_semantic=10.0, score_stylometric=35.0, heatmap_annotations=[*yellows, late_red])
    summary = format_single_report_summary("tesis.docx", report)
    assert "Kalimat plagiat berat di bab 3." in summary
    assert summary.index("Kalimat plagiat berat di bab 3.") < summary.index("Kalimat AI ke-0.")
