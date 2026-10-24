from datetime import datetime, timezone
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.common import APIResponse, PaginatedData
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=APIResponse[DocumentUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    audit_depth: Optional[str] = Form("FULL"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    depth = audit_depth if audit_depth in ("FULL", "TIER1_ONLY") else "FULL"
    doc, task = await DocumentService.save_uploaded_file_and_create_task(
        db=db,
        user_id=current_user.id,
        file=file,
        audit_depth=depth,
    )
    return APIResponse(
        message="Document uploaded successfully",
        data=DocumentUploadResponse(
            document_id=doc.id,
            task_id=task.id,
            celery_task_id=task.celery_task_id,
            original_filename=doc.original_filename,
            message="Naskah berhasil diunggah dan tugas audit telah diantrekan",
        ),
    )


@router.get("", response_model=APIResponse[PaginatedData[DocumentResponse]])
async def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Document).where(Document.user_id == current_user.id, Document.deleted_at.is_(None))
    count_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    query = query.order_by(Document.created_at.desc()).offset((page - 1) * limit).limit(limit)
    items = (await db.execute(query)).scalars().all()

    pages = (total + limit - 1) // limit if total > 0 else 1

    return APIResponse(
        message="Documents retrieved",
        data=PaginatedData(
            items=[DocumentResponse.model_validate(x) for x in items],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        ),
    )


@router.get("/{doc_id}", response_model=APIResponse[DocumentResponse])
async def get_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Document).where(
        Document.id == doc_id,
        Document.user_id == current_user.id,
        Document.deleted_at.is_(None),
    )
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return APIResponse(message="Document retrieved", data=DocumentResponse.model_validate(doc))


@router.delete("/{doc_id}", response_model=APIResponse[dict])
async def delete_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # UU PDP Compliance: Soft delete document and purge physical stored file from disk
    await DocumentService.delete_document(db, doc)

    return APIResponse(message="Document deleted permanently in compliance with UU PDP No. 27/2022", data={})
