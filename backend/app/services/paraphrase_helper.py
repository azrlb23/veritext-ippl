from __future__ import annotations

from typing import Any

from app.models.audit import AuditReport, AuditSentence


def _recompute_tier_score(
    old_score: float,
    old_match_type: str | None,
    target_match_type: str,
    old_sim: float,
    sentence_id: Any,
    all_sentences: list[AuditSentence],
) -> float:
    if old_match_type != target_match_type or old_score <= 0.0:
        return round(old_score, 2)
    other_total = sum(
        float(s.similarity_score or 0.0)
        for s in all_sentences
        if s.id != sentence_id and s.match_type == target_match_type
    )
    prev_total = other_total + old_sim
    if prev_total <= 0.0:
        return round(old_score, 2)
    residual = min(6.0, old_sim)
    new_val = old_score * max(0.0, prev_total - old_sim + residual) / prev_total
    return round(min(100.0, max(0.0, new_val)), 2)


def _update_heatmap_annotations(
    annotations: list[Any],
    sentence_id: Any,
    old_start: int,
    selected_text: str,
    delta: int,
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
        is_target = (item_sid == sid_str) or (item_sid is None and item_start == old_start)
        if is_target:
            item["color"] = "RESOLVED_GREEN"
            item["text_snippet"] = selected_text
            item["similarity"] = 6.0
            if delta != 0 and "end" in item:
                item["end"] = int(item["end"]) + delta
        elif delta != 0 and item_start > old_start:
            item["start"] = item_start + delta
            if "end" in item:
                item["end"] = int(item["end"]) + delta
        updated.append(item)
    return updated


def apply_paraphrase_update(
    sentence: AuditSentence,
    selected_text: str,
    all_sentences: list[AuditSentence],
    report: AuditReport | None = None,
) -> dict[str, Any]:
    old_text = sentence.current_text or sentence.sentence_text or ""
    old_match = sentence.match_type
    old_sim = float(sentence.similarity_score or 0.0)
    old_start = int(getattr(sentence, "start_char", 0) or 0)
    old_end = int(getattr(sentence, "end_char", 0) or 0)
    old_idx = getattr(sentence, "sentence_index", None)
    delta = len(selected_text) - len(old_text)

    sentence.current_text = selected_text
    sentence.match_type = "RESOLVED_GREEN"
    sentence.is_modified = True
    sentence.similarity_score = 6.0
    sentence.lexical_similarity = 0.06
    sentence.semantic_similarity = 0.06
    if delta != 0 and hasattr(sentence, "end_char") and sentence.end_char is not None:
        sentence.end_char = old_end + delta

    if delta != 0:
        for s in all_sentences:
            if s.id == sentence.id:
                continue
            s_idx = getattr(s, "sentence_index", None)
            is_after = (s_idx > old_idx) if (old_idx is not None and s_idx is not None) else ((s.start_char or 0) > old_start)
            if is_after:
                s.start_char = int(s.start_char or 0) + delta
                s.end_char = int(s.end_char or 0) + delta

    if report is not None and (report.score_lexical is not None or report.score_semantic is not None):
        new_lex = _recompute_tier_score(float(report.score_lexical or 0.0), old_match, "RED", old_sim, sentence.id, all_sentences)
        new_sem = _recompute_tier_score(float(report.score_semantic or 0.0), old_match, "ORANGE", old_sim, sentence.id, all_sentences)
        stylo = float(report.score_stylometric or 0.0)
        report.score_lexical = new_lex
        report.score_semantic = new_sem
        new_comp = round(min(100.0, max(0.0, (0.50 * new_lex) + (0.35 * new_sem) + (0.15 * stylo))), 2)
        report.score_composite = new_comp
    else:
        scores = [
            6.0 if (s.id == sentence.id or s.match_type == "RESOLVED_GREEN")
            else (0.0 if s.match_type == "NONE" else float(s.similarity_score or 0.0))
            for s in all_sentences
        ] if all_sentences else [6.0]
        new_comp = round(sum(scores) / max(len(scores), 1), 2)
        if report is not None:
            report.score_composite = new_comp

    if report is not None and report.heatmap_annotations:
        report.heatmap_annotations = _update_heatmap_annotations(
            report.heatmap_annotations, sentence.id, old_start, selected_text, delta
        )

    return {
        "sentence_id": sentence.id,
        "current_text": sentence.current_text,
        "match_type": "RESOLVED_GREEN",
        "new_similarity": 6.0,
        "new_composite_score": new_comp,
        "is_modified": True,
    }
