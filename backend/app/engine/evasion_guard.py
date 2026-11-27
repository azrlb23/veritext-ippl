from __future__ import annotations

import re
import statistics
import zlib
from typing import Any

ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff\u00ad]")
_LATIN_RE = re.compile(r"[A-Za-z]")

CYRILLIC_TO_LATIN: dict[str, str] = {
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p", "\u0441": "c",
    "\u0445": "x", "\u0443": "y", "\u0456": "i", "\u0410": "A", "\u0415": "E",
    "\u041e": "O", "\u0420": "P", "\u0421": "C", "\u0425": "X", "\u0422": "T",
    "\u041c": "M", "\u041d": "H", "\u041a": "K", "\u0412": "B",
}
_CYRILLIC_TABLE = str.maketrans(CYRILLIC_TO_LATIN)


def normalize_evasion(text: str) -> str:
    """Strips invisible evasion characters and normalizes Cyrillic homoglyphs."""
    return ZERO_WIDTH_RE.sub("", text).translate(_CYRILLIC_TABLE) if text else ""


def detect_evasion_signals(text: str) -> list[tuple[str, float, str]]:
    """Detects zero-width characters and mixed Cyrillic-Latin homoglyph evasion."""
    if not text:
        return []
    signals: list[tuple[str, float, str]] = []
    if ZERO_WIDTH_RE.search(text):
        signals.append(
            ("evasion_zw", 0.92, "Terdeteksi karakter tak terlihat (zero-width/soft-hyphen) indikasi manipulasi teks")
        )
    if any(ch in CYRILLIC_TO_LATIN for ch in text) and _LATIN_RE.search(text):
        signals.append(
            ("evasion_homoglyph", 0.92, "Terdeteksi aksara homoglyph (Cyrillic) bercampur huruf Latin indikasi manipulasi teks")
        )
    return signals


def compute_compression_ratio(text: str) -> float:
    """Computes zlib compression ratio as an intrinsic redundancy proxy."""
    raw = text.encode("utf-8") if text else b""
    if not raw:
        return 1.0
    return round(len(zlib.compress(raw, level=6)) / len(raw), 4)


def detect_style_shift_blocks(
    valid_spans: list[Any], block_size: int = 10
) -> tuple[set[int], list[str]]:
    """Flags contiguous blocks showing abrupt sentence-length shifts or low entropy."""
    if len(valid_spans) < block_size * 2:
        return set(), []

    blocks = [
        valid_spans[i : i + block_size]
        for i in range(0, len(valid_spans), block_size)
        if i + block_size <= len(valid_spans) or len(valid_spans) - i >= 6
    ]
    if len(blocks) < 2:
        return set(), []

    stats: list[tuple[list[Any], float, int, float]] = []
    for blk in blocks:
        total_words = sum(s.word_count for s in blk)
        mean_wc = total_words / len(blk)
        comp_ratio = compute_compression_ratio(" ".join(s.text for s in blk))
        stats.append((blk, mean_wc, total_words, comp_ratio))

    med_wc = statistics.median(item[1] for item in stats)
    flagged_indices: set[int] = set()
    hints: list[str] = []

    for blk, mean_wc, total_words, comp_ratio in stats:
        shift_hit = med_wc > 0 and abs(mean_wc - med_wc) / med_wc >= 0.45 and comp_ratio <= 0.58
        entropy_hit = total_words >= 60 and comp_ratio <= 0.46
        if shift_hit or entropy_hit:
            flagged_indices.update(s.index for s in blk)
            hints.append(
                f"Blok kalimat [{blk[0].index}..{blk[-1].index}]: terdeteksi style-shift "
                f"(rata-rata kata {mean_wc:.1f} vs median {med_wc:.1f}, rasio kompresi {comp_ratio:.2f})"
            )

    return flagged_indices, hints
