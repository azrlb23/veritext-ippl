from __future__ import annotations

HISTORY_TURNS = 6
HISTORY_CHARS = 600

_TASK_INSTRUCTIONS: dict[str, str] = {
    "QA_DOCUMENT": (
        "Anda adalah asisten analis naskah akademik. Jawab pertanyaan, ringkas bagian, "
        "atau klarifikasi isi berdasarkan kutipan dokumen yang dilampirkan. "
        "Jangan mengarang sumber dan jangan melenceng ke obrolan umum."
    ),
    "PARAPHRASE_TASK": (
        "Anda adalah spesialis parafrase akademik Bahasa Indonesia. Ubah teks pengguna menjadi "
        "2-3 variasi kalimat/paragraf yang orisinal, baku, dan mempertahankan makna ilmiah "
        "tanpa menambah informasi fiktif."
    ),
    "STYLE_REVIEW": (
        "Anda adalah penyunting gaya dan struktur akademik. Evaluasi kejelasan, koherensi, "
        "dan pola penulisan mirip AI, lalu berikan saran revisi konkret."
    ),
}
INSTRUCTION = _TASK_INSTRUCTIONS["QA_DOCUMENT"]


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
