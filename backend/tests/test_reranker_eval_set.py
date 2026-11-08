"""Evaluasi regresi re-ranker pada 52 pasangan kalimat berlabel (Indonesia dan Inggris).

Set ini ditulis tangan dan kecil. Ia menjaga agar pasangan berlawanan makna tidak lolos
sebagai parafrase, bukan tolok ukur akurasi umum.
"""
from __future__ import annotations

import pytest
from semantic_pairs_data import build

from app.core.config import settings
from app.engine.tier2_reranker import SemanticReranker

PAIRS = build()


@pytest.fixture(scope="module")
def scores() -> list[float]:
    result = SemanticReranker.score_pairs([(a, b) for a, b, *_ in PAIRS])
    if result is None:
        pytest.skip("Model re-ranker tidak tersedia di mesin ini")
    return result


def _accuracy(scores: list[float], kinds: set[str]) -> float:
    rows = [(s, p[2]) for s, p in zip(scores, PAIRS) if p[4] in kinds]
    return sum((s >= settings.RERANKER_THRESHOLD) == bool(label) for s, label in rows) / len(rows)


def test_eval_set_has_expected_shape():
    assert len(PAIRS) == 52
    assert {p[3] for p in PAIRS} == {"id", "en"}
    assert {p[4] for p in PAIRS} == {"pos", "hard", "easy"}


def test_paraphrases_are_accepted(scores):
    assert _accuracy(scores, {"pos"}) >= 0.9


def test_antonym_pairs_are_rejected(scores):
    assert _accuracy(scores, {"hard"}) >= 0.9


def test_unrelated_pairs_are_rejected(scores):
    assert _accuracy(scores, {"easy"}) == 1.0


@pytest.mark.parametrize("lang", ["id", "en"])
def test_each_language_separates_paraphrase_from_antonym(scores, lang):
    pos = [s for s, p in zip(scores, PAIRS) if p[3] == lang and p[4] == "pos"]
    hard = [s for s, p in zip(scores, PAIRS) if p[3] == lang and p[4] == "hard"]
    assert min(pos) > max(hard)
