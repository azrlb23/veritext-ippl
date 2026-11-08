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
    LIMIT 1
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

    def nearest(self, embedding: list[float]) -> tuple[float, dict[str, Any]] | None:
        """Mengembalikan (kemiripan, potongan) terdekat, atau None bila basis data tidak tersedia."""
        if not self.available:
            return None
        try:
            self._configure()
            row = self.db.execute(NEAREST_SQL, {"vec": vector_literal(embedding)}).mappings().first()
        except Exception as err:  # noqa: BLE001
            logger.warning("Pencarian HNSW pgvector dilewati: %s", err)
            self.available = False
            try:
                self.db.rollback()
            except Exception:  # noqa: BLE001
                pass
            return None
        if not row:
            return None
        return float(row["similarity"]), {
            "chunk_id": str(row["id"]), "corpus_doc_id": str(row["corpus_doc_id"]),
            "title": row["title"], "category": row["category"] or "General", "chunk_text": row["chunk_text"],
            "start_char": row["start_char"], "end_char": row["end_char"],
        }
