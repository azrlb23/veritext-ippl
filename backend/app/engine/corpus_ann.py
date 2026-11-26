from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text

from app.core.config import settings

logger = logging.getLogger(__name__)

NEAREST_SQL = text(
    """
    SELECT c.id, c.corpus_doc_id, c.chunk_text, c.start_char, c.end_char, d.title, d.category,
           1 - (c.embedding <=> CAST(:vec AS vector)) AS similarity
    FROM document_chunks c
    JOIN corpus_documents d ON d.id = c.corpus_doc_id
    WHERE d.status = 'INDEXED'
    ORDER BY c.embedding <=> CAST(:vec AS vector)
    LIMIT :top_k
    """
)


def vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(f"{float(x):.6f}" for x in embedding) + "]"


class PgvectorChunkSearch:
    """Pencarian tetangga terdekat korpus lewat indeks HNSW pgvector (jarak kosinus), tanpa memuat korpus ke memori."""

    def __init__(self, db: Any, ef_search: int | None = None):
        self.db = db
        self.ef_search = ef_search or settings.HNSW_EF_SEARCH
        self.available = True
        self._configured = False

    def _configure(self) -> None:
        if not self._configured:
            self.db.execute(text(f"SET hnsw.ef_search = {int(self.ef_search)}"))
            self._configured = True

    def nearest_k(self, embedding: list[float], k: int = 5) -> list[tuple[float, dict[str, Any]]]:
        """Mengembalikan hingga k pasangan (kemiripan, potongan) terdekat dari pgvector."""
        if not self.available:
            return []
        try:
            self._configure()
            rows = self.db.execute(NEAREST_SQL, {"vec": vector_literal(embedding), "top_k": max(1, k)}).mappings().all()
        except Exception as err:  # noqa: BLE001
            logger.warning("Pencarian HNSW pgvector dilewati: %s", err)
            self.available = False
            try:
                self.db.rollback()
            except Exception:  # noqa: BLE001
                pass
            return []
        return [
            (float(r["similarity"]), {
                "chunk_id": str(r["id"]), "corpus_doc_id": str(r["corpus_doc_id"]),
                "title": r["title"], "category": r["category"] or "General", "chunk_text": r["chunk_text"],
                "start_char": r["start_char"], "end_char": r["end_char"],
            })
            for r in rows
        ]

    def nearest(self, embedding: list[float]) -> tuple[float, dict[str, Any]] | None:
        """Mengembalikan (kemiripan, potongan) terdekat, atau None bila basis data tidak tersedia."""
        hits = self.nearest_k(embedding, k=1)
        return hits[0] if hits else None
