from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str, mime_type: str | None = None) -> str:
    """Extracts text content from PDF, DOCX, or plain text files."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""

    # 1. Plain text
    if ext in ("txt", "text", "md") or (mime_type and "text/plain" in mime_type):
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                with open(file_path, encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        with open(file_path, encoding="utf-8", errors="replace") as f:
            return f.read()

    # 2. PDF extraction using pdfplumber
    if ext == "pdf" or (mime_type and "pdf" in mime_type):
        try:
            import pdfplumber

            text_parts: list[str] = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            if text_parts:
                return "\n\n".join(text_parts)
        except Exception as pdf_err:  # noqa: BLE001
            logger.debug("PDF extraction skipped: %s", pdf_err)

    # 3. DOCX extraction using python-docx
    if ext in ("docx", "doc") or (mime_type and "wordprocessingml" in mime_type):
        try:
            import docx

            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            if paragraphs:
                return "\n\n".join(paragraphs)
        except Exception as docx_err:  # noqa: BLE001
            logger.debug("DOCX extraction skipped: %s", docx_err)

    # Fallback binary text read
    try:
        with open(file_path, "rb") as f:
            return f.read().decode("utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        return f"Error reading file content: {e}"
