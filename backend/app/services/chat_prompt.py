from __future__ import annotations

HISTORY_TURNS = 6
HISTORY_CHARS = 600

_DOMAIN_SAFEGUARD = (
    "ATURAN DOMAIN KETAT: Anda HANYA melayani pertanyaan seputar isi naskah, "
    "parafrase akademik, dan penyuntingan gaya penulisan. Jika pengguna bertanya "
    "di luar topik akademik atau naskah (seperti hiburan, resep, kode aplikasi umum, "
    "atau obrolan santai), tolak dengan sopan dan arahkan kembali ke naskah."
)
_PARAPHRASE_KEYS = (
    "parafrase", "tulis ulang", "ubah kalimat", "kalimat lain", "perbaiki kalimat", "susun ulang",
)
_STYLE_KEYS = ("pola ai", "gaya bahasa", "tata bahasa", "koherensi", "burstiness", "terlalu kaku")

_TASK_INSTRUCTIONS: dict[str, str] = {
    "QA_DOCUMENT": (
        "Anda adalah asisten analis naskah akademik. Jawab pertanyaan, ringkas bagian, "
        "atau klarifikasi isi berdasarkan kutipan dokumen yang dilampirkan. "
        f"Jangan mengarang sumber. {_DOMAIN_SAFEGUARD}"
    ),
    "PARAPHRASE_TASK": (
        "Anda adalah spesialis parafrase akademik Bahasa Indonesia. Ubah teks pengguna menjadi "
        "2-3 variasi kalimat/paragraf yang orisinal, baku, dan mempertahankan makna ilmiah "
        f"tanpa menambah informasi fiktif. {_DOMAIN_SAFEGUARD}"
    ),
    "STYLE_REVIEW": (
        "Anda adalah penyunting gaya dan struktur akademik. Evaluasi kejelasan, koherensi, "
        f"dan pola penulisan mirip AI, lalu berikan saran revisi konkret. {_DOMAIN_SAFEGUARD}"
    ),
}
INSTRUCTION = _TASK_INSTRUCTIONS["QA_DOCUMENT"]


def classify_task_and_engine(question: str, has_docs: bool = False) -> tuple[str, str]:
    """Menentukan task_mode dan preferred_engine secara otomatis dari pertanyaan pengguna."""
    _ = has_docs
    q = (question or "").lower()
    if any(key in q for key in _PARAPHRASE_KEYS):
        return ("PARAPHRASE_TASK", "ollama")
    if any(key in q for key in _STYLE_KEYS):
        return ("STYLE_REVIEW", "ollama")
    return ("QA_DOCUMENT", "auto")


def build_prompt(
    question: str,
    context: str,
    history: list[tuple[str, str]],
    task_mode: str = "QA_DOCUMENT",
) -> str:
    """Menyusun prompt: instruksi task_mode, kutipan naskah relevan, riwayat singkat, lalu pertanyaan."""
    instruction = _TASK_INSTRUCTIONS.get((task_mode or "").strip().upper(), _TASK_INSTRUCTIONS["QA_DOCUMENT"])
    parts = [instruction]
    if context:
        parts.append("Kutipan naskah yang relevan:\n" + context)
    recent = history[-HISTORY_TURNS:]
    if recent:
        lines = [f"{'Pengguna' if role == 'USER' else 'Asisten'}: {text[:HISTORY_CHARS]}" for role, text in recent]
        parts.append("Percakapan sebelumnya:\n" + "\n".join(lines))
    parts.append("Pertanyaan pengguna:\n" + question)
    return "\n\n".join(parts)
