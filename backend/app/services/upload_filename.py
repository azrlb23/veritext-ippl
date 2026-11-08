from __future__ import annotations

from fastapi import HTTPException, status

from app.core.config import settings

MAX_FILENAME_LENGTH = 200
RISKY_INNER_PARTS = frozenset({
    "exe", "dll", "bat", "cmd", "com", "scr", "msi", "sh", "bash", "py", "pyc", "js", "mjs", "vbs", "ps1",
    "php", "phtml", "asp", "aspx", "jsp", "cgi", "pl", "rb", "jar", "apk", "html", "htm", "svg", "zip",
    "rar", "7z", "gz", "tar", "pdf", "docx", "doc", "txt",
})


def allowed_extensions() -> list[str]:
    return [x.strip().lower() for x in settings.ALLOWED_EXTENSIONS.split(",") if x.strip()]


def _reject(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def extension_of(filename: str | None) -> str:
    """Memeriksa nama berkas dan mengembalikan ekstensi yang diizinkan (huruf kecil)."""
    name = (filename or "").strip()
    if not name or "." not in name or name.endswith("."):
        raise _reject("Filename is missing or has no valid extension.")
    if len(name) > MAX_FILENAME_LENGTH:
        raise _reject("Nama berkas terlalu panjang (maksimal 200 karakter).")
    if "/" in name or "\\" in name or ".." in name or any(ord(c) < 32 for c in name):
        raise _reject("Nama berkas tidak valid: tidak boleh memuat jalur atau karakter kontrol.")
    parts = name.lower().split(".")
    ext = parts[-1]
    allowed = allowed_extensions()
    if ext not in allowed:
        raise _reject(f"Unsupported file format '.{ext}'. Allowed: {', '.join(allowed)}")
    if any(part.strip() in RISKY_INNER_PARTS for part in parts[1:-1]):
        raise _reject("Nama berkas tidak valid: ekstensi ganda tidak diizinkan.")
    return ext
