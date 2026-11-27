from __future__ import annotations

from typing import Any

from app.services.local_similarity_check import measure_paraphrase_similarity


def build_paraphrase_prompt(original_text: str, mode: str) -> str:
    """Menyusun prompt parafrase akademik dengan aturan anti-WP:AISIGNS dan penguncian bahasa."""
    return (
        f"Parafrasekan teks berikut ({mode}) menjadi 3 variasi gaya akademik.\n"
        "WAJIB pertahankan bahasa yang sama persis dengan teks asli "
        "(jika teks berbahasa Indonesia, seluruh variasi WAJIB berbahasa Indonesia akademik baku; "
        "jangan diterjemahkan ke bahasa lain).\n"
        "ATURAN GAYA ANTI-DETEKSI AI (WP:AISIGNS):\n"
        "- Dilarang memakai tanda pisah em-dash (—) atau tanda hubung ganda (--).\n"
        "- Dilarang memakai pola 'Label singkat: penjelasan panjang'.\n"
        "- Dilarang memakai klise AI seperti 'dalam era digital ini', 'penting untuk dicatat', "
        "'memainkan peran vital', atau 'secara keseluruhan dapat disimpulkan'.\n"
        "- Dilarang memakai pola enumerasi tiga frasa sejajar (rule-of-three) atau buzzword berlebihan.\n"
        "- Dilarang menyertakan format Markdown (**...**, ##) atau kalimat pengantar chatbot.\n"
        f"Teks asli:\n{original_text}\n"
        "KEMBALIKAN HANYA JSON ARRAY MURNI (diawali `[` dan diakhiri `]`) tanpa teks pengantar atau markdown:\n"
        '[{"option_id": 1, "style": "Formal", "text": "...", "predicted_score": 8.2}, ...]'
    )


def score_paraphrase_variations(
    original_text: str, variations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Menghitung ulang predicted_score tiap variasi menggunakan kemiripan leksikal/kata lokal."""
    scored: list[dict[str, Any]] = []
    for item in variations:
        v = dict(item)
        sim = measure_paraphrase_similarity(original_text, str(v.get("text") or ""))
        v["predicted_score"] = round(
            max(float(sim["lexical_overlap_pct"]), float(sim["word_overlap_pct"])), 1
        )
        scored.append(v)
    return scored
