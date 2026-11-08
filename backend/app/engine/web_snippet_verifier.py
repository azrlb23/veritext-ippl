from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticEngine

logger = logging.getLogger(__name__)


@dataclass
class WebMatchResult:
    """Hasil kecocokan kalimat naskah dengan sumber web publik yang terverifikasi."""

    sentence_index: int
    similarity: float
    source_url: str
    source_title: str
    matched_snippet: str
    tier: str = "T1"


def is_meaningful_sentence(s: SentenceSpan) -> bool:
    if s.is_citation or s.word_count < 6 or len(s.text.strip()) < 25:
        return False
    pat = r"^(bab\s+\d+|daftar\s+pustaka|lampiran|pendahuluan|kesimpulan|latar\s+belakang|rumusan\s+masalah|tujuan\s+penelitian|metodologi\s+penelitian)"
    return not bool(re.match(pat, s.text.strip(), re.IGNORECASE))


def verify_snippet_cross_check(
    sentence_text: str, snippet: str, lexical_engine: WinnowingLexicalEngine, semantic_engine: SemanticEngine
) -> tuple[float, float, bool, str]:
    if not snippet or not sentence_text:
        return 0.0, 0.0, False, ""
    tokens_s, tokens_snip = set(TextPreprocessor.tokenize_words(sentence_text)), set(TextPreprocessor.tokenize_words(snippet))
    if not tokens_s or not tokens_snip:
        lexical_sim = 0.0
    else:
        inter = tokens_s.intersection(tokens_snip)
        lexical_sim = max(len(inter) / len(tokens_s), len(inter) / len(tokens_s.union(tokens_snip)))
    try:
        fps_s = {h for h, _ in lexical_engine.extract_fingerprints(sentence_text)}
        fps_snip = {h for h, _ in lexical_engine.extract_fingerprints(snippet)}
        if fps_s and fps_snip:
            lexical_sim = max(lexical_sim, len(fps_s.intersection(fps_snip)) / max(1, len(fps_s)))
    except Exception as err:  # noqa: BLE001
        logger.debug("Lexical fingerprint match error: %s", err)
    try:
        emb_s, emb_snip = semantic_engine.embed_sentence(sentence_text), semantic_engine.embed_sentence(snippet)
        semantic_sim = max(0.0, min(1.0, float(semantic_engine.cosine_similarity(emb_s, emb_snip))))
    except Exception:  # noqa: BLE001
        semantic_sim = 0.0
    if lexical_sim >= 0.60:
        return lexical_sim, semantic_sim, True, "T1"
    if semantic_sim >= 0.65 or (lexical_sim >= 0.30 and semantic_sim >= 0.40):
        return lexical_sim, semantic_sim, True, "T2"
    return lexical_sim, semantic_sim, False, ""


def extract_matches_from_response(cand: dict[str, Any], batch_sentences: list[SentenceSpan]) -> list[dict[str, Any]]:
    parts = cand.get("content", {}).get("parts", [])
    raw_text = parts[0].get("text", "") if parts else ""
    grounding = cand.get("groundingMetadata", {})
    chunks = grounding.get("groundingChunks", [])
    chunk_info = [{"url": c.get("web", {}).get("uri", ""), "title": c.get("web", {}).get("title", "")} for c in chunks]
    items: list[dict[str, Any]] = []

    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join([line for line in cleaned.splitlines() if not line.strip().startswith("```")]).strip()
    cleaned_json = re.sub(r",\s*([\]}])", r"\1", cleaned)
    try:
        arr_m = re.search(r"\[\s*\{.*?\}\s*\]", cleaned_json, re.DOTALL)
        if arr_m:
            items = json.loads(arr_m.group(0))
        elif cleaned_json.startswith("[") and cleaned_json.endswith("]"):
            items = json.loads(cleaned_json)
        else:
            obj_m = re.search(r"\{[^{}]*\"sentence_index\"[^{}]*\}", cleaned_json, re.DOTALL)
            if obj_m:
                items = [json.loads(obj_m.group(0))]
    except Exception as err:  # noqa: BLE001
        logger.debug("JSON text match failed: %s", err)
    if not isinstance(items, list):
        items = []

    if not items and chunks:
        for sup in grounding.get("groundingSupports", []):
            seg = sup.get("segment", {}).get("text", "").strip()
            for c_idx in sup.get("groundingChunkIndices", []):
                if 0 <= c_idx < len(chunk_info) and chunk_info[c_idx]["url"] and seg:
                    c_meta = chunk_info[c_idx]
                    t_seg = set(TextPreprocessor.tokenize_words(seg))
                    best_s, best_ov = None, 0.0
                    for s_span in batch_sentences:
                        t_span = set(TextPreprocessor.tokenize_words(s_span.text))
                        if t_span and t_seg:
                            ov = len(t_span.intersection(t_seg)) / len(t_span)
                            if ov > best_ov and ov >= 0.40:
                                best_ov, best_s = ov, s_span
                    if best_s:
                        items.append({"sentence_index": best_s.index, "source_title": c_meta["title"] or "Sumber Web Publik", "source_url": c_meta["url"], "matched_snippet": seg})

    first_url = chunk_info[0]["url"] if chunk_info and chunk_info[0]["url"] else ""
    first_title = chunk_info[0]["title"] if chunk_info and chunk_info[0]["title"] else ""
    valid: list[dict[str, Any]] = []
    for it in items:
        raw_idx = it.get("sentence_index")
        m = re.search(r"\d+", str(raw_idx)) if raw_idx is not None else None
        if not m:
            continue
        valid.append({
            "sentence_index": int(m.group(0)),
            "source_title": str(it.get("source_title") or "").strip() or first_title or "Sumber Web Publik",
            "source_url": str(it.get("source_url") or "").strip() or first_url,
            "matched_snippet": str(it.get("matched_snippet") or "").strip(),
        })
    return valid
