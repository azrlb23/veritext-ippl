"""Ekstraksi teks dalam proses terpisah agar bisa dihentikan paksa saat melewati batas waktu."""
from __future__ import annotations

import sys


def main(path: str, mime_type: str, max_pdf_pages: int) -> int:
    ext = path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        import pdfplumber

        with pdfplumber.open(path) as pdf:
            if len(pdf.pages) > max_pdf_pages:
                return 3
            sys.stdout.write("\n\n".join(filter(None, (p.extract_text() for p in pdf.pages))))
        return 0
    from app.engine.file_text_extractor import extract_text_from_file

    sys.stdout.write(extract_text_from_file(path, mime_type=mime_type or None))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], int(sys.argv[3])))
