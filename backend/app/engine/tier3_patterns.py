import re

from app.engine.evasion_guard import detect_evasion_signals

AI_TRANSITION_MARKERS: list[str] = [
    r"\bdalam era (?:digital|modern|globalisasi) ini\b",
    r"\bpenting untuk (?:dicatat|diingat|diperhatikan)\b",
    r"\bsecara keseluruhan dapat disimpulkan bahwa\b",
    r"\bmemainkan peran (?:penting|krusial|vital)\b",
    r"\bkesimpulannya,? dapat dikatakan bahwa\b",
    r"\bberdasarkan penjelasan di atas\b",
    r"\bsebagaimana telah disebutkan sebelumnya\b",
    r"\bhal ini menunjukkan bahwa\b",
    r"\bmoreover, it is crucial to note that\b",
    r"\bin summary, it can be concluded that\b",
    r"\bplays a pivotal role\b",
    r"\btidak hanya\b.+\btetapi juga\b",
    r"\bsecara signifikan meningkatkan\b",
    r"\bmenjadi fondasi (?:utama|penting|krusial)\b",
    r"\bseiring dengan pesatnya perkembangan\b",
    r"\bbukan sekadar\b.+\bmelainkan\b",
]

TRANSITION_REGEX = re.compile("|".join(AI_TRANSITION_MARKERS), re.IGNORECASE)
EM_DASH_PATTERN = re.compile(r"\u2014|(?<=\w)\s+--\s+(?=[A-Za-zÀ-ÿ])")
RULE_OF_THREE_PATTERN = re.compile(
    r"\b[a-zA-ZÀ-ÿ]{4,},\s+[a-zA-ZÀ-ÿ]{4,},\s+(?:dan|serta|maupun|and)\s+[a-zA-ZÀ-ÿ]{4,}\b",
    re.IGNORECASE,
)

EXCLUDED_LABEL_PREFIXES: set[str] = {
    "gambar", "tabel", "bab", "lampiran", "sumber", "catatan", "contoh", "rumus",
    "persamaan", "figure", "table", "source", "note", "chapter", "appendix", "http", "https",
}

LABEL_COLON_PATTERN = re.compile(
    r"^\s*(?:(?:[-*\u2022\u2013\u2014]|\d+[.)]|[a-zA-Z][.)])\s+)?"
    r"(?P<label>[^.?!;:\n]{2,48}):\s+(?P<body>.+)$"
)

CHATBOT_ARTIFACT_RE = re.compile(
    r"\*\*[^*\n]{2,60}\*\*|^\s*#{2,4}\s+\S|\b(?:"
    r"tentu,?\s+berikut\s+adalah|semoga\s+membantu|sebagai\s+model\s+bahasa|"
    r"as\s+an\s+ai\s+language\s+model|certainly!\s+here\s+is|i\s+hope\s+this\s+helps"
    r")\b",
    re.IGNORECASE,
)
INLINE_CITATION_RE = re.compile(r"\(\s*[A-Z][^)]*(?:19|20)\d{2}[^)]*\)|\[\d+\]")
VAGUE_ATTRIBUTION_RE = re.compile(
    r"\b(?:para\s+ahli\s+(?:berpendapat|menyatakan|menilai)|"
    r"beberapa\s+pengamat\s+(?:mencatat|menilai)|"
    r"banyak\s+pihak\s+(?:berpendapat|meyakini)|"
    r"experts\s+(?:argue|note|highlight)|some\s+critics\s+(?:argue|claim))\b",
    re.IGNORECASE,
)
AI_BUZZWORDS: frozenset[str] = frozenset({
    "delve", "tapestry", "pivotal", "testament", "realm", "showcase", "meticulously",
    "groundbreaking", "landscape", "lanskap", "katalisator", "transformatif",
    "komprehensif", "holistik", "sinergi", "signifikansi", "paradigma",
    "revolusioner", "berkelanjutan", "optimalisasi",
})
PUFFERY_RE = re.compile(
    r"\b(?:meninggalkan\s+warisan\s+(?:mendalam|abadi)|membentuk\s+ulang\s+masa\s+depan|"
    r"tonggak\s+bersejarah|pergeseran\s+paradigma\s+yang\s+mendalam|"
    r"stands\s+as\s+a\s+testament|profound\s+impact\s+on\s+the\s+landscape|"
    r"reshaping\s+the\s+future\s+of)\b",
    re.IGNORECASE,
)
_BUZZ_WORD_RE = re.compile(r"\b[a-z]+\b")


def has_label_colon_pattern(text: str) -> bool:
    """Detects AI-style short label + colon + long explanation sentence structure."""
    match = LABEL_COLON_PATTERN.match(text.strip())
    if not match:
        return False
    label = match.group("label").strip()
    words = label.split()
    if not (1 <= len(words) <= 5):
        return False
    first_word = re.sub(r"^[^\w]+|[^\w]+$", "", words[0].lower())
    if not first_word or first_word in EXCLUDED_LABEL_PREFIXES:
        return False
    if first_word.startswith(("http", "https", "ftp")) or "://" in label:
        return False
    return len(match.group("body").strip().split()) >= 8


def detect_sentence_ai_signals(text: str) -> list[tuple[str, float, str]]:
    """Returns detected AI structural/lexical signals as (signal_key, score, reason)."""
    signals: list[tuple[str, float, str]] = []
    signals.extend(detect_evasion_signals(text))
    if CHATBOT_ARTIFACT_RE.search(text):
        signals.append(
            ("chatbot_artifact", 0.95, "Terdeteksi artefak format chatbot/Markdown (WP:AISIGNS)")
        )
    if EM_DASH_PATTERN.search(text):
        signals.append(
            ("em_dash", 0.80, "Penggunaan tanda pisah em-dash (—) khas pola penulisan AI")
        )
    if has_label_colon_pattern(text):
        signals.append(
            ("label_colon", 0.78, "Pola label singkat diikuti titik dua dan penjelasan panjang khas AI")
        )
    if TRANSITION_REGEX.search(text):
        signals.append(("transition", 0.72, "Pola transisi generatif AI terdeteksi"))
    if RULE_OF_THREE_PATTERN.search(text):
        signals.append(
            ("triad", 0.68, "Pola enumerasi tiga frasa sejajar khas gaya penulisan AI")
        )
    if VAGUE_ATTRIBUTION_RE.search(text) and not INLINE_CITATION_RE.search(text):
        signals.append(
            ("vague_attribution", 0.72, "Atribusi kabur tanpa sitasi rujukan yang jelas (WP:AISIGNS)")
        )
    if len(set(_BUZZ_WORD_RE.findall(text.lower())) & AI_BUZZWORDS) >= 3:
        signals.append(
            ("ai_vocab_density", 0.76, "Kepadatan kosakata klise AI berlebih dalam satu kalimat (WP:AISIGNS)")
        )
    if PUFFERY_RE.search(text):
        signals.append(
            ("puffery", 0.74, "Pola penekanan signifikansi hiperbolis khas tulisan AI (WP:AISIGNS)")
        )
    return signals
