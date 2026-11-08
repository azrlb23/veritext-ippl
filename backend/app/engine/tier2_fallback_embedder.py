from __future__ import annotations

import hashlib
import math
from contextlib import nullcontext
from typing import Any

from app.engine.preprocessor import TextPreprocessor

PREFIXES = ("meng", "meny", "men", "mem", "me", "peng", "peny", "pen", "pem", "pe", "di", "ter", "ber", "per", "se")
SUFFIXES = ("kan", "an", "nya", "lah", "kah", "i")
STOPWORDS = {
    "yang", "di", "dan", "dari", "ini", "itu", "untuk", "pada", "adalah", "dengan", "ke", "oleh", "dalam",
    "sebagai", "akan", "juga", "atau", "tidak", "dapat", "secara", "ia", "mereka", "kita", "kamu", "saya", "telah", "bisa", "hal",
}
SYNONYM_CONCEPTS = {
    "cerdas": "concept:smart", "pintar": "concept:smart", "pandai": "concept:smart", "intelektual": "concept:smart",
    "manfaat": "concept:use", "memanfaatkan": "concept:use", "pemanfaatan": "concept:use", "guna": "concept:use",
    "menggunakan": "concept:use", "penggunaan": "concept:use", "kegunaan": "concept:use", "pakai": "concept:use",
    "memakai": "concept:use", "terap": "concept:use", "menerapkan": "concept:use", "penerapan": "concept:use",
    "padu": "concept:combine", "perpaduan": "concept:combine", "memadukan": "concept:combine", "kombinasi": "concept:combine",
    "mengombinasikan": "concept:combine", "gabung": "concept:combine", "penggabungan": "concept:combine", "integrasi": "concept:combine",
    "mengintegrasikan": "concept:combine", "deteksi": "concept:detect", "mendeteksi": "concept:detect", "pendeteksian": "concept:detect",
    "terdeteksi": "concept:detect", "identifikasi": "concept:detect", "mengidentifikasi": "concept:detect",
    "pengidentifikasian": "concept:detect", "temu": "concept:detect", "menemukan": "concept:detect", "plagiat": "concept:plagiarism",
    "plagiarisme": "concept:plagiarism", "jiplak": "concept:plagiarism", "penjiplakan": "concept:plagiarism", "mirip": "concept:similarity",
    "kemiripan": "concept:similarity", "sama": "concept:similarity", "kesamaan": "concept:similarity", "serupa": "concept:similarity",
    "algoritma": "concept:algorithm", "metode": "concept:algorithm", "metodologi": "concept:algorithm", "pendekatan": "concept:algorithm",
    "teknik": "concept:algorithm", "naskah": "concept:text", "dokumen": "concept:text", "teks": "concept:text", "tulisan": "concept:text",
    "karya": "concept:text", "artikel": "concept:text", "paper": "concept:text", "representasi": "concept:vector",
    "vektor": "concept:vector", "embedding": "concept:vector", "leksikal": "concept:lexical", "kata": "concept:lexical",
    "semantik": "concept:semantic", "makna": "concept:semantic", "konteks": "concept:semantic", "deep": "concept:deeplearning",
    "mendalam": "concept:deeplearning", "learning": "concept:deeplearning", "pembelajaran": "concept:deeplearning",
    "basis": "concept:base", "berbasis": "concept:base", "dasar": "concept:base", "berdasarkan": "concept:base",
    "dan": "concept:and", "serta": "concept:and", "beserta": "concept:and",
}


def get_inference_context():
    try:
        import torch
        if hasattr(torch, "inference_mode"):
            return torch.inference_mode()
        if hasattr(torch, "no_grad"):
            return torch.no_grad()
    except ImportError:
        pass
    return nullcontext()


def get_stem(word: str) -> str:
    w = word.lower().strip()
    if len(w) <= 4:
        return w
    for p in PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 3:
            w = w[len(p):]
            break
    for s in SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= 3:
            w = w[:-len(s)]
            break
    return w


def cosine_similarity(u: Any, v: Any) -> float:
    if u is None or v is None:
        return 0.0
    try:
        if len(u) == 0 or len(v) == 0 or len(u) != len(v):
            return 0.0
    except TypeError:
        return 0.0
    dot, norm_u_sq, norm_v_sq = 0.0, 0.0, 0.0
    for a, b in zip(u, v):
        dot += float(a) * float(b)
        norm_u_sq += float(a) * float(a)
        norm_v_sq += float(b) * float(b)
    if norm_u_sq <= 1e-12 or norm_v_sq <= 1e-12:
        return 0.0
    sim = dot / (math.sqrt(norm_u_sq) * math.sqrt(norm_v_sq))
    return max(-1.0, min(1.0, sim))


def embed_sentence_dense(text: str, dimension: int = 384) -> list[float]:
    vec = [0.0] * dimension
    if not text or not text.strip():
        return vec
    tokens = TextPreprocessor.tokenize_words(text)
    if not tokens:
        return vec
    features: list[tuple[str, float]] = []
    for i, token in enumerate(tokens):
        stem = get_stem(token)
        if token in SYNONYM_CONCEPTS:
            features.append((SYNONYM_CONCEPTS[token], 4.0))
        elif stem in SYNONYM_CONCEPTS:
            features.append((SYNONYM_CONCEPTS[stem], 3.5))
        weight = 0.5 if token in STOPWORDS else 2.0
        features.append((f"tok:{token}", weight))
        features.append((f"stem:{stem}", weight * 1.5))
        if len(token) >= 3 and token not in STOPWORDS:
            for c_i in range(len(token) - 2):
                features.append((f"char3:{token[c_i:c_i+3]}", 0.6))
        if i < len(tokens) - 1:
            features.append((f"bi:{stem}_{get_stem(tokens[i + 1])}", 1.2))

    for feat_name, weight in features:
        h = hashlib.sha256(feat_name.encode("utf-8")).digest()
        for offset in range(0, 16, 4):
            idx = int.from_bytes(h[offset : offset + 2], "big") % dimension
            sign = 1.0 if (h[offset + 2] % 2 == 0) else -1.0
            vec[idx] += sign * (h[offset + 3] / 255.0) * weight

    norm_sq = sum(x * x for x in vec)
    if norm_sq > 0:
        inv_norm = 1.0 / math.sqrt(norm_sq)
        vec = [x * inv_norm for x in vec]
    return vec
