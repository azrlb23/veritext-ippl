from __future__ import annotations

HISTORY_TURNS = 6
HISTORY_CHARS = 600

INSTRUCTION = (
    "Anda adalah asisten penulisan untuk naskah berbahasa Indonesia. Bantu pengguna memperbaiki gaya, struktur, "
    "dan orisinalitas tulisannya. Jangan menuliskan naskah penuh menggantikan pengguna dan jangan mengarang sumber. "
    "Gunakan kutipan naskah di bawah hanya sebagai konteks; jika pertanyaan tidak berkaitan, jawab secara umum."
)


def build_prompt(question: str, context: str, history: list[tuple[str, str]]) -> str:
    """Menyusun prompt: instruksi, kutipan naskah relevan, riwayat singkat, lalu pertanyaan."""
    parts = [INSTRUCTION]
    if context:
        parts.append("Kutipan naskah yang relevan:\n" + context)
    recent = history[-HISTORY_TURNS:]
    if recent:
        lines = [f"{'Pengguna' if role == 'USER' else 'Asisten'}: {text[:HISTORY_CHARS]}" for role, text in recent]
        parts.append("Percakapan sebelumnya:\n" + "\n".join(lines))
    parts.append("Pertanyaan pengguna:\n" + question)
    return "\n\n".join(parts)
