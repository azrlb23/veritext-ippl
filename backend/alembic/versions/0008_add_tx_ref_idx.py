"""Add index on token_transactions.reference_id.

Revision ID: 0008_add_tx_ref_idx
Revises: 0007_fix_tx_and_invoice_constraints
Create Date: 2026-11-28 00:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0008_add_tx_ref_idx"
down_revision: str | None = "0007_fix_tx_and_invoice_constraints"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_token_transactions_reference_id", "token_transactions", ["reference_id"], unique=False, if_not_exists=True)


def downgrade() -> None:
    op.drop_index("ix_token_transactions_reference_id", table_name="token_transactions", if_exists=True)
