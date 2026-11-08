from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class SentenceSpan:
    """Represents a segmented sentence with character offset coordinates in the original manuscript."""
    index: int
    text: str
    start_char: int
    end_char: int
    word_count: int
    tokens: list[str] = field(default_factory=list)
    clean_text: str = ""
    is_citation: bool = False


class TextPreprocessor:
    """Accurate manuscript text extraction, normalization, and sentence segmentation."""

    ABBREVIATIONS: ClassVar[set[str]] = {
        "dr", "prof", "ir", "drs", "dra", "h", "hj", "mr", "mrs", "ms",
        "vol", "no", "hal", "hlm", "dkk", "et al", "ed", "etc", "e.g", "i.e",
        "vs", "jan", "feb", "mar", "apr", "mei", "jun", "jul", "ags", "agu",
        "sep", "okt", "nov", "des", "ibid", "op cit", "loc cit", "k.p", "s.pd",
        "m.kom", "m.sc", "ph.d", "b.sc", "s.t", "m.t", "s.si", "m.si",
    }

    CITATION_REGEX = re.compile(
        r"(\[\d+(?:[,\s\-]+\d+)*\])|"
        r"(\([A-Z][a-zA-Z\s\.,]+(?:\s+(?:dkk|et al)\.?)?,?\s*(?:19|20)\d{2}[a-z]?\))|"
        r"(\b(?:Daftar Pustaka|Referensi|Bibliography)\b)",
        re.IGNORECASE,
    )

    @classmethod
    def normalize_whitespace(cls, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip() if text else ""

    @classmethod
    def case_folding(cls, text: str) -> str:
        return text.lower() if text else ""

    @classmethod
    def remove_punctuation(cls, text: str) -> str:
        return re.sub(r"[^\w\s]", "", text) if text else ""

    @classmethod
    def clean_for_lexical(cls, text: str) -> str:
        return re.sub(r"[^a-z0-9]", "", cls.case_folding(text)) if text else ""

    @classmethod
    def tokenize_words(cls, text: str) -> list[str]:
        if not text:
            return []
        return re.findall(r"\b[a-z0-9\u00C0-\u017F\-]+\b", cls.case_folding(text))

    @classmethod
    def is_citation_sentence(cls, sentence: str) -> bool:
        if not sentence:
            return False
        stripped = sentence.strip()
        if stripped.startswith("[") and re.match(r"^\[\d+\]", stripped):
            return True
        return bool(cls.CITATION_REGEX.search(sentence) and len(cls.tokenize_words(sentence)) <= 6)

    @classmethod
    def _create_span(cls, original_text: str, start: int, end: int, index: int) -> SentenceSpan | None:
        trimmed, adj_start, adj_end = cls._trim_span(original_text, start, end)
        if not trimmed:
            return None
        tokens = cls.tokenize_words(trimmed)
        return SentenceSpan(
            index=index, text=trimmed, start_char=adj_start, end_char=adj_end,
            word_count=len(tokens), tokens=tokens,
            clean_text=cls.normalize_whitespace(cls.case_folding(trimmed)),
            is_citation=cls.is_citation_sentence(trimmed),
        )

    @classmethod
    def segment_sentences(cls, original_text: str) -> list[SentenceSpan]:
        if not original_text or not original_text.strip():
            return []
        spans: list[SentenceSpan] = []
        n, current_start, last_pos = len(original_text), 0, 0
        boundary_pattern = re.compile(r"([.!?]+)(?:\s+|\n+|$)|(\n\s*\n+)")

        for match in boundary_pattern.finditer(original_text):
            delim_start, delim_end = match.start(), match.end()
            is_valid, matched_delim = True, match.group(1)
            if matched_delim and "." in matched_delim:
                preceding = re.search(r"(\b[a-zA-Z\.]+)\s*$", original_text[last_pos:delim_start])
                if preceding:
                    word = preceding.group(1).lower().rstrip(".")
                    if word in cls.ABBREVIATIONS or (len(word) == 1 and word.isalpha()):
                        is_valid = False
                if delim_start > 0 and delim_end < n:
                    before, after = original_text[delim_start - 1], original_text[delim_start + 1]
                    if before.isdigit() and after.isdigit():
                        is_valid = False
            if not is_valid:
                continue

            chunk_end = delim_start + (len(matched_delim) if matched_delim else 0)
            span = cls._create_span(original_text, current_start, chunk_end, len(spans))
            if span:
                spans.append(span)
            current_start = delim_end
            last_pos = current_start

        if current_start < n:
            span = cls._create_span(original_text, current_start, n, len(spans))
            if span:
                spans.append(span)
        return spans

    @staticmethod
    def _trim_span(source: str, start: int, end: int) -> tuple[str, int, int]:
        sub = source[start:end]
        if not sub.strip():
            return "", start, start
        leading_ws = len(sub) - len(sub.lstrip())
        adj_start = start + leading_ws
        trailing_ws = len(sub) - len(sub.rstrip())
        adj_end = end - trailing_ws
        return source[adj_start:adj_end], adj_start, adj_end

    @classmethod
    def extract_text_from_file(cls, file_path: str, mime_type: str | None = None) -> str:
        """Extracts text content from PDF, DOCX, or plain text files."""
        from app.engine.file_text_extractor import extract_text_from_file
        return extract_text_from_file(file_path, mime_type=mime_type)
