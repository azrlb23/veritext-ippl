from __future__ import annotations

import math

from fastapi import HTTPException, status

from app.core.config import settings

WORDS_PER_TOKEN = 2500
MAX_AUDIT_TOKEN_COST = 5
FREE_MAX_WORDS = 2500


def compute_audit_cost(word_count: int | None) -> int:
    """Biaya audit = min(5, ceil(kata / 2500)) token, minimal 1 token."""
    words = max(0, int(word_count or 0))
    return max(1, min(MAX_AUDIT_TOKEN_COST, math.ceil(words / WORDS_PER_TOKEN)))


def exceeds_plan_limit(role: str | None, word_count: int | None) -> bool:
    """Akun FREE dibatasi 2.500 kata per dokumen. Peran None berarti tanpa pembatasan."""
    if role is None:
        return False
    return str(role).upper() == "FREE" and int(word_count or 0) > FREE_MAX_WORDS


def _dotted(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def ensure_within_plan(role: str | None, word_count: int | None) -> None:
    if exceeds_plan_limit(role, word_count):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Naskah akun FREE maksimal {_dotted(FREE_MAX_WORDS)} kata, sedangkan naskah ini "
                f"{_dotted(int(word_count or 0))} kata. Upgrade ke Premium untuk naskah yang lebih panjang."
            ),
        )


def ensure_minimum_words(word_count: int | None) -> None:
    """DOC_003: naskah di bawah batas minimum kata tidak layak dianalisis."""
    minimum = settings.MIN_DOCUMENT_WORDS
    if int(word_count or 0) < minimum:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Naskah terlalu pendek: {int(word_count or 0)} kata. Minimal {minimum} kata agar dapat dianalisis.",
        )
