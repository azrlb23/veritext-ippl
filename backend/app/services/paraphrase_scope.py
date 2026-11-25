from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditSentence

_CHARS_PER_PAGE = 1800
_MAX_SCOPE_CHARS = 4500


async def resolve_paraphrase_scope_text(
    db: AsyncSession, sentence: AuditSentence, mode: str
) -> str:
    """Mengambil teks sesuai cakupan: SENTENCE, PARAGRAPH (5 kalimat sekitar), atau FULL_PAGE (1 halaman)."""
    base = sentence.current_text or sentence.sentence_text
    if mode == "SENTENCE":
        return base

    stmt = (
        select(AuditSentence)
        .where(AuditSentence.audit_task_id == sentence.audit_task_id)
        .order_by(AuditSentence.sentence_index.asc())
    )
    rows = list((await db.execute(stmt)).scalars().all())
    if not rows:
        return base

    if mode == "PARAGRAPH":
        idx = sentence.sentence_index
        picked = [r for r in rows if idx - 2 <= r.sentence_index <= idx + 2]
    else:
        page_idx = max(0, (sentence.start_char or 0) // _CHARS_PER_PAGE)
        p_start, p_end = page_idx * _CHARS_PER_PAGE, (page_idx + 1) * _CHARS_PER_PAGE
        picked = [r for r in rows if p_start <= (r.start_char or 0) < p_end]

    joined = " ".join((r.current_text or r.sentence_text or "").strip() for r in picked if (r.current_text or r.sentence_text or "").strip())
    return joined[:_MAX_SCOPE_CHARS] if joined else base
