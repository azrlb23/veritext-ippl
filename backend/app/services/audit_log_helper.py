from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


def record_token_debit(
    db: AsyncSession,
    actor_id: uuid.UUID | None,
    resource_type: str,
    resource_id: uuid.UUID | None,
    amount: int,
    reason: str,
) -> None:
    """Catat mutasi pemotongan token ke tabel audit_logs."""
    db.add(
        AuditLog(
            actor_id=actor_id,
            action_type="TOKEN_DEBIT",
            resource_type=resource_type,
            resource_id=resource_id,
            action_result="SUCCESS",
            meta_data={"amount": abs(amount), "reason": reason},
        )
    )
