"""Phase 3 PDP compliance: Anonymization rule and corpus uploaded_by FK

Revision ID: 0003_phase3_pdp_compliance
Revises: 0002_phase2_security_hardening
Create Date: 2026-10-24 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_phase3_pdp_compliance'
down_revision: Union[str, None] = '0002_phase2_security_hardening'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update audit_logs_no_update rule to allow actor_id anonymization (UU PDP Pasal 8)
    op.execute("DROP RULE IF EXISTS audit_logs_no_update ON audit_logs;")
    op.execute(
        "CREATE RULE audit_logs_no_update AS ON UPDATE TO audit_logs "
        "WHERE NEW.actor_id IS NOT NULL DO INSTEAD NOTHING;"
    )

    # 2. Relax corpus_documents.uploaded_by to nullable with ON DELETE SET NULL
    op.alter_column('corpus_documents', 'uploaded_by', nullable=True)
    op.drop_constraint('corpus_documents_uploaded_by_fkey', 'corpus_documents', type_='foreignkey')
    op.create_foreign_key(
        'corpus_documents_uploaded_by_fkey',
        'corpus_documents',
        'users',
        ['uploaded_by'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('corpus_documents_uploaded_by_fkey', 'corpus_documents', type_='foreignkey')
    op.create_foreign_key(
        'corpus_documents_uploaded_by_fkey',
        'corpus_documents',
        'users',
        ['uploaded_by'],
        ['id'],
    )
    op.alter_column('corpus_documents', 'uploaded_by', nullable=False)
    op.execute("DROP RULE IF EXISTS audit_logs_no_update ON audit_logs;")
    op.execute("CREATE RULE audit_logs_no_update AS ON UPDATE TO audit_logs DO INSTEAD NOTHING;")
