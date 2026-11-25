from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditSentence, AuditTask

_PRIORITY_ORDER: dict[str, int] = {"RED": 0, "ORANGE": 1, "YELLOW": 2}
_MIN_PROSE_WORDS = 7


def is_substantive_prose(text: str) -> bool:
    """Membedakan kalimat prosa akademik dari heading/label/frasa pendek secara struktural (tanpa daftar kata)."""
    cleaned = " ".join((text or "").split())
    words = [w.strip(".,;:!?\"'()[]") for w in cleaned.split() if w.strip(".,;:!?\"'()[]")]
    if len(words) < _MIN_PROSE_WORDS:
        return False

    alpha_words = [w for w in words if any(ch.isalpha() for ch in w)]
    if len(alpha_words) < _MIN_PROSE_WORDS:
        return False

    cap_ratio = sum(1 for w in alpha_words if w[0].isupper()) / len(alpha_words)
    if len(words) < 12 and cap_ratio >= 0.65:
        return False

    if len(words) < 10 and cleaned[-1] not in ".?!":
        return False
    return True


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
        and is_substantive_prose(s.current_text or s.sentence_text or "")
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
