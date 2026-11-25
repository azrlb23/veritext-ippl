from __future__ import annotations

import re
from typing import Literal

_WORD_RE = re.compile(r"[a-zA-Z]+")

_ID_MARKERS = frozenset({
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "pada", "ini", "itu",
    "adalah", "sebagai", "dalam", "atau", "tidak", "oleh", "secara", "bahwa",
    "dapat", "akan", "telah", "tersebut", "karena", "sehingga", "merupakan",
})

_EN_MARKERS = frozenset({
    "the", "and", "is", "are", "of", "to", "in", "for", "with", "that", "this",
    "as", "by", "from", "on", "was", "were", "which", "has", "have", "been",
    "can", "will", "not", "or", "an", "be", "their", "these", "using",
})


def detect_language(text: str) -> Literal["id", "en"]:
    """Deteksi cepat bahasa Indonesia ('id') vs Inggris/Asing ('en') berbasis kata fungsi."""
    words = [w.lower() for w in _WORD_RE.findall(text or "")]
    if not words:
        return "id"
    id_hits = sum(1 for w in words if w in _ID_MARKERS)
    en_hits = sum(1 for w in words if w in _EN_MARKERS)
    if en_hits > id_hits and en_hits >= 1:
        return "en"
    return "id"
