from __future__ import annotations

import logging
from typing import Literal

logger = logging.getLogger(__name__)

_DETECTOR = None
_ATTEMPTED = False


def _get_detector():
    global _DETECTOR, _ATTEMPTED
    if not _ATTEMPTED:
        _ATTEMPTED = True
        try:
            from lingua import Language, LanguageDetectorBuilder

            _DETECTOR = LanguageDetectorBuilder.from_languages(
                Language.INDONESIAN,
                Language.ENGLISH,
            ).build()
        except Exception as err:  # noqa: BLE001
            logger.warning("Lingua language detector gagal dimuat: %s", err)
            _DETECTOR = None
    return _DETECTOR


def detect_language(text: str) -> Literal["id", "en"]:
    """Deteksi bahasa Indonesia ('id') vs Inggris ('en') menggunakan library lingua-language-detector."""
    cleaned = (text or "").strip()
    if len(cleaned) < 8:
        return "id"
    detector = _get_detector()
    if detector is None:
        return "id"
    try:
        from lingua import Language

        detected = detector.detect_language_of(cleaned)
        if detected == Language.ENGLISH:
            return "en"
    except Exception as err:  # noqa: BLE001
        logger.warning("Deteksi bahasa gagal, fallback ke 'id': %s", err)
    return "id"
