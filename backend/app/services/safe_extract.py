from __future__ import annotations

import subprocess
import sys

from fastapi import HTTPException, status

from app.core.config import settings


def _reject(code: int, detail: str) -> HTTPException:
    return HTTPException(status_code=code, detail=detail)


def extract_text_limited(path: str, mime_type: str | None = None) -> str:
    """Mengekstrak teks lewat subproses dengan batas waktu dan batas halaman PDF."""
    try:
        proc = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "app.engine.extract_cli", path, mime_type or "", str(settings.MAX_PDF_PAGES)],
            capture_output=True,
            timeout=settings.EXTRACTION_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise _reject(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Pemrosesan naskah melebihi {settings.EXTRACTION_TIMEOUT_SECONDS} detik dan dihentikan. Sederhanakan berkas lalu coba lagi.",
        ) from None
    if proc.returncode == 3:
        raise _reject(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"PDF melebihi batas {settings.MAX_PDF_PAGES} halaman. Pecah naskah menjadi beberapa berkas.",
        )
    if proc.returncode != 0:
        raise _reject(status.HTTP_422_UNPROCESSABLE_ENTITY, "Teks naskah tidak dapat dibaca dari berkas ini.")
    return proc.stdout.decode("utf-8", errors="replace")
