from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from app.engine.tier3_patterns import detect_sentence_ai_signals
from app.models.audit import AuditReport, AuditSentence
from app.services.local_similarity_check import measure_paraphrase_similarity
from app.services.paraphrase_scope import resolve_paraphrase_scope_sentences

_TOO_SIMILAR_DETAIL = "PARAPHRASE_TOO_SIMILAR: Teks pengganti masih terlalu mirip dengan naskah asli. Silakan pilih variasi lain."


def _active_text(sentence: AuditSentence) -> str:
    return (sentence.current_text or "") if getattr(sentence, "is_modified", False) else (sentence.current_text or sentence.sentence_text or "")


def _recompute_tier_score(
    old_score: float, target_match: str, scope_sentences: list[AuditSentence],
    scope_sims: dict[Any, float], scope_matches: dict[Any, str | None],
    residual: float, all_sentences: list[AuditSentence],
) -> float:
    scope_ids = {s.id for s in scope_sentences}
    scope_total = sum(scope_sims[s.id] for s in scope_sentences if scope_matches[s.id] == target_match)
    if scope_total <= 0.0 or old_score <= 0.0:
        return round(old_score, 2)
    other_total = sum(
        float(s.similarity_score or 0.0) for s in all_sentences
        if s.id not in scope_ids and s.match_type == target_match
    )
    prev_total = other_total + scope_total
    if prev_total <= 0.0:
        return round(old_score, 2)
    clamped = min(float(residual), scope_total)
    new_val = old_score * max(0.0, prev_total - scope_total + clamped) / prev_total
    return round(min(100.0, max(0.0, new_val)), 2)


def _update_heatmap_annotations(
    annotations: list[Any], sentence_id: Any, scope_ids: set[str],
    old_start: int, selected_text: str, delta: int, new_sim: float, clear_ai: bool,
) -> list[dict[str, Any]]:
    updated: list[dict[str, Any]] = []
    sid_str = str(sentence_id)
    for raw in annotations:
        if not isinstance(raw, dict):
            updated.append(raw)
            continue
        item = dict(raw)
        item_sid = str(item.get("sentence_id")) if item.get("sentence_id") else None
        item_start = int(item.get("start", -1))
        is_primary = (item_sid == sid_str) or (item_sid is None and item_start == old_start)
        is_absorbed = item_sid is not None and item_sid in scope_ids and not is_primary
        if is_primary or is_absorbed:
            item["color"] = "RESOLVED_GREEN"
            item["text_snippet"] = selected_text if is_primary else ""
            item["similarity"] = new_sim if is_primary else 0.0
            if clear_ai:
                for key in ("ai_flag", "ai_reason", "ai_score", "reason"):
                    item.pop(key, None)
            if is_primary and delta != 0 and "end" in item:
                item["end"] = int(item["end"]) + delta
        elif delta != 0 and item_start > old_start:
            item["start"] = item_start + delta
            if "end" in item:
                item["end"] = int(item["end"]) + delta
        updated.append(item)
    return updated


def apply_paraphrase_update(
    sentence: AuditSentence, selected_text: str, all_sentences: list[AuditSentence],
    report: AuditReport | None = None, mode: str = "SENTENCE",
) -> dict[str, Any]:
    ordered = sorted(all_sentences, key=lambda s: int(getattr(s, "sentence_index", 0) or 0))
    scope_sentences = resolve_paraphrase_scope_sentences(ordered, sentence, mode)
    if sentence not in scope_sentences:
        scope_sentences = [sentence]

    old_scope_text = " ".join(t for s in scope_sentences if (t := _active_text(s).strip())).strip() or _active_text(sentence)
    old_match, old_sim = sentence.match_type, float(sentence.similarity_score or 0.0)
    sim = measure_paraphrase_similarity(old_scope_text, selected_text)
    new_sim = round(min(100.0, max(0.0, max(sim["lexical_overlap_pct"], sim["word_overlap_pct"]))), 2)

    if selected_text.strip().lower() == old_scope_text.strip().lower() or (
        old_match in ("RED", "ORANGE") and new_sim >= 75.0
    ):
        raise HTTPException(status_code=400, detail=_TOO_SIMILAR_DETAIL)

    signals = detect_sentence_ai_signals(selected_text)
    if old_match == "YELLOW":
        new_sim = round(0.0 if not signals else min(old_sim, max(sc for _, sc, _ in signals) * 100.0), 2)

    scope_sims = {s.id: float(s.similarity_score or 0.0) for s in scope_sentences}
    scope_matches = {s.id: s.match_type for s in scope_sentences}
    old_start = int(getattr(sentence, "start_char", 0) or 0)
    last_idx = getattr(scope_sentences[-1], "sentence_index", None)
    delta = len(selected_text) - len(old_scope_text)

    sentence.current_text, sentence.match_type, sentence.is_modified = selected_text, "RESOLVED_GREEN", True
    sentence.similarity_score = new_sim
    sentence.lexical_similarity = sentence.semantic_similarity = round(new_sim / 100.0, 4)
    if delta != 0 and hasattr(sentence, "end_char") and sentence.end_char is not None:
        sentence.end_char = old_start + len(selected_text)

    scope_ids = {s.id for s in scope_sentences}
    for other in scope_sentences:
        if other.id != sentence.id:
            other.current_text, other.is_modified, other.match_type, other.similarity_score = "", True, "RESOLVED_GREEN", 0.0

    if delta != 0:
        for s in all_sentences:
            if s.id in scope_ids:
                continue
            s_idx = getattr(s, "sentence_index", None)
            if (s_idx > last_idx) if (last_idx is not None and s_idx is not None) else ((s.start_char or 0) > old_start):
                s.start_char, s.end_char = int(s.start_char or 0) + delta, int(s.end_char or 0) + delta

    if report is not None and any(getattr(report, c, None) is not None for c in ("score_lexical", "score_semantic", "score_stylometric")):
        new_lex = _recompute_tier_score(float(report.score_lexical or 0.0), "RED", scope_sentences, scope_sims, scope_matches, new_sim if old_match == "RED" else 0.0, all_sentences)
        new_sem = _recompute_tier_score(float(report.score_semantic or 0.0), "ORANGE", scope_sentences, scope_sims, scope_matches, new_sim if old_match == "ORANGE" else 0.0, all_sentences)
        new_stylo = _recompute_tier_score(float(report.score_stylometric or 0.0), "YELLOW", scope_sentences, scope_sims, scope_matches, new_sim if old_match == "YELLOW" else 0.0, all_sentences)
        report.score_lexical, report.score_semantic, report.score_stylometric = new_lex, new_sem, new_stylo
        new_comp = round(min(100.0, max(0.0, (0.50 * new_lex) + (0.35 * new_sem) + (0.15 * new_stylo))), 2)
        report.score_composite = new_comp
    else:
        scores = [
            new_sim if s.id == sentence.id else (0.0 if s.match_type == "NONE" else float(s.similarity_score or 0.0))
            for s in all_sentences
        ] if all_sentences else [new_sim]
        new_comp = round(sum(scores) / max(len(scores), 1), 2)
        if report is not None:
            report.score_composite = new_comp

    if report is not None and report.heatmap_annotations:
        report.heatmap_annotations = _update_heatmap_annotations(
            report.heatmap_annotations, sentence.id, {str(sid) for sid in scope_ids},
            old_start, selected_text, delta, new_sim, not signals,
        )

    return {
        "sentence_id": sentence.id, "current_text": sentence.current_text, "match_type": "RESOLVED_GREEN",
        "new_similarity": new_sim, "new_composite_score": new_comp, "is_modified": True,
    }
