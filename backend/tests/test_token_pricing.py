from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.services.token_pricing import (
    FREE_MAX_WORDS,
    compute_audit_cost,
    ensure_within_plan,
    exceeds_plan_limit,
)
from app.services.word_counter import count_words, count_words_in_file


@pytest.mark.parametrize(
    "words, expected",
    [(0, 1), (1, 1), (2500, 1), (2501, 2), (5000, 2), (5001, 3), (12500, 5), (12501, 5), (100000, 5), (None, 1)],
)
def test_cost_is_min_five_of_ceiling_per_2500_words(words, expected):
    assert compute_audit_cost(words) == expected


def test_free_plan_limit_applies_only_to_free_role():
    assert exceeds_plan_limit("FREE", FREE_MAX_WORDS + 1) is True
    assert exceeds_plan_limit("free", FREE_MAX_WORDS) is False
    assert exceeds_plan_limit("PREMIUM", 50000) is False
    assert exceeds_plan_limit(None, 50000) is False


def test_free_over_limit_raises_402_with_dotted_numbers():
    with pytest.raises(HTTPException) as exc:
        ensure_within_plan("FREE", 3100)
    assert exc.value.status_code == 402
    assert "2.500" in exc.value.detail and "3.100" in exc.value.detail


def test_ensure_within_plan_allows_premium_and_short_free():
    ensure_within_plan("PREMIUM", 40000)
    ensure_within_plan("FREE", 2500)


def test_count_words_ignores_empty_text():
    assert count_words("") == 0
    assert count_words(None) == 0
    assert count_words("Penelitian ini membahas orisinalitas naskah.") == 5


def test_count_words_in_text_file(tmp_path):
    path = tmp_path / "naskah.txt"
    path.write_text("satu dua tiga empat lima " * 100, encoding="utf-8")
    assert count_words_in_file(str(path), "text/plain") == 500


def test_count_words_in_missing_file_returns_zero(tmp_path):
    assert count_words_in_file(str(tmp_path / "tidak-ada.txt")) == 0
