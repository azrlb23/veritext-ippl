from __future__ import annotations

import asyncio
import os
import re
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.engine.preprocessor import TextPreprocessor
from app.engine.tier2_fallback_embedder import cosine_similarity
from app.engine.tier2_semantic import SemanticEngine
from app.models.audit import AuditSentence, AuditTask
from app.models.document import Document
from app.services.safe_extract import extract_text_limited

TOP_SENTENCES_PER_MESSAGE = 6
MAX_SENTENCES_PER_DOCUMENT = 3000
MAX_SENTENCE_CHARS = 400
_PREFILTER_LIMIT = 120
_WORD_RE = re.compile(r"[a-zA-Z0-9À-ÿ]{2,}")


def _active_sentence_text(sent: AuditSentence) -> str:
    return (sent.current_text or "").strip() if getattr(sent, "is_modified", False) else (sent.current_text or sent.sentence_text or "").strip()


async def load_owned_documents(db: AsyncSession, user_id, document_ids: list) -> list[Document]:
    """Memuat naskah milik pengguna; ID yang tidak ditemukan atau milik orang lain ditolak (DOC_004)."""
    if not document_ids:
        return []
    stmt = select(Document).where(Document.id.in_(document_ids), Document.user_id == user_id, Document.deleted_at.is_(None))
    docs = list((await db.execute(stmt)).scalars().all())
    if len(docs) != len(set(document_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DOC_004: Naskah tidak ditemukan atau bukan milik Anda.")
    return docs


async def load_focus_sentence_context(db: AsyncSession, user_id, sentence_id) -> str:
    """Memuat kalimat fokus dan tetangganya dari hasil audit milik pengguna."""
    if not sentence_id:
        return ""
    stmt = select(AuditSentence).join(AuditTask, AuditSentence.audit_task_id == AuditTask.id).where(AuditSentence.id == sentence_id, AuditTask.user_id == user_id)
    sent = (await db.execute(stmt)).scalar_one_or_none()
    if not sent:
        return ""
    idx = int(getattr(sent, "sentence_index", 0) or 0)
    nbr_stmt = select(AuditSentence).where(AuditSentence.audit_task_id == sent.audit_task_id, AuditSentence.sentence_index.between(max(0, idx - 1), idx + 1)).order_by(AuditSentence.sentence_index.asc())
    nbrs = [t for r in (await db.execute(nbr_stmt)).scalars().all() if r.id != sent.id and (t := _active_sentence_text(r))]
    active = _active_sentence_text(sent) or (sent.sentence_text or "")
    lines = [f"Kalimat fokus yang dipilih pengguna (status: {sent.match_type}, kemiripan: {float(sent.similarity_score or 0.0):.1f}%):", f'- "{active[:MAX_SENTENCE_CHARS]}"']
    if nbrs:
        lines.append("Konteks sekitar:\n" + "\n".join(f"- {n[:MAX_SENTENCE_CHARS]}" for n in nbrs))
    return "\n".join(lines)


async def load_audited_sentences_map(db: AsyncSession, user_id, document_ids: list) -> dict[Any, list[str]]:
    """Memuat kalimat hasil audit terakhir (status SUCCESS/COMPLETED) per document_id."""
    if not document_ids:
        return {}
    task_stmt = select(AuditTask).where(AuditTask.document_id.in_(document_ids), AuditTask.user_id == user_id, AuditTask.status.in_(("SUCCESS", "COMPLETED"))).order_by(AuditTask.created_at.desc())
    latest_by_doc: dict[Any, Any] = {}
    for task in (await db.execute(task_stmt)).scalars().all():
        latest_by_doc.setdefault(task.document_id, task.id)
    if not latest_by_doc:
        return {}
    sent_stmt = select(AuditSentence).where(AuditSentence.audit_task_id.in_(list(latest_by_doc.values()))).order_by(AuditSentence.sentence_index.asc())
    task_to_doc, out = {tid: did for did, tid in latest_by_doc.items()}, {did: [] for did in latest_by_doc}
    for s in (await db.execute(sent_stmt)).scalars().all():
        did = task_to_doc.get(s.audit_task_id)
        if did is not None and len(out[did]) < MAX_SENTENCES_PER_DOCUMENT and (txt := _active_sentence_text(s)):
            out[did].append(txt[:MAX_SENTENCE_CHARS])
    return {did: sents for did, sents in out.items() if sents}


def _document_sentences(doc: Document) -> list[str]:
    path = os.path.join(settings.UPLOAD_DIR, doc.stored_filename or "")
    if not doc.stored_filename or not os.path.exists(path):
        return []
    return [s.text.strip()[:MAX_SENTENCE_CHARS] for s in TextPreprocessor.segment_sentences(extract_text_limited(path, doc.mime_type))[:MAX_SENTENCES_PER_DOCUMENT] if s.text.strip()]


def select_relevant_sentences(question: str, sentences: list[str], top_k: int = TOP_SENTENCES_PER_MESSAGE) -> list[str]:
    """Memilih kalimat paling relevan terhadap pertanyaan memakai pre-filter leksikal + MiniLM."""
    if not sentences:
        return []
    candidates = sentences
    if len(sentences) > _PREFILTER_LIMIT:
        q_words = set(_WORD_RE.findall((question or "").lower()))
        ranked = sorted(range(len(sentences)), key=lambda i: len(q_words & set(_WORD_RE.findall(sentences[i].lower()))), reverse=True)
        candidates = [sentences[i] for i in sorted(ranked[:_PREFILTER_LIMIT])]
    engine = SemanticEngine()
    q_emb = engine.embed_sentence(question)
    best = sorted([(cosine_similarity(q_emb, e), i) for i, e in enumerate(engine.embed_sentences(candidates))], reverse=True)[:top_k]
    return [candidates[i] for _, i in sorted(best, key=lambda x: x[1])]


def build_document_context(docs: list[Document], question: str, focus_context: str = "", audited_map: dict[Any, list[str]] | None = None) -> str:
    """Kutipan paling relevan dari tiap naskah (plus kalimat fokus jika ada), siap disisipkan ke prompt."""
    blocks = [focus_context] if focus_context else []
    for doc in docs:
        picked = select_relevant_sentences(question, (audited_map or {}).get(getattr(doc, "id", None)) or _document_sentences(doc))
        if picked:
            blocks.append(f'Naskah "{doc.original_filename}":\n' + "\n".join(f"- {s}" for s in picked))
    return "\n\n".join(blocks)


async def build_document_context_async(docs: list[Document], question: str, focus_context: str = "", audited_map: dict[Any, list[str]] | None = None) -> str:
    return await asyncio.to_thread(build_document_context, docs, question, focus_context, audited_map)
