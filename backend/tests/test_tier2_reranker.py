from __future__ import annotations

from unittest.mock import patch

from app.engine.preprocessor import SentenceSpan
from app.engine.tier2_reranker import SemanticReranker
from app.engine.tier2_semantic import SemanticEngine


def _sentence(text: str) -> SentenceSpan:
    return SentenceSpan(index=0, text=text, start_char=0, end_char=len(text), word_count=len(text.split()))


def _chunks(engine: SemanticEngine, text: str) -> list[dict]:
    return [{
        "chunk_id": "c1", "corpus_doc_id": "d1", "title": "Dokumen A", "category": "Umum",
        "chunk_text": text, "embedding": engine.embed_sentence(text),
    }]


def test_accept_mask_accepts_all_when_model_unavailable():
    with patch.object(SemanticReranker, "get_model", return_value=None):
        assert SemanticReranker.accept_mask([("a", "b"), ("c", "d")]) == [True, True]


def test_accept_mask_applies_threshold():
    with patch.object(SemanticReranker, "score_pairs", return_value=[0.9, 0.1]):
        assert SemanticReranker.accept_mask([("a", "b"), ("c", "d")]) == [True, False]


def test_rejected_candidate_is_dropped_from_semantic_result():
    engine = SemanticEngine(paraphrase_threshold=0.5)
    text = "Inflasi meningkat tajam akibat kenaikan harga bahan bakar."
    chunks = _chunks(engine, text)
    with patch.object(SemanticReranker, "score_pairs", return_value=[0.02]):
        result = engine.analyze_document([_sentence(text)], chunks)
    assert result.sentence_matches == []
    assert result.score_t2 == 0.0


def test_accepted_candidate_is_kept_in_semantic_result():
    engine = SemanticEngine(paraphrase_threshold=0.5)
    text = "Inflasi meningkat tajam akibat kenaikan harga bahan bakar."
    chunks = _chunks(engine, text)
    with patch.object(SemanticReranker, "score_pairs", return_value=[0.97]):
        result = engine.analyze_document([_sentence(text)], chunks)
    assert len(result.sentence_matches) == 1
    assert result.score_t2 > 0.0


def test_real_reranker_separates_antonym_from_paraphrase():
    pairs = [
        ("Kenaikan harga bahan bakar menyebabkan inflasi meningkat tajam.",
         "Inflasi melonjak karena harga bahan bakar naik."),
        ("Kenaikan harga bahan bakar menyebabkan inflasi meningkat tajam.",
         "Penurunan harga bahan bakar menyebabkan inflasi menurun tajam."),
    ]
    scores = SemanticReranker.score_pairs(pairs)
    if scores is None:
        return
    assert scores[0] > scores[1]
    assert SemanticReranker.accept_mask(pairs) == [True, False]
