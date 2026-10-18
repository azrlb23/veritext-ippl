from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import APIResponse, PaginatedData
from app.schemas.corpus import CorpusDocResponse, CorpusDocUpdateRequest, CorpusIngestResponse
from app.services.corpus_service import CorpusService

router = APIRouter(prefix="/corpus", tags=["Corpus"])


@router.post("/ingest", response_model=APIResponse[CorpusIngestResponse], status_code=status.HTTP_201_CREATED)
async def ingest_corpus(
    file: UploadFile = File(...),
    category: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(require_role("REVIEWER", "ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    queued = await CorpusService.ingest_zip_corpus(db, current_user.id, file, category, academic_year)
    return APIResponse(
        message="Corpus archive ingested and queued for indexing",
        data=CorpusIngestResponse(queued_count=queued, message="Indexing started asynchronously"),
    )


@router.get("", response_model=APIResponse[PaginatedData[CorpusDocResponse]])
async def list_corpus(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("REVIEWER", "ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await CorpusService.list_corpus_documents(db, category=category, page=page, limit=limit)
    pages = (total + limit - 1) // limit if total > 0 else 1

    return APIResponse(
        message="Corpus documents retrieved",
        data=PaginatedData(
            items=[CorpusDocResponse.model_validate(x) for x in items],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        ),
    )


@router.patch("/{doc_id}", response_model=APIResponse[CorpusDocResponse])
async def update_corpus(
    doc_id: uuid.UUID,
    req: CorpusDocUpdateRequest,
    current_user: User = Depends(require_role("REVIEWER", "ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    doc = await CorpusService.update_corpus_doc(db, doc_id, req)
    return APIResponse(message="Corpus metadata updated", data=CorpusDocResponse.model_validate(doc))


@router.delete("/{doc_id}", response_model=APIResponse[dict])
async def delete_corpus(
    doc_id: uuid.UUID,
    current_user: User = Depends(require_role("REVIEWER", "ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    await CorpusService.delete_corpus_doc(db, doc_id)
    return APIResponse(message="Corpus document marked as deleted", data={})
