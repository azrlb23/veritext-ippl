from __future__ import annotations

from typing import Any

from app.engine.preprocessor import TextPreprocessor
from app.engine.tier1_lexical import WinnowingLexicalEngine

_STOPWORDS: frozenset[str] = frozenset({
    "yang", "dan", "dari", "pada", "untuk", "dengan", "dalam", "atau", "juga",
    "oleh", "karena", "bahwa", "sebagai", "agar", "serta", "dapat", "telah",
    "akan", "adalah", "merupakan", "tersebut", "antara", "sebuah", "suatu",
    "lebih", "saat", "bila", "jika", "maka", "namun", "tetapi", "tidak",
    "bukan", "secara", "hanya", "masih", "sudah", "belum", "sangat", "bagi",
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "were",
    "into", "have", "has", "had", "not", "but", "can", "will", "their", "they",
})


def _content_words(text: str) -> set[str]:
    tokens = TextPreprocessor.tokenize_words(text)
    filtered = {w for w in tokens if len(w) >= 3 and w not in _STOPWORDS}
    return filtered or {w for w in tokens if len(w) >= 3}


def measure_paraphrase_similarity(original_text: str, rewritten_text: str) -> dict[str, Any]:
    """Measure local Winnowing lexical and content-word overlap with zero LLM cost."""
    orig = original_text or ""
    rewr = rewritten_text or ""

    engine = WinnowingLexicalEngine()
    orig_fps = engine.extract_fingerprints(orig)
    rewr_hashes = {h for h, _ in engine.extract_fingerprints(rewr)}
    lexical_overlap_pct, _ = engine.calculate_containment(orig_fps, rewr_hashes)

    orig_words = _content_words(orig)
    rewr_words = _content_words(rewr)
    if orig_words:
        word_overlap_pct = round(
            min(100.0, max(0.0, (len(orig_words & rewr_words) / len(orig_words)) * 100.0)),
            2,
        )
    else:
        word_overlap_pct = 0.0

    is_improved = (
        bool(rewr.strip())
        and lexical_overlap_pct < 35.0
        and rewr.strip() != orig.strip()
    )
    return {
        "lexical_overlap_pct": float(lexical_overlap_pct),
        "word_overlap_pct": float(word_overlap_pct),
        "is_improved": bool(is_improved),
    }
