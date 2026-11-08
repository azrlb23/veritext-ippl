from __future__ import annotations

from app.engine.preprocessor import TextPreprocessor


def polynomial_hash(substring: str, base: int = 257, mod: int = 1_000_000_007) -> int:
    """Computes Rabin-Karp polynomial hash directly: H = sum(c_i * base^(k-1-i)) % mod."""
    h = 0
    for char in substring:
        h = (h * base + ord(char)) % mod
    return (h % mod + mod) % mod


def compute_kgram_hashes(
    text: str, k: int, base: int, mod: int, base_k_minus_1: int
) -> list[tuple[int, int]]:
    """Generates k-grams and calculates their polynomial rolling hashes."""
    clean = TextPreprocessor.clean_for_lexical(text)
    n = len(clean)
    if n < k:
        return [(polynomial_hash(clean, base, mod), 0)] if n > 0 else []

    first_kgram = clean[:k]
    current_hash = polynomial_hash(first_kgram, base, mod)
    hashes = [(current_hash, 0)]

    for i in range(1, n - k + 1):
        prev_char, new_char = ord(clean[i - 1]), ord(clean[i + k - 1])
        current_hash = (
            (current_hash - prev_char * base_k_minus_1) * base + new_char
        ) % mod
        current_hash = (current_hash % mod + mod) % mod
        hashes.append((current_hash, i))

    return hashes


def winnow_hashes(hashes: list[tuple[int, int]], w: int) -> list[tuple[int, int]]:
    """Applies sliding window of size w to select minimum hashes with rightmost tie-breaking."""
    n = len(hashes)
    if n == 0:
        return []
    if n <= w:
        min_tuple = hashes[0]
        for h_val, pos in hashes:
            if h_val <= min_tuple[0]:
                min_tuple = (h_val, pos)
        return [min_tuple]

    fingerprints: list[tuple[int, int]] = []
    last_pos = None
    for i in range(n - w + 1):
        window = hashes[i : i + w]
        min_tuple = window[0]
        for h_val, pos in window:
            if h_val <= min_tuple[0]:
                min_tuple = (h_val, pos)
        if last_pos != min_tuple[1]:
            fingerprints.append(min_tuple)
            last_pos = min_tuple[1]

    return fingerprints
