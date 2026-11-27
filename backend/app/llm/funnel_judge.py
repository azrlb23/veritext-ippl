from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Any

from app.core.config import settings

if TYPE_CHECKING:
    from app.engine.preprocessor import SentenceSpan

logger = logging.getLogger(__name__)


def _select_segment_sentences(
    seg: list[SentenceSpan], priority_indices: set[int], batch_size: int
) -> list[SentenceSpan]:
    if len(seg) <= batch_size:
        return sorted(seg, key=lambda s: s.index)

    prio_pos = [p for p, s in enumerate(seg) if s.index in priority_indices]
    prio_with_neighbors = prio_pos + [
        nb for p in prio_pos for nb in (p - 1, p + 1) if 0 <= nb < len(seg)
    ]
    chosen = list(dict.fromkeys(prio_with_neighbors))[:batch_size]
    seen = set(chosen)
    rem = batch_size - len(chosen)
    if rem > 0:
        avail = [p for p in range(len(seg)) if p not in seen]
        if len(avail) <= rem:
            chosen.extend(avail)
        elif rem == 1:
            chosen.append(avail[len(avail) // 2])
        else:
            step = dict.fromkeys(round(i * (len(avail) - 1) / (rem - 1)) for i in range(rem))
            chosen.extend(avail[k] for k in step)

    return sorted((seg[p] for p in chosen), key=lambda s: s.index)


def build_funnel_batches(
    meaningful: list[SentenceSpan], priority_indices: set[int], max_batches: int = 3, batch_size: int = 25
) -> list[list[SentenceSpan]]:
    if not meaningful or batch_size <= 0:
        return []
    if len(meaningful) <= batch_size:
        return [meaningful]
    n = len(meaningful)
    num_batches = min(max_batches, max(2, (n + batch_size - 1) // batch_size))
    batches: list[list[SentenceSpan]] = []
    for b in range(num_batches):
        if seg := meaningful[(b * n) // num_batches : ((b + 1) * n) // num_batches]:
            batches.append(_select_segment_sentences(seg, priority_indices, batch_size))
    return batches


def _parse_sentence_index(raw_idx: Any) -> int | None:
    if raw_idx is None or isinstance(raw_idx, bool):
        return None
    if isinstance(raw_idx, int):
        return raw_idx
    match = re.search(r"\d+", str(raw_idx))
    return int(match.group(0)) if match else None


def _merge_suspicious(
    merged: dict[int, dict[str, Any]], items: list[dict[str, Any]], confirm: bool = False
) -> None:
    for item in items:
        if not isinstance(item, dict) or (s_idx := _parse_sentence_index(item.get("sentence_index"))) is None:
            continue
        try:
            score = max(0.0, min(1.0, float(item.get("anomaly_score", 0.75))))
        except (ValueError, TypeError):
            score = 0.75
        reason = str(item.get("reason", "Indikasi pola tulisan AI generatif")).strip()
        if s_idx not in merged:
            merged[s_idx] = {"sentence_index": s_idx, "reason": reason, "anomaly_score": score}
        elif confirm:
            cur = merged[s_idx]
            cur["anomaly_score"] = max(float(cur.get("anomaly_score", 0.0)), score)
            if reason and reason not in cur["reason"]:
                cur["reason"] = f"{cur['reason']}; {reason}"
        elif score > float(merged[s_idx].get("anomaly_score", 0.0)):
            merged[s_idx] = {"sentence_index": s_idx, "reason": reason, "anomaly_score": score}


def evaluate_funnel_parallel(
    gateway: Any,
    sentences: list[SentenceSpan],
    stage1_hints: list[str] | None = None,
    priority_indices: set[int] | None = None,
) -> tuple[dict[str, Any] | None, str]:
    meaningful = [s for s in sentences if not s.is_citation and s.word_count >= 3]
    prio_set = priority_indices or set()
    batches = build_funnel_batches(meaningful, prio_set, max_batches=3, batch_size=min(25, settings.WEB_SCAN_MAX_SENTENCES))
    if not batches:
        return None, ""

    results: list[tuple[int, dict[str, Any], str]] = []
    with ThreadPoolExecutor(max_workers=len(batches)) as pool:
        fmap = {pool.submit(gateway.evaluate_batch, b, stage1_hints=stage1_hints): i for i, b in enumerate(batches)}
        for fut in as_completed(fmap):
            idx = fmap[fut]
            try:
                data, name = fut.result()
                if data is not None:
                    results.append((idx, data, name))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Funnel batch %d gagal: %s", idx, exc)

    if not results:
        return None, ""
    results.sort(key=lambda r: r[0])
    total_w = sum(len(batches[idx]) for idx, _, _ in results)
    avg_prob = round(sum(float(d["ai_probability"]) * len(batches[idx]) for idx, d, _ in results) / max(1, total_w), 2)
    merged: dict[int, dict[str, Any]] = {}
    for _, data, _ in results:
        _merge_suspicious(merged, data.get("suspicious_sentences", []))

    primary_name = results[0][2]
    evaluator_name = primary_name
    if 35.0 <= avg_prob <= 65.0 and len(gateway._client_order()) >= 2:
        focus_idx, _, _ = max(
            results,
            key=lambda r: (len(r[1].get("suspicious_sentences", [])) + sum(1 for s in batches[r[0]] if s.index in prio_set), -r[0]),
        )
        sec_data, sec_name = gateway.evaluate_batch(batches[focus_idx], stage1_hints=stage1_hints, skip_first=True)
        if sec_data is not None and sec_name:
            avg_prob = round(0.5 * avg_prob + 0.5 * float(sec_data["ai_probability"]), 2)
            _merge_suspicious(merged, sec_data.get("suspicious_sentences", []), confirm=True)
            evaluator_name = f"{primary_name} + {sec_name}"

    return {"ai_probability": avg_prob, "suspicious_sentences": [merged[k] for k in sorted(merged)]}, evaluator_name
