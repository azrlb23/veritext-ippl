from __future__ import annotations

import re

from fastapi import HTTPException

GUARDRAIL_DETAIL = (
    "CHAT_001: Pelanggaran Guardrail - "
    "Permintaan ini di luar ruang lingkup analisis naskah akademik VeriText AI."
)

JOKI_MANIPULATION_PHRASES: tuple[str, ...] = (
    "tuliskan skripsi penuh",
    "buatkan skripsi penuh",
    "buatkan bab 1 sampai",
    "palsukan data",
    "manipulasi data penelitian",
    "bikin daftar pustaka palsu",
    "buatkan makalah",
    "buatkan laporan lengkap",
    "kerjakan tugas",
    "jawabkan soal",
)

PROMPT_INJECTION_OFFTOPIC_PHRASES: tuple[str, ...] = (
    "ignore previous instructions",
    "abaikan instruksi",
    "system prompt",
    "reveal your prompt",
    "resep masakan",
    "ramalan zodiak",
    "situs judi",
    "slot gacor",
)

_PROFANITY_RE = re.compile(
    r"\b(anjing|bangsat|kontol|memek|ngentot|jancok|tolol|goblok|goblog|"
    r"asu|bajingan|keparat|fuck|shit|bitch|asshole|dick)\b",
    re.IGNORECASE,
)

_CODING_CREATE_RE = re.compile(
    r"\b(buatkan|buatin|tuliskan|bikinin)\s+"
    r"(kode|script|skrip|program|aplikasi|website|bot|malware)\b",
    re.IGNORECASE,
)

_HACKING_RE = re.compile(
    r"\b(sql\s+injection|exploit|jailbreak|bypass\s+auth|ddos|hack\s+akun)\b",
    re.IGNORECASE,
)

_PHRASE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
    for phrase in (*JOKI_MANIPULATION_PHRASES, *PROMPT_INJECTION_OFFTOPIC_PHRASES)
)

_BLOCKED_REGEXES: tuple[re.Pattern[str], ...] = (
    _PROFANITY_RE,
    _CODING_CREATE_RE,
    _HACKING_RE,
    *_PHRASE_PATTERNS,
)


def enforce_academic_guardrail(prompt: str) -> None:
    """Validate that a user prompt stays within VeriText AI academic scope."""
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail=GUARDRAIL_DETAIL)

    normalized = " ".join(prompt.split())
    if any(pattern.search(normalized) for pattern in _BLOCKED_REGEXES):
        raise HTTPException(status_code=400, detail=GUARDRAIL_DETAIL)
