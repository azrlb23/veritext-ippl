import hashlib
import os
import uuid
from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.corpus import CorpusDocument
from app.schemas.corpus import CorpusDocUpdateRequest


class CorpusService:
    @staticmethod
    async def list_corpus_documents(
        db: AsyncSession, category: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> tuple[List[CorpusDocument], int]:
        stmt = select(CorpusDocument).where(CorpusDocument.status != "DELETED")
        if category:
            stmt = stmt.where(CorpusDocument.category == category)
        
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(CorpusDocument.created_at.desc()).offset((page - 1) * limit).limit(limit)
        items = (await db.execute(stmt)).scalars().all()
        return list(items), total

    @staticmethod
    async def ingest_zip_corpus(
        db: AsyncSession,
        user_id: uuid.UUID,
        file: UploadFile,
        category: Optional[str] = None,
        academic_year: Optional[str] = None,
    ) -> int:
        content = await file.read()
        sha256 = hashlib.sha256(content).hexdigest()

        # Check existing
        existing = await db.execute(select(CorpusDocument).where(CorpusDocument.sha256_hash == sha256))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Corpus document with identical content hash already exists",
            )

        stored_filename = f"corpus_{uuid.uuid4().hex}.zip"
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(os.path.join(settings.UPLOAD_DIR, stored_filename), "wb") as f:
            f.write(content)

        doc = CorpusDocument(
            uploaded_by=user_id,
            title=file.filename or "Corpus Batch Archive",
            category=category or "General",
            academic_year=academic_year or "2025/2026",
            stored_filename=stored_filename,
            sha256_hash=sha256,
            status="PENDING_INDEX",
            total_chunks=0,
        )
        db.add(doc)
        await db.commit()

        # Dispatch async indexing task
        try:
            from app.workers.tasks import index_corpus_document
            index_corpus_document.delay(str(doc.id))
        except Exception:
            pass

        return 1

    @staticmethod
    async def update_corpus_doc(
        db: AsyncSession, doc_id: uuid.UUID, req: CorpusDocUpdateRequest
    ) -> CorpusDocument:
        stmt = select(CorpusDocument).where(CorpusDocument.id == doc_id, CorpusDocument.status != "DELETED")
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corpus document not found")

        if req.title:
            doc.title = req.title
        if req.category:
            doc.category = req.category
        if req.academic_year:
            doc.academic_year = req.academic_year

        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def delete_corpus_doc(db: AsyncSession, doc_id: uuid.UUID) -> bool:
        stmt = select(CorpusDocument).where(CorpusDocument.id == doc_id)
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corpus document not found")

        doc.status = "DELETED"
        await db.commit()
        return True
