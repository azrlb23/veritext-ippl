from __future__ import annotations

from unittest.mock import patch

import pytest
from semantic_pairs_data import build

from app.engine.tier2_indobert import IndoBertScorer
from app.engine.tier2_reranker import SemanticReranker

PAIRS = build()


def test_accepts_everything_when_indobert_unavailable():
    with patch.object(IndoBertScorer, "similarities", return_value=None):
        assert IndoBertScorer.accept_mask([("a", "b"), ("c", "d")]) == [True, True]


def test_reranker_requires_both_layers():
    pairs = [("p1", "q1"), ("p2", "q2"), ("p3", "q3")]
    with patch.object(SemanticReranker, "score_pairs", return_value=[0.9, 0.9, 0.1]), \
         patch.object(IndoBertScorer, "similarities", return_value=[0.8, 0.2]):
        assert SemanticReranker.accept_mask(pairs) == [True, False, False]


@pytest.fixture(scope="module")
def sims():
    result = IndoBertScorer.similarities([(a, b) for a, b, *_ in PAIRS])
    if result is None:
        pytest.skip("Model IndoBERT tidak tersedia di mesin ini")
    return result


def test_indobert_is_768_dimensional():
    model = IndoBertScorer.get_model()
    if model is None:
        pytest.skip("Model IndoBERT tidak tersedia di mesin ini")
    assert model.get_sentence_embedding_dimension() == 768


def test_unrelated_pairs_fall_below_floor_and_paraphrases_stay_above(sims):
    from app.core.config import settings

    easy = [s for s, p in zip(sims, PAIRS) if p[4] == "easy"]
    pos = [s for s, p in zip(sims, PAIRS) if p[4] == "pos"]
    assert max(easy) < settings.INDOBERT_MIN_SIM
    assert min(pos) >= settings.INDOBERT_MIN_SIM


def test_two_layer_reranker_keeps_eval_accuracy():
    mask = SemanticReranker.accept_mask([(a, b) for a, b, *_ in PAIRS])
    accuracy = sum(m == bool(p[2]) for m, p in zip(mask, PAIRS)) / len(PAIRS)
    assert accuracy >= 0.96
