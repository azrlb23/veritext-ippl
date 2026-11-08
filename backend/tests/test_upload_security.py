from __future__ import annotations

import io
import os
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.services.upload_charging import estimate_upload, stage_upload
from app.services.upload_filename import extension_of
from app.services.upload_limits import enforce_active_audit_limit, enforce_rate_limit

BODY = ("kata " * 80).strip()


@pytest.fixture(autouse=True)
def isolated_upload_dir(tmp_path):
    with patch.object(settings, "UPLOAD_DIR", str(tmp_path)):
        yield tmp_path


def _file(data: bytes, name: str, mime: str = "text/plain") -> AsyncMock:
    f = AsyncMock()
    f.filename = name
    f.content_type = mime
    f.read.return_value = data
    return f


def _docx(words: int = 80, with_body: bool = True) -> bytes:
    import docx

    buf = io.BytesIO()
    document = docx.Document()
    document.add_paragraph(("kata " * words).strip())
    document.save(buf)
    data = buf.getvalue()
    if with_body:
        return data
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("readme.xml", "x")
    return out.getvalue()


@pytest.mark.parametrize("name", ["a.pdf.exe", "../a.txt", "dir/a.txt", "a\\b.txt", "x.php.txt", "a.txt.", "noext", "", "a.exe", "a..txt"])
def test_filename_rejected(name):
    with pytest.raises(HTTPException) as exc:
        extension_of(name)
    assert exc.value.status_code == 400


@pytest.mark.parametrize("name", ["naskah.txt", "Laporan v1.2.PDF", "bab-1.docx"])
def test_filename_accepted(name):
    assert extension_of(name) in ("txt", "pdf", "docx")


async def test_txt_with_nul_byte_rejected_and_removed(isolated_upload_dir):
    with pytest.raises(HTTPException) as exc:
        await stage_upload(_file(b"abc\x00" + BODY.encode(), "a.txt"), "PREMIUM")
    assert exc.value.status_code == 422
    assert os.listdir(isolated_upload_dir) == []


async def test_pdf_extension_with_text_content_rejected():
    with pytest.raises(HTTPException) as exc:
        await stage_upload(_file(BODY.encode(), "a.pdf", "application/pdf"), "PREMIUM")
    assert exc.value.status_code == 422


async def test_docx_without_document_xml_rejected():
    with pytest.raises(HTTPException) as exc:
        await stage_upload(_file(_docx(with_body=False), "a.docx", "application/octet-stream"), "PREMIUM")
    assert exc.value.status_code == 422


async def test_txt_that_is_actually_zip_rejected():
    with pytest.raises(HTTPException) as exc:
        await stage_upload(_file(_docx(), "a.txt"), "PREMIUM")
    assert exc.value.status_code == 422


async def test_declared_mime_conflicting_with_content_rejected():
    with pytest.raises(HTTPException) as exc:
        await stage_upload(_file(BODY.encode(), "a.txt", "application/pdf"), "PREMIUM")
    assert exc.value.status_code == 422


async def test_zip_bomb_docx_rejected():
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("word/document.xml", b"0" * (5 * 1024 * 1024))
    with patch.object(settings, "MAX_DOCX_COMPRESSION_RATIO", 100):
        with pytest.raises(HTTPException) as exc:
            await stage_upload(_file(out.getvalue(), "bom.docx", "application/octet-stream"), "PREMIUM")
    assert exc.value.status_code == 422


async def test_valid_docx_counted_via_subprocess():
    _, _, _, words, cost = await stage_upload(_file(_docx(80), "ok.docx", "application/octet-stream"), "PREMIUM")
    assert words == 80
    assert cost == 1


async def test_short_text_rejected_doc_003(isolated_upload_dir):
    with pytest.raises(HTTPException) as exc:
        await stage_upload(_file(b"hanya sepuluh kata saja", "a.txt"), "PREMIUM")
    assert exc.value.status_code == 422
    assert "Minimal 50 kata" in exc.value.detail
    assert os.listdir(isolated_upload_dir) == []


async def test_estimate_also_rejects_short_text():
    with pytest.raises(HTTPException) as exc:
        await estimate_upload(_file(b"terlalu pendek", "a.txt"), "FREE")
    assert exc.value.status_code == 422


def _pdf(pages: int) -> bytes:
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    pdf = canvas.Canvas(buf)
    for _ in range(pages):
        pdf.drawString(72, 720, "kata " * 10)
        pdf.showPage()
    pdf.save()
    return buf.getvalue()


async def test_pdf_page_limit_enforced():
    with patch.object(settings, "MAX_PDF_PAGES", 2):
        with pytest.raises(HTTPException) as exc:
            await stage_upload(_file(_pdf(4), "a.pdf", "application/pdf"), "PREMIUM")
    assert exc.value.status_code == 422
    assert "halaman" in exc.value.detail


async def test_valid_pdf_counted():
    _, _, _, words, _ = await stage_upload(_file(_pdf(6), "a.pdf", "application/pdf"), "PREMIUM")
    assert words == 60


async def test_active_audit_limit_blocks_fourth_job():
    db = MagicMock()
    result = MagicMock()
    result.scalar.return_value = settings.MAX_ACTIVE_AUDITS_PER_USER
    db.execute = AsyncMock(return_value=result)
    with pytest.raises(HTTPException) as exc:
        await enforce_active_audit_limit(db, "u1")
    assert exc.value.status_code == 429


async def test_rate_limit_blocks_after_limit_and_fails_open_without_redis():
    client = MagicMock()
    client.incr = AsyncMock(return_value=settings.UPLOAD_RATE_LIMIT_PER_MINUTE + 1)
    client.expire = AsyncMock()
    client.aclose = AsyncMock()
    with patch("redis.asyncio.from_url", return_value=client):
        with pytest.raises(HTTPException) as exc:
            await enforce_rate_limit("u1", "upload")
    assert exc.value.status_code == 429
    with patch("redis.asyncio.from_url", side_effect=OSError("down")):
        await enforce_rate_limit("u1", "upload")
