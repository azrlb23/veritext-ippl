from __future__ import annotations

import re

from app.engine.preprocessor import TextPreprocessor

_HEADING_RE = re.compile(
    r"^(?:bab\s+[ivxlcdm0-9]+|\d+(?:\.\d+)+\s+|daftar\s+(?:isi|pustaka|tabel|gambar)|kata\s+pengantar|abstrak|pendahuluan|kesimpulan|saran|referensi)\b",
    re.IGNORECASE,
)
_BOILERPLATE_RE = re.compile(
    r"^(?:bab\s+ini\s+(?:membahas|menguraikan|menjelaskan|berfungsi)|"
    r"(?:tujuan\s+(?:dari\s+)?penelitian\s+ini\s+adalah|penelitian\s+ini\s+bertujuan)|"
    r"berdasarkan\s+(?:hasil|penjelasan|uraian)\s+(?:penelitian\s+)?di\s+atas|"
    r"pada\s+bab\s+(?:ini|sebelumnya|selanjutnya))\b",
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
    if not cleaned or _HEADING_RE.match(cleaned) or _BOILERPLATE_RE.search(cleaned):
        return True
    return len(content_words(cleaned)) < min_content_words


def content_words(text: str) -> list[str]:
    return [w for w in TextPreprocessor.tokenize_words(text) if len(w) >= 4 and w not in STOPWORDS]


def _has_ngram(a: list[str], b: list[str], n: int) -> bool:
    if len(a) < n or len(b) < n:
        return False
    a_ngrams = {tuple(a[i : i + n]) for i in range(len(a) - n + 1)}
    return bool(a_ngrams.intersection(tuple(b[i : i + n]) for i in range(len(b) - n + 1)))


def has_lexical_evidence(sentence_text: str, candidate_text: str | None) -> bool:
    """Verifikasi kecocokan nyata: minimal 4-gram token bebas stopword atau 5-gram token mentah."""
    if not candidate_text:
        return False
    raw_s = TextPreprocessor.tokenize_words(sentence_text)
    raw_c = TextPreprocessor.tokenize_words(candidate_text)
    s_toks = [w for w in raw_s if w not in STOPWORDS]
    c_toks = [w for w in raw_c if w not in STOPWORDS]
    return _has_ngram(s_toks, c_toks, 4) or _has_ngram(raw_s, raw_c, 5)


def pick_best_matching_snippet(sentence_text: str, candidate_text: str) -> str:
    segs = TextPreprocessor.segment_sentences(candidate_text)
    if len(segs) <= 1:
        return candidate_text
    s_cw = set(content_words(sentence_text))
    best_seg, best_ov, best_len = None, 0, -1
    for seg in segs:
        ov = len(s_cw.intersection(content_words(seg.text)))
        if ov > best_ov or (ov == best_ov and ov > 0 and len(seg.text) > best_len):
            best_seg, best_ov, best_len = seg.text, ov, len(seg.text)
    return best_seg if best_seg is not None else candidate_text
