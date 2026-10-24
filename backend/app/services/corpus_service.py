import hashlib
import os
import uuid
from typing import Any, List, Optional
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
        filename = (file.filename or "").strip()
        if not filename or not filename.lower().endswith(".zip"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported corpus file format. Only ZIP archives (.zip) are allowed.",
            )

        content = await file.read()
        file_size = len(content)
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corpus archive is empty (0 bytes). Please upload a valid ZIP file.",
            )

        max_corpus_bytes = 100 * 1024 * 1024  # 100 MB
        if file_size > max_corpus_bytes:
            raise HTTPException(
                status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
                detail="Corpus archive exceeds maximum allowed size of 100MB.",
            )

        if not content.startswith(b"PK"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ZIP archive header. The uploaded file is corrupted or not a valid ZIP archive.",
            )

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
        stmt = select(CorpusDocument).where(CorpusDocument.id == doc_id, CorpusDocument.status != "DELETED")
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corpus document not found")

        # Cascade cleanup: remove child chunks and lexical fingerprints
        from sqlalchemy import delete
        from app.models.corpus import DocumentChunk, LexicalFingerprint

        await db.execute(delete(DocumentChunk).where(DocumentChunk.corpus_doc_id == doc_id))
        await db.execute(delete(LexicalFingerprint).where(LexicalFingerprint.corpus_doc_id == doc_id))

        # Purge physical corpus file from disk if present
        if doc.stored_filename:
            file_path = os.path.join(settings.UPLOAD_DIR, doc.stored_filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

        doc.status = "DELETED"
        await db.commit()
        return True

    @staticmethod
    def extract_zip_safely(
        zip_file: Any,
        target_dir: str,
        max_uncompressed_bytes: int = 200 * 1024 * 1024,
    ) -> List[str]:
        """
        Safely extracts a ZIP archive into target_dir with robust protections against:
        1. Zip-Slip (Directory Traversal attacks via relative path "../" or absolute path).
        2. Zip-Bomb (Resource exhaustion DoS attacks via malicious compression ratios).
        3. Symlink Hijacking (prohibits symbolic links in archive headers).
        4. Bad/Corrupt ZIP archives.
        Returns a list of extracted file paths.
        """
        import stat
        import zipfile

        target_dir_abs = os.path.abspath(target_dir)
        extracted_paths: List[str] = []

        try:
            zf = zip_file if isinstance(zip_file, zipfile.ZipFile) else zipfile.ZipFile(zip_file)
        except (zipfile.BadZipFile, zipfile.LargeZipFile) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Corrupted or invalid ZIP archive: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to open archive: {str(e)}",
            )

        try:
            infolist = zf.infolist()
            if not infolist:
                return []

            total_uncompressed_bytes = 0

            # 1. Validation pass: check paths, symlinks, and cumulative sizes
            for info in infolist:
                # Anti Symlink: Reject symbolic link headers in archive members
                mode = (info.external_attr >> 16) & 0o177777
                if stat.S_ISLNK(mode):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Security violation: Symbolic links in archive members ('{info.filename}') are strictly prohibited.",
                    )

                total_uncompressed_bytes += info.file_size
                if total_uncompressed_bytes > max_uncompressed_bytes:
                    threshold_desc = (
                        f"{max_uncompressed_bytes // (1024 * 1024)}MB"
                        if max_uncompressed_bytes >= 1024 * 1024
                        else f"{max_uncompressed_bytes} bytes"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Zip-bomb detected: Total uncompressed size exceeds maximum allowed threshold "
                            f"of {threshold_desc}."
                        ),
                    )

                # Destination path validation (Anti Zip-Slip)
                dest_path = os.path.abspath(os.path.join(target_dir_abs, info.filename))
                if not dest_path.startswith(target_dir_abs + os.sep) and dest_path != target_dir_abs:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Zip-slip vulnerability detected: Attempted directory traversal in archive member '{info.filename}'.",
                    )

            # 2. Safe extraction pass with streaming threshold guard
            actual_uncompressed_bytes = 0
            for info in infolist:
                dest_path = os.path.abspath(os.path.join(target_dir_abs, info.filename))
                if info.is_dir():
                    os.makedirs(dest_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    with zf.open(info) as src, open(dest_path, "wb") as dst:
                        while chunk := src.read(65536):
                            actual_uncompressed_bytes += len(chunk)
                            if actual_uncompressed_bytes > max_uncompressed_bytes:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Zip-bomb detected: Decompressed stream exceeded maximum threshold.",
                                )
                            dst.write(chunk)
                    extracted_paths.append(dest_path)

            return extracted_paths
        finally:
            if not isinstance(zip_file, zipfile.ZipFile):
                zf.close()


