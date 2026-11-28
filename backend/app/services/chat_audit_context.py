from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditReport, AuditTask
from app.models.document import Document
from app.services.chat_context import load_audited_sentences_map, load_focus_sentence_context

_COLORS = ("RED", "ORANGE", "YELLOW", "RESOLVED_GREEN")
_PRIORITY = {"RED": 0, "ORANGE": 1, "YELLOW": 2}
_CITATION_KEYS = ("sitasi", "doi", "daftar pustaka")


def _clip(text: Any, limit: int = 140) -> str:
    cleaned = " ".join(str(text or "").split())
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 3].rstrip() + "..."


def _count_colors(annos: list[dict[str, Any]]) -> dict[str, int]:
    counts = {c: 0 for c in _COLORS}
    for item in annos:
        if (color := str(item.get("color") or "").upper()) in counts:
            counts[color] += 1
    return counts


def _num(obj: Any, attr: str) -> float:
    return float(getattr(obj, attr, 0.0) or 0.0)


def format_single_report_summary(filename: str, report: AuditReport) -> str:
    """Merangkum skor, sebaran warna, sumber teratas, temuan sitasi, dan kalimat bermasalah."""
    annos = [a for a in (getattr(report, "heatmap_annotations", None) or []) if isinstance(a, dict)]
    sources = [s for s in (getattr(report, "matched_sources", None) or []) if isinstance(s, dict)]
    counts = _count_colors(annos)
    lines = [
        f'Laporan Audit "{filename}":',
        f"- Skor: Komposit {_num(report, 'score_composite'):.1f}% | T1 Leksikal {_num(report, 'score_lexical'):.1f}% | T2 Semantik {_num(report, 'score_semantic'):.1f}% | T3 Stilometri/AI {_num(report, 'score_stylometric'):.1f}%",
        f"- Sebaran kalimat: RED={counts['RED']}, ORANGE={counts['ORANGE']}, YELLOW={counts['YELLOW']}, RESOLVED_GREEN={counts['RESOLVED_GREEN']}",
    ]
    if sources:
        lines.append("- Sumber pembanding teratas:")
        for src in sources[:5]:
            url = src.get("source_url") or src.get("url")
            lines.append(f"  * {_clip(src.get('title') or 'Sumber Tanpa Judul', 80)}: {float(src.get('contribution_pct') or 0.0):.1f}%{f' ({url})' if url else ''}")
    cit_annos = [a for a in annos if any(k in f"{a.get('reason') or ''} {a.get('ai_reason') or ''}".lower() for k in _CITATION_KEYS)]
    if cit_annos:
        lines.append("- Temuan verifikasi sitasi/daftar pustaka:")
        for item in cit_annos[:5]:
            lines.append(f'  * {_clip(item.get("ai_reason") or item.get("reason") or "Anomali sitasi", 120)} | "{_clip(item.get("text_snippet"), 120)}"')
    flagged = [a for a in annos if str(a.get("color") or "").upper() in _PRIORITY]
    if flagged:
        ranked = sorted(
            flagged,
            key=lambda a: (
                _PRIORITY[str(a.get("color") or "").upper()],
                -float(a.get("similarity") or a.get("ai_score") or 0.0),
            ),
        )
        picked = ranked[:6]
        yellows = [a for a in ranked if str(a.get("color") or "").upper() == "YELLOW" and a not in picked]
        picked.extend(yellows[:2])
        lines.append("- Contoh kalimat terindikasi prioritas:")
        for item in picked[:8]:
            src = _clip(item.get("source_title") or item.get("reason") or item.get("ai_reason") or "-", 70)
            detail = _clip(item.get("reason") or item.get("ai_reason") or "", 70)
            meta = f"{src}; {detail}" if detail and detail != src else src
            lines.append(f'  * [{str(item.get("color") or "").upper()}/{item.get("tier") or "-"}] ({meta}): "{_clip(item.get("text_snippet"), 140)}"')
    return "\n".join(lines)


def _format_draft_comparison(items: list[tuple[str, AuditReport]]) -> str:
    lines = ["Perbandingan Skor Antar-Draf:"]
    for idx, (fname, rep) in enumerate(items, 1):
        annos = [a for a in (getattr(rep, "heatmap_annotations", None) or []) if isinstance(a, dict)]
        resolved = _count_colors(annos)["RESOLVED_GREEN"]
        lines.append(
            f"- Draf {idx} ({fname}): Komposit {_num(rep, 'score_composite'):.1f}% | "
            f"T1 {_num(rep, 'score_lexical'):.1f}% | T2 {_num(rep, 'score_semantic'):.1f}% | "
            f"T3 {_num(rep, 'score_stylometric'):.1f}% | Resolved={resolved}"
        )
    return "\n".join(lines)


async def load_audit_reports_context(db: AsyncSession, user_id, docs: list[Document]) -> str:
    """Memuat ringkasan laporan audit terbaru untuk dokumen yang dilampirkan."""
    doc_ids = [d.id for d in docs if getattr(d, "id", None)]
    if not doc_ids:
        return ""
    stmt = (
        select(AuditTask).options(selectinload(AuditTask.report))
        .where(AuditTask.document_id.in_(doc_ids), AuditTask.user_id == user_id, AuditTask.status.in_(("SUCCESS", "COMPLETED")))
        .order_by(AuditTask.completed_at.desc(), AuditTask.created_at.desc())
    )
    latest: dict[Any, AuditTask] = {}
    for task in (await db.execute(stmt)).scalars().all():
        if task.document_id not in latest and task.report is not None:
            latest[task.document_id] = task
    ordered = [
        (getattr(doc, "original_filename", None) or "Naskah", latest[doc.id].report)
        for doc in docs if getattr(doc, "id", None) in latest and latest[doc.id].report is not None
    ]
    if not ordered:
        return ""
    blocks = [format_single_report_summary(fname, rep) for fname, rep in ordered]
    if len(ordered) >= 2:
        blocks.append(_format_draft_comparison(ordered))
    return "\n\n".join(blocks)


async def load_chat_audit_bundle(
    db: AsyncSession, user_id, docs: list[Document], sentence_id
) -> tuple[str, dict[Any, list[str]]]:
    """Menggabungkan konteks kalimat fokus, ringkasan laporan audit, dan peta kalimat teraudit."""
    focus_ctx = await load_focus_sentence_context(db, user_id, sentence_id) if sentence_id else ""
    doc_ids = [d.id for d in docs if getattr(d, "id", None)]
    report_ctx = await load_audit_reports_context(db, user_id, docs) if doc_ids else ""
    audited_map = await load_audited_sentences_map(db, user_id, doc_ids) if doc_ids else {}
    return "\n\n".join(part for part in (focus_ctx, report_ctx) if part), audited_map
