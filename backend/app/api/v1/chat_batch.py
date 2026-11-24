from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.assistant_batch_service import fetch_priority_sentences
from app.services.local_similarity_check import measure_paraphrase_similarity

router = APIRouter(prefix="/chat", tags=["AI Assistant & Paraphrase"])


class CheckSimilarityRequest(BaseModel):
    original_text: str = Field(..., max_length=10000)
    rewritten_text: str = Field(..., max_length=10000)


class CheckSimilarityResponse(BaseModel):
    lexical_overlap_pct: float
    word_overlap_pct: float
    is_improved: bool


class PrioritySentenceItem(BaseModel):
    sentence_id: str
    text: str
    match_type: str
    similarity_score: float


class PrioritySentencesResponse(BaseModel):
    audit_task_id: str
    report_id: Optional[str] = None
    items: list[PrioritySentenceItem]


@router.post("/check-similarity", response_model=APIResponse[CheckSimilarityResponse])
async def check_similarity(
    payload: CheckSimilarityRequest,
    _current_user: User = Depends(get_current_user),  # noqa: B008
):
    result = measure_paraphrase_similarity(payload.original_text, payload.rewritten_text)
    return APIResponse(
        message="Pengecekan kemiripan lokal selesai",
        data=CheckSimilarityResponse(**result),
    )


@router.get("/priority-sentences", response_model=APIResponse[PrioritySentencesResponse])
async def get_priority_sentences(
    document_id: uuid.UUID = Query(...),  # noqa: B008
    limit: int = Query(5),
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    result = await fetch_priority_sentences(db, current_user.id, document_id, limit)
    return APIResponse(
        message="Daftar kalimat prioritas berhasil diambil",
        data=PrioritySentencesResponse(**result),
    )
