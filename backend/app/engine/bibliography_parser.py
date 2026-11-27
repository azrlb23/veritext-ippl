from __future__ import annotations

import re
from dataclasses import dataclass

_BIB_HEADING_RE = re.compile(
    r"^[ \t]*(?:#{1,4}[ \t]+|\*{2})?(?:(?:BAB\s+[IVX\d]+|[IVX]+\.?|\d+(?:\.\d+)*\.?)[ \t:\-]+)?"
    r"(?:Daftar\s+Pustaka|Daftar\s+Referensi|Referensi|References|Bibliography|Kepustakaan)"
    r"[ \t]*:?(?:\*{2})?[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
_POST_BIB_HEADING_RE = re.compile(
    r"^[ \t]*(?:#{1,4}[ \t]+|\*{2})?(?:(?:BAB\s+[IVX\d]+|[IVX]+\.?|\d+(?:\.\d+)*\.?)[ \t:\-]+)?"
    r"(?:Lampiran|Appendix|Appendices|Biodata\s+Penulis|Riwayat\s+Hidup)"
    r"[ \t]*:?(?:\*{2})?[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
_DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b")
_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})[a-z]?\b")
_QUOTED_TITLE_RE = re.compile(r"[\"“]([^\"”\n]{12,240})[\"”]")
_APA_TITLE_RE = re.compile(r"\(\s*(?:19|20)\d{2}[a-z]?\s*\)[.,]?\s+([^.?!\n]{12,240})[.?!]")
_YEAR_DOT_TITLE_RE = re.compile(r"\b(?:19|20)\d{2}[a-z]?\.\s+([^.?!\n]{12,240})[.?!]")
_ENTRY_START_RE = re.compile(r"^(?:\[\d+\]\s+|\d{1,3}[.)]\s+|[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ'\-]{1,30},\s+[A-ZÀ-ÖØ-Ý])")
_URL_RE = re.compile(r"https?://\S+|doi:\s*\S+", re.IGNORECASE)


@dataclass
class BibliographyEntry:
    raw_text: str
    start_char: int
    end_char: int
    doi: str | None
    year: str | None
    title_query: str


def find_bibliography_section(text: str) -> tuple[int, str] | None:
    if not text or not text.strip():
        return None
    matches = list(_BIB_HEADING_RE.finditer(text))
    if not matches:
        return None
    chosen = matches[-1]
    body_start = chosen.end()
    tail = text[body_start:]
    post_match = _POST_BIB_HEADING_RE.search(tail)
    body_end = body_start + post_match.start() if post_match else len(text)
    if body_end <= body_start:
        return None
    return body_start, text[body_start:body_end]


def extract_doi(entry_text: str) -> str | None:
    match = _DOI_RE.search(entry_text or "")
    if not match:
        return None
    return match.group(1).rstrip(".,;)]")


def extract_title_query(entry_text: str) -> str:
    cleaned = " ".join((entry_text or "").split())
    if not cleaned:
        return ""
    if m := _QUOTED_TITLE_RE.search(cleaned):
        candidate = m.group(1).strip(" .,;:")
        if len(candidate.split()) >= 3:
            return candidate
    if m := _APA_TITLE_RE.search(cleaned):
        candidate = m.group(1).strip(" .,;:")
        if len(candidate.split()) >= 3:
            return candidate
    if m := _YEAR_DOT_TITLE_RE.search(cleaned):
        candidate = m.group(1).strip(" .,;:")
        if len(candidate.split()) >= 3:
            return candidate
    stripped = re.sub(r"^(?:\[\d+\]|\d{1,3}[.)])\s*", "", cleaned)
    stripped = _URL_RE.sub("", stripped)
    stripped = re.sub(r"\s+", " ", stripped).strip(" .,;:")
    return " ".join(stripped.split()[:14])


def _split_entry_spans(section_text: str, base_offset: int) -> list[tuple[str, int, int]]:
    lines = section_text.splitlines(keepends=True)
    groups: list[tuple[int, int]] = []
    cur_start: int | None = None
    cur_end = 0
    pos = 0

    for line in lines:
        line_start, line_end = pos, pos + len(line)
        pos = line_end
        stripped = line.strip()
        if not stripped:
            if cur_start is not None:
                groups.append((cur_start, cur_end))
                cur_start = None
            continue
        if cur_start is None:
            cur_start, cur_end = line_start, line_end
        elif _ENTRY_START_RE.match(stripped):
            groups.append((cur_start, cur_end))
            cur_start, cur_end = line_start, line_end
        else:
            cur_end = line_end

    if cur_start is not None:
        groups.append((cur_start, cur_end))

    out: list[tuple[str, int, int]] = []
    for s_off, e_off in groups:
        chunk = section_text[s_off:e_off]
        lead = len(chunk) - len(chunk.lstrip())
        trail = len(chunk) - len(chunk.rstrip())
        trimmed = chunk.strip()
        if trimmed:
            out.append((trimmed, base_offset + s_off + lead, base_offset + e_off - trail))
    return out


def parse_bibliography_entries(text: str, max_entries: int = 20) -> list[BibliographyEntry]:
    section = find_bibliography_section(text)
    if not section:
        return []
    base_offset, section_text = section
    entries: list[BibliographyEntry] = []
    for raw, start_c, end_c in _split_entry_spans(section_text, base_offset):
        if len(raw) < 15 or len(raw.split()) < 3:
            continue
        ym = _YEAR_RE.search(raw)
        entries.append(
            BibliographyEntry(
                raw_text=raw,
                start_char=start_c,
                end_char=end_c,
                doi=extract_doi(raw),
                year=ym.group(1) if ym else None,
                title_query=extract_title_query(raw),
            )
        )
        if len(entries) >= max_entries:
            break
    return entries
