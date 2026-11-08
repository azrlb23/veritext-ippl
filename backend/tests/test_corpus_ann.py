from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy import text

from app.engine.corpus_ann import PgvectorChunkSearch, vector_literal
from app.engine.preprocessor import SentenceSpan
from app.engine.tier2_semantic import SemanticEngine


def test_vector_literal_format():
    assert vector_literal([0.5, 1, -2]) == "[0.500000,1.000000,-2.000000]"


def test_search_disables_itself_when_database_errors():
    db = MagicMock()
    db.execute.side_effect = RuntimeError("tabel tidak ada")
    searcher = PgvectorChunkSearch(db)
    assert searcher.nearest([0.1] * 384) is None
    assert searcher.available is False
    db.execute.reset_mock()
    assert searcher.nearest([0.1] * 384) is None
    db.execute.assert_not_called()


def test_tier2_uses_ann_hit_when_better_than_memory_chunks():
    engine = SemanticEngine()
    engine._transformer_model = None
    text_ = "Metode penelitian ini memakai survei kuesioner terhadap mahasiswa."
    sentence = SentenceSpan(index=0, text=text_, start_char=0, end_char=len(text_), word_count=8)
    emb = engine.embed_sentence_dense(text_)
    engine.embed_sentences = lambda texts: [emb for _ in texts]
    hit = {"chunk_id": "c1", "corpus_doc_id": "d1", "title": "Sumber ANN", "category": "Umum", "chunk_text": text_}
    searcher = SimpleNamespace(nearest=lambda e: (0.93, hit))
    from unittest.mock import patch

    with patch("app.engine.tier2_semantic.SemanticReranker.accept_mask", return_value=[True]):
        result = engine.analyze_document([sentence], [], corpus_searcher=searcher)
    assert result.sentence_matches and result.sentence_matches[0].matched_source_title == "Sumber ANN"
    assert result.score_t2 > 0


def _live_session():
    from app.core.database import SyncSessionLocal

    db = SyncSessionLocal()
    try:
        db.execute(text("select 1 from document_chunks limit 1"))
    except Exception:
        db.close()
        pytest.skip("Postgres dengan pgvector tidak tersedia")
    return db


def test_live_nearest_uses_hnsw_index_and_returns_closest_chunk():
    db = _live_session()
    try:
        row = db.execute(text("select embedding::text from document_chunks c join corpus_documents d on d.id=c.corpus_doc_id where d.status='INDEXED' limit 1")).first()
        if not row:
            pytest.skip("Belum ada potongan korpus terindeks")
        emb = [float(x) for x in row[0].strip("[]").split(",")]
        found = PgvectorChunkSearch(db).nearest(emb)
        assert found is not None and found[0] > 0.99
        db.execute(text("SET LOCAL enable_seqscan = off"))
        plan = "\n".join(r[0] for r in db.execute(text("EXPLAIN SELECT id FROM document_chunks ORDER BY embedding <=> CAST(:v AS vector) LIMIT 1"), {"v": row[0]}))
        assert "idx_document_chunks_vector" in plan
    finally:
        db.rollback()
        db.close()
