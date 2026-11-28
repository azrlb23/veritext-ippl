from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatSession, ChatSessionDocument

TITLE_CHARS = 60


async def get_owned_session(db: AsyncSession, user_id, session_id) -> ChatSession:
    session = (await db.execute(select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id))).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesi asisten tidak ditemukan.")
    return session


async def create_session(db: AsyncSession, user_id, document_ids: list, first_prompt: str) -> ChatSession:
    title = first_prompt.strip().replace("\n", " ")[:TITLE_CHARS] or "Konsultasi Naskah"
    session = ChatSession(id=uuid.uuid4(), user_id=user_id, document_id=document_ids[0] if len(document_ids) == 1 else None, title=title)
    db.add(session)
    await db.flush()
    for doc_id in document_ids:
        db.add(ChatSessionDocument(session_id=session.id, document_id=doc_id))
    return session


async def session_document_ids(db: AsyncSession, session_id) -> list:
    rows = await db.execute(select(ChatSessionDocument.document_id).where(ChatSessionDocument.session_id == session_id))
    return list(rows.scalars().all())


async def recent_history(db: AsyncSession, session_id, limit: int = 6) -> list[tuple[str, str]]:
    rows = await db.execute(
        select(ChatMessage.role, ChatMessage.content).where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc()).limit(limit)
    )
    return [(r, c) for r, c in reversed(rows.all())]


async def list_sessions(db: AsyncSession, user_id) -> list[dict]:
    sessions = (await db.execute(
        select(ChatSession).where(ChatSession.user_id == user_id, ChatSession.is_active.is_(True))
        .order_by(ChatSession.updated_at.desc()).limit(50)
    )).scalars().all()
    if not sessions:
        return []

    sids = [s.id for s in sessions]
    doc_rows = (await db.execute(select(ChatSessionDocument.session_id, ChatSessionDocument.document_id).where(ChatSessionDocument.session_id.in_(sids)))).all()
    docs_map: dict = {sid: [] for sid in sids}
    for sid, doc_id in doc_rows:
        docs_map[sid].append(doc_id)

    stats_sq = (
        select(ChatMessage.session_id.label("sid"), func.count(ChatMessage.id).label("cnt"), func.max(ChatMessage.created_at).label("max_ts"))
        .where(ChatMessage.session_id.in_(sids)).group_by(ChatMessage.session_id).subquery()
    )
    counts = {sid: int(cnt or 0) for sid, cnt in (await db.execute(select(stats_sq.c.sid, stats_sq.c.cnt))).all()}
    last_msg: dict = {}
    if counts:
        latest_rows = (await db.execute(
            select(ChatMessage.session_id, ChatMessage.content)
            .join(stats_sq, (ChatMessage.session_id == stats_sq.c.sid) & (ChatMessage.created_at == stats_sq.c.max_ts))
        )).all()
        last_msg = {sid: content for sid, content in latest_rows}

    return [
        {
            "id": s.id, "title": s.title, "document_ids": docs_map.get(s.id, []),
            "last_message": (last_msg.get(s.id) or "")[:160] or None,
            "message_count": counts.get(s.id, 0), "updated_at": s.updated_at,
        }
        for s in sessions
    ]
