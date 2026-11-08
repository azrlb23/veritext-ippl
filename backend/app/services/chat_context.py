from __future__ import annotations

import asyncio
import os

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.engine.preprocessor import TextPreprocessor
from app.engine.tier2_fallback_embedder import cosine_similarity
from app.engine.tier2_semantic import SemanticEngine
from app.models.document import Document
from app.services.safe_extract import extract_text_limited

TOP_SENTENCES_PER_MESSAGE = 6
MAX_SENTENCES_PER_DOCUMENT = 3000
MAX_SENTENCE_CHARS = 400


async def load_owned_documents(db: AsyncSession, user_id, document_ids: list) -> list[Document]:
    """Memuat naskah milik pengguna; ID yang tidak ditemukan atau milik orang lain ditolak (DOC_004)."""
    if not document_ids:
        return []
    stmt = select(Document).where(Document.id.in_(document_ids), Document.user_id == user_id, Document.deleted_at.is_(None))
    docs = list((await db.execute(stmt)).scalars().all())
    if len(docs) != len(set(document_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DOC_004: Naskah tidak ditemukan atau bukan milik Anda.")
    return docs


def _document_sentences(doc: Document) -> list[str]:
    path = os.path.join(settings.UPLOAD_DIR, doc.stored_filename or "")
    if not doc.stored_filename or not os.path.exists(path):
        return []
    text = extract_text_limited(path, doc.mime_type)
    spans = TextPreprocessor.segment_sentences(text)[:MAX_SENTENCES_PER_DOCUMENT]
    return [s.text.strip()[:MAX_SENTENCE_CHARS] for s in spans if s.text.strip()]


def select_relevant_sentences(question: str, sentences: list[str], top_k: int = TOP_SENTENCES_PER_MESSAGE) -> list[str]:
    """Memilih kalimat paling relevan terhadap pertanyaan memakai embedding MiniLM (kosinus), dikembalikan sesuai urutan naskah."""
    if not sentences:
        return []
    engine = SemanticEngine()
    q_emb = engine.embed_sentence(question)
    scored = [(cosine_similarity(q_emb, e), i) for i, e in enumerate(engine.embed_sentences(sentences))]
    best = sorted(scored, reverse=True)[:top_k]
    return [sentences[i] for _, i in sorted(best, key=lambda x: x[1])]


def build_document_context(docs: list[Document], question: str) -> str:
    """Kutipan paling relevan dari tiap naskah, siap disisipkan ke prompt."""
    blocks = []
    for doc in docs:
        picked = select_relevant_sentences(question, _document_sentences(doc))
        if picked:
            body = "\n".join(f"- {s}" for s in picked)
            blocks.append(f"Naskah \"{doc.original_filename}\":\n{body}")
    return "\n\n".join(blocks)


async def build_document_context_async(docs: list[Document], question: str) -> str:
    return await asyncio.to_thread(build_document_context, docs, question)
