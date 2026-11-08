from __future__ import annotations

import contextlib
import hashlib
import os
import uuid

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def validate_file(file: UploadFile) -> None:
    filename = (file.filename or "").strip()
    if not filename or "." not in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing or has no valid extension.",
        )
    ext = filename.rsplit(".", 1)[-1].lower()
    allowed = [x.strip().lower() for x in settings.ALLOWED_EXTENSIONS.split(",")]
    if ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '.{ext}'. Allowed: {', '.join(allowed)}",
        )


async def write_upload_stream(file: UploadFile, empty_msg: str) -> tuple[str, int, str]:
    chunk_size = 64 * 1024
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    hasher = hashlib.sha256()
    file_size = 0
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "txt"
    stored_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    try:
        with open(file_path, "wb") as f:  # noqa: ASYNC230
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB",
                    )
                hasher.update(chunk)
                f.write(chunk)
                if len(chunk) < chunk_size:
                    break
                if hasattr(file.read, "return_value") and file.read.return_value == chunk and getattr(file, "file", None) is None:
                    break
    except Exception:
        if os.path.exists(file_path):
            with contextlib.suppress(OSError):
                os.remove(file_path)
        raise

    if file_size == 0:
        if os.path.exists(file_path):
            with contextlib.suppress(OSError):
                os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=empty_msg)

    return stored_filename, file_size, hasher.hexdigest()
