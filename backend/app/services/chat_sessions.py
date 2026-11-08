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
        select(ChatSession).where(ChatSession.user_id == user_id, ChatSession.is_active.is_(True)).order_by(ChatSession.updated_at.desc())
    )).scalars().all()
    items = []
    for s in sessions:
        count = (await db.execute(select(func.count()).select_from(ChatMessage).where(ChatMessage.session_id == s.id))).scalar() or 0
        last = (await db.execute(
            select(ChatMessage.content).where(ChatMessage.session_id == s.id).order_by(ChatMessage.created_at.desc()).limit(1)
        )).scalar_one_or_none()
        items.append({
            "id": s.id, "title": s.title, "document_ids": await session_document_ids(db, s.id),
            "last_message": (last or "")[:160] or None, "message_count": count, "updated_at": s.updated_at,
        })
    return items
