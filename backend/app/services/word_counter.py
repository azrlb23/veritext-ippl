from __future__ import annotations

import logging
import os

from app.core.config import settings
from app.engine.preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)


def count_words(text: str | None) -> int:
    return len(TextPreprocessor.tokenize_words(text or ""))


def count_words_in_file(path: str, mime_type: str | None = None) -> int:
    """Menghitung kata dari PDF, DOCX, atau TXT. Jika ekstraksi gagal, membaca berkas sebagai teks mentah."""
    try:
        text = TextPreprocessor.extract_text_from_file(path, mime_type=mime_type)
    except Exception as err:  # noqa: BLE001
        logger.warning("Ekstraksi teks gagal saat menghitung kata, memakai pembacaan mentah: %s", err)
        try:
            with open(path, "rb") as handle:
                text = handle.read().decode("utf-8", errors="replace")
        except OSError:
            return 0
    return count_words(text)


def count_strict_words_in_file(path: str, mime_type: str | None = None) -> int:
    """Hitung kata untuk unggahan baru: PDF/DOCX diekstrak di subproses ber-timeout; kegagalan baca dihitung 0 kata."""
    if path.rsplit(".", 1)[-1].lower() == "txt":
        return count_words_in_file(path, mime_type)
    from app.services.safe_extract import extract_text_limited

    return count_words(extract_text_limited(path, mime_type))


def document_word_count(doc) -> int:
    """Jumlah kata dokumen: memakai nilai tersimpan, atau menghitung dari berkas di disk."""
    if getattr(doc, "word_count", None):
        return int(doc.word_count)
    stored = getattr(doc, "stored_filename", None)
    if stored:
        return count_words_in_file(os.path.join(settings.UPLOAD_DIR, stored), getattr(doc, "mime_type", None))
    return 0
