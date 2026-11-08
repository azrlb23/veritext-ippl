import uuid
from typing import Any

from app.engine.preprocessor import TextPreprocessor
from app.engine.reference_corpus_data import BASE_REFERENCE_PAPERS, sync_corpus_records
from app.engine.reference_corpus_data_ext import EXT_REFERENCE_PAPERS
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticEngine

BUILTIN_REFERENCE_CORPUS: list[dict[str, Any]] = BASE_REFERENCE_PAPERS + EXT_REFERENCE_PAPERS
BUILTIN_REFERENCE_PAPERS = BUILTIN_REFERENCE_CORPUS


def get_builtin_corpus() -> list[dict[str, Any]]:
    return BUILTIN_REFERENCE_CORPUS


class ReferenceCorpusBank:
    """Built-in Reference Corpus Bank providing in-memory indexed reference documents."""

    _instance: "ReferenceCorpusBank | None" = None

    def __init__(self):
        self.documents = BUILTIN_REFERENCE_PAPERS
        self.lexical_engine = WinnowingLexicalEngine()
        self.semantic_engine = SemanticEngine()
        self.fingerprint_index: dict[int, list[dict[str, Any]]] = {}
        self.corpus_chunks: list[dict[str, Any]] = []
        self._build_indexes()

    @classmethod
    def get_instance(cls) -> "ReferenceCorpusBank":
        if cls._instance is None:
            cls._instance = ReferenceCorpusBank()
        return cls._instance

    def _build_indexes(self):
        self.fingerprint_index.clear()
        self.corpus_chunks.clear()
        for doc in self.documents:
            doc_id, title, category, text = doc["id"], doc["title"], doc["category"], doc["text"]
            sentences = TextPreprocessor.segment_sentences(text)
            for h_val, pos in self.lexical_engine.extract_fingerprints(text):
                self.fingerprint_index.setdefault(h_val, []).append(
                    {"doc_id": doc_id, "title": title, "category": category, "position": pos}
                )
            for s in sentences:
                self.corpus_chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "corpus_doc_id": doc_id,
                    "title": title,
                    "category": category,
                    "chunk_text": s.text,
                    "embedding": self.semantic_engine.embed_sentence(s.text),
                    "start_char": s.start_char,
                    "end_char": s.end_char,
                })

    def get_fingerprint_index(self) -> dict[int, list[dict[str, Any]]]:
        return self.fingerprint_index

    def get_corpus_chunks(self) -> list[dict[str, Any]]:
        return self.corpus_chunks

    def get_all_documents(self) -> list[dict[str, Any]]:
        return self.documents

    def sync_to_db(self, db_session) -> int:
        return sync_corpus_records(
            self.documents, self.lexical_engine, self.semantic_engine, db_session
        )
