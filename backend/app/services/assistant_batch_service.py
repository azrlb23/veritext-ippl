from __future__ import annotations

import re
import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditSentence, AuditTask

_PRIORITY_ORDER: dict[str, int] = {"RED": 0, "ORANGE": 1, "YELLOW": 2}
_TEMPLATE_RE = re.compile(
    r"^(bab\s+[ivx\d]+|daftar\s+(isi|pustaka|gambar|tabel)|abstrak|kata\s+pengantar|pendahuluan|penutup|kesimpulan|lampiran|informatika)\b",
    re.IGNORECASE,
)


def _is_substantive_sentence(text: str) -> bool:
    cleaned = " ".join((text or "").split())
    if len(cleaned) < 28 or len(cleaned.split()) < 5:
        return False
    return not bool(_TEMPLATE_RE.match(cleaned) and len(cleaned.split()) <= 6)


async def fetch_priority_sentences(
    db: AsyncSession,
    user_id,
    document_id: uuid.UUID,
    limit: int = 5,
) -> dict[str, Any]:
    """Fetch top 1..5 highest-priority unmodified flagged sentences for a document."""
    capped_limit = max(1, min(int(limit), 5))
    task_stmt = (
        select(AuditTask)
        .options(selectinload(AuditTask.report))
        .where(
            AuditTask.document_id == document_id,
            AuditTask.user_id == user_id,
            AuditTask.status == "SUCCESS",
        )
        .order_by(AuditTask.completed_at.desc(), AuditTask.created_at.desc())
        .limit(1)
    )
    task = (await db.execute(task_stmt)).scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Audit untuk naskah ini belum selesai atau tidak ditemukan.",
        )

    priority_case = case(
        _PRIORITY_ORDER,
        value=AuditSentence.match_type,
        else_=99,
    )
    sent_stmt = (
        select(AuditSentence)
        .where(
            AuditSentence.audit_task_id == task.id,
            AuditSentence.is_modified.is_(False),
            AuditSentence.match_type.in_(tuple(_PRIORITY_ORDER.keys())),
        )
        .order_by(
            priority_case.asc(),
            AuditSentence.similarity_score.desc(),
            AuditSentence.sentence_index.asc(),
        )
        .limit(capped_limit * 10)
    )
    rows = list((await db.execute(sent_stmt)).scalars().all())
    eligible = [
        s
        for s in rows
        if not bool(getattr(s, "is_modified", False))
        and getattr(s, "match_type", None) in _PRIORITY_ORDER
        and _is_substantive_sentence(s.current_text or s.sentence_text or "")
    ]
    if not eligible:
        eligible = [
            s for s in rows
            if not bool(getattr(s, "is_modified", False)) and getattr(s, "match_type", None) in _PRIORITY_ORDER
        ]
    eligible.sort(
        key=lambda s: (
            _PRIORITY_ORDER[s.match_type],
            -float(s.similarity_score or 0.0),
            int(getattr(s, "sentence_index", 0) or 0),
        )
    )
    selected = eligible[:capped_limit]
    report = getattr(task, "report", None)

    return {
        "audit_task_id": str(task.id),
        "report_id": str(report.id) if report else None,
        "items": [
            {
                "sentence_id": str(s.id),
                "text": s.current_text or s.sentence_text,
                "match_type": s.match_type,
                "similarity_score": float(s.similarity_score or 0.0),
            }
            for s in selected
        ],
    }
