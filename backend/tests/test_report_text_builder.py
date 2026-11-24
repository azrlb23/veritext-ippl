import os
import sys
import uuid
from types import SimpleNamespace
from unittest.mock import patch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.report_text_builder import build_structured_report_view


def _sent(idx, text, start_char, end_char, current_text=None, is_modified=False):
    return SimpleNamespace(
        id=uuid.uuid4(),
        sentence_index=idx,
        sentence_text=text,
        current_text=current_text,
        is_modified=is_modified,
        start_char=start_char,
        end_char=end_char,
    )


def _report(stored_filename=None, mime_type="text/plain"):
    doc = SimpleNamespace(stored_filename=stored_filename, mime_type=mime_type) if stored_filename else None
    return SimpleNamespace(audit_task=SimpleNamespace(document=doc))


def test_paragraph_and_heading_reconstruction_without_disk_file():
    s0 = _sent(0, "Kalimat pembuka penelitian.", 0, 27)
    s1 = _sent(1, "Paragraf kedua dimulai di sini.", 31, 62)  # gap > 2 -> \n\n
    s2 = _sent(2, "Bagian Metode Penelitian", 64, 88)  # gap == 2 & heading -> \n
    s3 = _sent(3, "Langkah pengujian dilakukan bertahap.", 89, 126)  # heading -> \n
    s4 = _sent(4, "Hasil dicatat rapi.", 127, 146)  # gap == 1 -> space
    text, _ = build_structured_report_view(_report("missing_nonexistent.txt"), [], [s4, s2, s0, s3, s1])
    assert text == (
        "Kalimat pembuka penelitian.\n\n"
        "Paragraf kedua dimulai di sini.\n"
        "Bagian Metode Penelitian\n"
        "Langkah pengujian dilakukan bertahap. Hasil dicatat rapi."
    )


def test_realigns_annotation_offsets_after_newline_shift_and_modification():
    s0 = _sent(0, "Pendahuluan singkat.", 0, 20)
    s1 = _sent(1, "Kalimat lama yang terdeteksi.", 25, 54, current_text="Kalimat baru hasil parafrase.", is_modified=True)
    s2 = _sent(2, "Target sorotan tetap akurat.", 56, 84)
    annotations = [
        {"start": 40, "end": 68, "tier": "T1", "color": "RED", "text_snippet": "Target sorotan tetap akurat."},
        {"start": 10, "end": 30, "tier": "T2", "color": "ORANGE", "sentence_id": str(s1.id)},
    ]
    text, aligned = build_structured_report_view(_report(), annotations, [s0, s1, s2])
    assert text is not None
    assert "Kalimat baru hasil parafrase." in text
    assert "Kalimat lama yang terdeteksi." not in text
    assert text[aligned[0]["start"]:aligned[0]["end"]] == "Target sorotan tetap akurat."
    assert text[aligned[1]["start"]:aligned[1]["end"]] == "Kalimat baru hasil parafrase."


def test_reads_original_file_from_disk_when_available(tmp_path):
    disk_file = tmp_path / "sample.txt"
    disk_text = "Judul Utama\n\nKalimat pertama asli.\nKalimat kedua yang diperiksa."
    disk_file.write_text(disk_text, encoding="utf-8")
    s0 = _sent(0, "Judul Utama", 0, 11)
    s1 = _sent(1, "Kalimat pertama asli.", 13, 34)
    s2 = _sent(2, "Kalimat kedua yang diperiksa.", 35, 64)
    annos = [{"start": 25, "end": 50, "tier": "T1", "color": "RED", "text_snippet": "Kalimat kedua yang diperiksa."}]
    with patch("app.services.report_text_builder.settings.UPLOAD_DIR", str(tmp_path)), patch(
        "app.services.report_text_builder.extract_text_limited", return_value=disk_text
    ):
        text, aligned = build_structured_report_view(_report("sample.txt"), annos, [s0, s1, s2])
    assert text == disk_text
    assert text[aligned[0]["start"]:aligned[0]["end"]] == "Kalimat kedua yang diperiksa."


def test_replaces_paraphrased_sentence_across_pdf_line_breaks(tmp_path):
    pdf_file = tmp_path / "draft.pdf"
    pdf_file.write_bytes(b"%PDF-1.4")
    disk_text = "Kalimat pertama\nyang terpotong baris\ndi PDF asli.\n\nKalimat kedua\ntetap utuh."
    s0 = _sent(
        0,
        "Kalimat pertama yang terpotong baris di PDF asli.",
        0,
        49,
        current_text="Kalimat pertama yang sudah direvisi rapi.",
        is_modified=True,
    )
    s1 = _sent(1, "Kalimat kedua tetap utuh.", 51, 76)
    annos = [
        {"start": 0, "end": 49, "tier": "T1", "color": "RESOLVED_GREEN", "sentence_id": str(s0.id), "text_snippet": "Kalimat pertama yang sudah direvisi rapi."},
        {"start": 51, "end": 76, "tier": "T2", "color": "ORANGE", "sentence_id": str(s1.id), "text_snippet": "Kalimat kedua tetap utuh."},
    ]
    with patch("app.services.report_text_builder.settings.UPLOAD_DIR", str(tmp_path)), patch(
        "app.services.report_text_builder.extract_text_limited", return_value=disk_text
    ):
        text, aligned = build_structured_report_view(_report("draft.pdf", "application/pdf"), annos, [s0, s1])
    assert text is not None
    assert "Kalimat pertama yang sudah direvisi rapi." in text
    assert "terpotong baris" not in text
    assert text[aligned[0]["start"]:aligned[0]["end"]] == "Kalimat pertama yang sudah direvisi rapi."
    assert text[aligned[1]["start"]:aligned[1]["end"]] == "Kalimat kedua\ntetap utuh."
