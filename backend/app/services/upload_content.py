from __future__ import annotations

import zipfile

from fastapi import HTTPException, status

PDF_MAGIC = b"%PDF-"
ZIP_MAGICS = (b"PK\x03\x04",)
MIME_KINDS = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}


def _reject(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def docx_is_safe(path: str, max_bytes: int, max_ratio: int) -> bool:
    """DOCX harus ZIP berisi word/document.xml dan tidak berpotensi ZIP bomb."""
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) > 5000 or "word/document.xml" not in {i.filename for i in infos}:
                return False
            total = sum(i.file_size for i in infos)
            packed = max(1, sum(i.compress_size for i in infos))
            return total <= max_bytes and total / packed <= max_ratio
    except (zipfile.BadZipFile, OSError):
        return False


def text_is_decodable(path: str) -> bool:
    with open(path, "rb") as handle:
        data = handle.read()
    if b"\x00" in data:
        return False
    for encoding in ("utf-8", "cp1252"):
        try:
            data.decode(encoding)
            return True
        except UnicodeDecodeError:
            continue
    return False


def verify_content(path: str, ext: str, declared_mime: str | None, max_docx_bytes: int, max_ratio: int) -> None:
    """Menolak berkas yang isinya tidak cocok dengan ekstensi atau tipe MIME yang diumumkan."""
    with open(path, "rb") as handle:
        head = handle.read(8)
    if ext == "pdf":
        ok = head.startswith(PDF_MAGIC)
    elif ext == "docx":
        ok = head.startswith(ZIP_MAGICS) and docx_is_safe(path, max_docx_bytes, max_ratio)
    else:
        ok = not head.startswith(PDF_MAGIC) and not head.startswith(ZIP_MAGICS) and text_is_decodable(path)
    if not ok:
        raise _reject("Isi berkas tidak sesuai dengan ekstensinya atau berkas tidak aman. Unggah PDF, DOCX, atau TXT yang asli.")
    mime_kind = MIME_KINDS.get((declared_mime or "").split(";")[0].strip().lower())
    if mime_kind and mime_kind != ext:
        raise _reject("Tipe berkas yang diumumkan bertentangan dengan isi berkas.")
