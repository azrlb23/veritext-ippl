"""Fix CHECK constraints on token_transactions and invoices.

Revision ID: 0007_fix_tx_and_invoice_constraints
Revises: 0006_chat_multi_document
Create Date: 2026-11-19 16:36:38.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0007_fix_tx_and_invoice_constraints"
down_revision: str | None = "0006_chat_multi_document"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TX_TYPES_NEW = (
    "'DEBIT_AUDIT', 'DEBIT_CHAT_PARAPHRASE', 'CREDIT_TOPUP', "
    "'CREDIT_REFUND', 'CREDIT_ADMIN', 'DEBIT_ADMIN', 'REFUND'"
)
_TX_TYPES_OLD = (
    "'DEBIT_AUDIT', 'CREDIT_TOPUP', 'CREDIT_REFUND', 'CREDIT_ADMIN', 'DEBIT_ADMIN'"
)
_INV_STATUS_NEW = "'PENDING', 'PAID', 'EXPIRED', 'FAILED', 'CANCEL', 'CHALLENGE'"
_INV_STATUS_OLD = "'PENDING', 'PAID', 'EXPIRED', 'FAILED', 'CANCEL'"


def upgrade() -> None:
    op.execute("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(64)")
    op.execute("ALTER TABLE token_transactions DROP CONSTRAINT IF EXISTS token_transactions_transaction_type_check")
    op.execute("ALTER TABLE token_transactions DROP CONSTRAINT IF EXISTS chk_transaction_type")
    op.execute(
        f"ALTER TABLE token_transactions ADD CONSTRAINT chk_transaction_type "
        f"CHECK (transaction_type IN ({_TX_TYPES_NEW}))"
    )
    op.execute("ALTER TABLE invoices DROP CONSTRAINT IF EXISTS invoices_status_check")
    op.execute("ALTER TABLE invoices DROP CONSTRAINT IF EXISTS chk_invoice_status")
    op.execute(
        f"ALTER TABLE invoices ADD CONSTRAINT chk_invoice_status "
        f"CHECK (status IN ({_INV_STATUS_NEW}))"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE token_transactions DROP CONSTRAINT IF EXISTS chk_transaction_type")
    op.execute(
        f"ALTER TABLE token_transactions ADD CONSTRAINT chk_transaction_type "
        f"CHECK (transaction_type IN ({_TX_TYPES_OLD}))"
    )
    op.execute("ALTER TABLE invoices DROP CONSTRAINT IF EXISTS chk_invoice_status")
    op.execute(
        f"ALTER TABLE invoices ADD CONSTRAINT chk_invoice_status "
        f"CHECK (status IN ({_INV_STATUS_OLD}))"
    )
