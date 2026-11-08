from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.chat import ChatHistoryItem, ChatSessionItem
from app.schemas.common import APIResponse
from app.services.chat_sessions import get_owned_session, list_sessions

router = APIRouter(prefix="/chat/sessions", tags=["AI Assistant & Paraphrase"])


@router.get("", response_model=APIResponse[list[ChatSessionItem]])
async def get_sessions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):  # noqa: B008
    items = await list_sessions(db, current_user.id)
    return APIResponse(message="Sesi asisten", data=[ChatSessionItem(**i) for i in items])


@router.get("/{session_id}/messages", response_model=APIResponse[list[ChatHistoryItem]])
async def get_session_messages(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    await get_owned_session(db, current_user.id, session_id)
    rows = (await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at))).scalars().all()
    return APIResponse(message="Riwayat pesan", data=[ChatHistoryItem.model_validate(r) for r in rows])


@router.delete("/{session_id}", response_model=APIResponse[dict])
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    session = await get_owned_session(db, current_user.id, session_id)
    await db.delete(session)
    await db.commit()
    return APIResponse(message="Sesi asisten dihapus permanen", data={})
