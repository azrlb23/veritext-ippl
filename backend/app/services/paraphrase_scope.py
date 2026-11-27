from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditSentence

_CHARS_PER_PAGE = 1800
_MAX_SCOPE_CHARS = 4500


def _active_sentence_text(sentence: AuditSentence) -> str:
    if getattr(sentence, "is_modified", False):
        return (sentence.current_text or "").strip()
    return (sentence.current_text or sentence.sentence_text or "").strip()


def resolve_paraphrase_scope_sentences(
    ordered_sentences: list[AuditSentence], target_sentence: AuditSentence, mode: str
) -> list[AuditSentence]:
    """Memilih daftar kalimat sesuai cakupan SENTENCE, PARAGRAPH, atau FULL_PAGE."""
    mode_upper = (mode or "SENTENCE").strip().upper()
    if mode_upper == "SENTENCE" or not ordered_sentences:
        return [target_sentence]
    if mode_upper == "PARAGRAPH":
        idx = int(getattr(target_sentence, "sentence_index", 0) or 0)
        picked = [r for r in ordered_sentences if idx - 2 <= int(getattr(r, "sentence_index", 0) or 0) <= idx + 2]
    else:
        page_idx = max(0, int(getattr(target_sentence, "start_char", 0) or 0) // _CHARS_PER_PAGE)
        p_start, p_end = page_idx * _CHARS_PER_PAGE, (page_idx + 1) * _CHARS_PER_PAGE
        picked = [r for r in ordered_sentences if p_start <= int(getattr(r, "start_char", 0) or 0) < p_end]
    active = [r for r in picked if _active_sentence_text(r) or r.id == target_sentence.id]
    return active or [target_sentence]


async def resolve_paraphrase_scope_text(db: AsyncSession, sentence: AuditSentence, mode: str) -> str:
    """Mengambil teks sesuai cakupan: SENTENCE, PARAGRAPH (5 kalimat sekitar), atau FULL_PAGE (1 halaman)."""
    base = _active_sentence_text(sentence)
    if (mode or "SENTENCE").strip().upper() == "SENTENCE":
        return base
    stmt = select(AuditSentence).where(AuditSentence.audit_task_id == sentence.audit_task_id).order_by(AuditSentence.sentence_index.asc())
    rows = list((await db.execute(stmt)).scalars().all())
    picked = resolve_paraphrase_scope_sentences(rows, sentence, mode)
    joined = " ".join(t for r in picked if (t := _active_sentence_text(r)))
    return joined[:_MAX_SCOPE_CHARS] if joined else base
