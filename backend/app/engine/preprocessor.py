import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class SentenceSpan:
    """Represents a segmented sentence with character offset coordinates in the original manuscript."""
    index: int
    text: str
    start_char: int
    end_char: int
    word_count: int
    tokens: List[str] = field(default_factory=list)
    clean_text: str = ""
    is_citation: bool = False


class TextPreprocessor:
    """Accurate manuscript text extraction, normalization, and sentence segmentation.
    
    Tracks character offsets (start_char, end_char) mapped directly to the original manuscript text
    to support granular heatmap visualization.
    """

    # Common Indonesian & academic abbreviations that should not trigger sentence boundaries
    ABBREVIATIONS = {
        "dr", "prof", "ir", "drs", "dra", "h", "hj", "mr", "mrs", "ms",
        "vol", "no", "hal", "hlm", "dkk", "et al", "ed", "etc", "e.g", "i.e",
        "vs", "jan", "feb", "mar", "apr", "mei", "jun", "jul", "ags", "agu",
        "sep", "okt", "nov", "des", "ibid", "op cit", "loc cit", "k.p", "s.pd",
        "m.kom", "m.sc", "ph.d", "b.sc", "s.t", "m.t", "s.si", "m.si",
    }

    # Citation patterns (e.g. "[1]", "(Smith, 2020)", "(Santoso dkk., 2023)")
    CITATION_REGEX = re.compile(
        r"(\[\d+(?:[,\s\-]+\d+)*\])|"
        r"(\([A-Z][a-zA-Z\s\.,]+(?:\s+(?:dkk|et al)\.?)?,?\s*(?:19|20)\d{2}[a-z]?\))|"
        r"(\b(?:Daftar Pustaka|Referensi|Bibliography)\b)",
        re.IGNORECASE,
    )

    @classmethod
    def normalize_whitespace(cls, text: str) -> str:
        """Replaces redundant tabs, carriage returns, and multiple spaces with standard space."""
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def case_folding(cls, text: str) -> str:
        """Converts text to standard lowercase."""
        return text.lower() if text else ""

    @classmethod
    def remove_punctuation(cls, text: str) -> str:
        """Removes punctuation characters, retaining alphanumeric tokens and spaces."""
        if not text:
            return ""
        return re.sub(r"[^\w\s]", "", text)

    @classmethod
    def clean_for_lexical(cls, text: str) -> str:
        """Prepares text for Winnowing lexical k-gram generation (case folded, alphanumeric only, no spaces)."""
        if not text:
            return ""
        folded = cls.case_folding(text)
        return re.sub(r"[^a-z0-9]", "", folded)

    @classmethod
    def tokenize_words(cls, text: str) -> List[str]:
        """Tokenizes text into individual word tokens (lowercased alphanumeric)."""
        if not text:
            return []
        folded = cls.case_folding(text)
        return re.findall(r"\b[a-z0-9\u00C0-\u017F\-]+\b", folded)

    @classmethod
    def is_citation_sentence(cls, sentence: str) -> bool:
        """Detects if sentence is primarily an academic citation, reference, or formula."""
        if not sentence:
            return False
        stripped = sentence.strip()
        # Direct bracket citation start: [1] or (Santoso, 2024)
        if stripped.startswith("[") and re.match(r"^\[\d+\]", stripped):
            return True
        if cls.CITATION_REGEX.search(sentence):
            # If citation takes up a significant portion of sentence or matches citation pattern
            tokens = cls.tokenize_words(sentence)
            if len(tokens) <= 6:
                return True
        return False

    @classmethod
    def segment_sentences(cls, original_text: str) -> List[SentenceSpan]:
        """Segments raw manuscript text into sentences with exact character offsets.
        
        Preserves offsets such that original_text[start_char:end_char] == text.
        """
        if not original_text or not original_text.strip():
            return []

        spans: List[SentenceSpan] = []
        n = len(original_text)
        current_start = 0

        # Pattern to locate potential sentence endings: . ! ? followed by space/newline or EOF
        # or double newlines (paragraphs)
        boundary_pattern = re.compile(r"([.!?]+)(?:\s+|\n+|$)|(\n\s*\n+)")

        last_pos = 0
        for match in boundary_pattern.finditer(original_text):
            delimiter_start = match.start()
            delimiter_end = match.end()

            # Check if this period is an abbreviation or decimal number
            is_valid_boundary = True
            matched_delim = match.group(1)

            if matched_delim and "." in matched_delim:
                # Preceding word check
                preceding_match = re.search(r"(\b[a-zA-Z\.]+)\s*$", original_text[last_pos:delimiter_start])
                if preceding_match:
                    preceding_word = preceding_match.group(1).lower().rstrip(".")
                    if preceding_word in cls.ABBREVIATIONS:
                        is_valid_boundary = False
                    # Single letter initial like 'A.' or 'B.'
                    elif len(preceding_word) == 1 and preceding_word.isalpha():
                        is_valid_boundary = False

                # Number like '3.14' check
                if delimiter_start > 0 and delimiter_end < n:
                    before_char = original_text[delimiter_start - 1]
                    after_char = original_text[delimiter_start + 1] if delimiter_start + 1 < n else ""
                    if before_char.isdigit() and after_char.isdigit():
                        is_valid_boundary = False

            if not is_valid_boundary:
                continue

            # Candidate sentence is from current_start to delimiter_start + len(delim or '')
            chunk_end = delimiter_start + (len(matched_delim) if matched_delim else 0)
            raw_chunk = original_text[current_start:chunk_end]

            # Adjust leading and trailing whitespaces while maintaining exact offsets
            trimmed_text, adj_start, adj_end = cls._trim_span(original_text, current_start, chunk_end)

            if trimmed_text:
                tokens = cls.tokenize_words(trimmed_text)
                is_cit = cls.is_citation_sentence(trimmed_text)
                spans.append(SentenceSpan(
                    index=len(spans),
                    text=trimmed_text,
                    start_char=adj_start,
                    end_char=adj_end,
                    word_count=len(tokens),
                    tokens=tokens,
                    clean_text=cls.normalize_whitespace(cls.case_folding(trimmed_text)),
                    is_citation=is_cit,
                ))

            current_start = delimiter_end
            last_pos = current_start

        # Trailing text after last delimiter
        if current_start < n:
            raw_chunk = original_text[current_start:n]
            trimmed_text, adj_start, adj_end = cls._trim_span(original_text, current_start, n)
            if trimmed_text:
                tokens = cls.tokenize_words(trimmed_text)
                is_cit = cls.is_citation_sentence(trimmed_text)
                spans.append(SentenceSpan(
                    index=len(spans),
                    text=trimmed_text,
                    start_char=adj_start,
                    end_char=adj_end,
                    word_count=len(tokens),
                    tokens=tokens,
                    clean_text=cls.normalize_whitespace(cls.case_folding(trimmed_text)),
                    is_citation=is_cit,
                ))

        return spans

    @staticmethod
    def _trim_span(source: str, start: int, end: int) -> Tuple[str, int, int]:
        """Trims leading and trailing whitespace from a substring while tracking exact start and end offsets."""
        sub = source[start:end]
        if not sub.strip():
            return "", start, start

        # Advance start over leading whitespace
        leading_ws = len(sub) - len(sub.lstrip())
        adj_start = start + leading_ws

        # Retract end over trailing whitespace
        trailing_ws = len(sub) - len(sub.rstrip())
        adj_end = end - trailing_ws

        trimmed = source[adj_start:adj_end]
        return trimmed, adj_start, adj_end

    @classmethod
    def extract_text_from_file(cls, file_path: str, mime_type: Optional[str] = None) -> str:
        """Extracts text content from PDF, DOCX, or plain text files."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""

        # 1. Plain text
        if ext in ("txt", "text", "md") or (mime_type and "text/plain" in mime_type):
            for encoding in ("utf-8", "latin-1", "cp1252"):
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        # 2. PDF extraction using pdfplumber
        if ext == "pdf" or (mime_type and "pdf" in mime_type):
            try:
                import pdfplumber
                text_parts = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                if text_parts:
                    return "\n\n".join(text_parts)
            except Exception:
                pass

        # 3. DOCX extraction using python-docx
        if ext in ("docx", "doc") or (mime_type and "wordprocessingml" in mime_type):
            try:
                import docx
                doc = docx.Document(file_path)
                paragraphs = [p.text for p in doc.paragraphs if p.text]
                if paragraphs:
                    return "\n\n".join(paragraphs)
            except Exception:
                pass

        # Fallback binary text read
        try:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()
                return raw_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            return f"Error reading file content: {str(e)}"
