from __future__ import annotations

import re

from app.engine.preprocessor import TextPreprocessor

_HEADING_RE = re.compile(
    r"^(?:bab\s+[ivxlcdm0-9]+|\d+(?:\.\d+)+\s+|daftar\s+(?:isi|pustaka|tabel|gambar)|kata\s+pengantar|abstrak|pendahuluan|kesimpulan|saran|referensi)\b",
    re.IGNORECASE,
)

STOPWORDS = frozenset({
    "dan", "atau", "yang", "untuk", "dengan", "pada", "dari", "dalam", "oleh", "sebagai",
    "serta", "terhadap", "adalah", "ini", "itu", "agar", "karena", "sehingga", "bahwa",
    "dapat", "akan", "telah", "juga", "antara", "secara", "menjadi", "merupakan", "tersebut",
    "bab", "the", "and", "for", "with", "that", "this", "from", "into", "are", "was", "were",
    "been", "have", "has", "not", "but", "such", "their", "these",
})


def is_heading_or_too_short(text: str, min_content_words: int = 5) -> bool:
    cleaned = " ".join((text or "").split())
    if not cleaned or _HEADING_RE.match(cleaned):
        return True
    return len(content_words(cleaned)) < min_content_words


def content_words(text: str) -> list[str]:
    return [w for w in TextPreprocessor.tokenize_words(text) if len(w) >= 4 and w not in STOPWORDS]


def has_lexical_evidence(sentence_text: str, candidate_text: str | None) -> bool:
    """Verifikasi kecocokan nyata: minimal 4-gram kata berurutan atau >= 3 kata bermakna yang sama."""
    if not candidate_text:
        return False
    s_cw = content_words(sentence_text)
    c_cw = content_words(candidate_text)
    if len(set(s_cw).intersection(c_cw)) >= 3:
        return True
    s_toks = [w for w in TextPreprocessor.tokenize_words(sentence_text) if w not in STOPWORDS]
    c_toks = [w for w in TextPreprocessor.tokenize_words(candidate_text) if w not in STOPWORDS]
    if len(s_toks) < 4 or len(c_toks) < 4:
        return False
    s_ngrams = {tuple(s_toks[i : i + 4]) for i in range(len(s_toks) - 3)}
    c_ngrams = {tuple(c_toks[i : i + 4]) for i in range(len(c_toks) - 3)}
    return bool(s_ngrams.intersection(c_ngrams))
