"""Phase 2 security hardening: FK indices and unique constraint

Revision ID: 0002_phase2_security_hardening
Revises: 0001_initial_schema
Create Date: 2026-10-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_phase2_security_hardening'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Foreign key index on corpus_documents(uploaded_by) to prevent full table lock on user mutations
    op.create_index(
        'idx_corpus_documents_uploaded_by',
        'corpus_documents',
        ['uploaded_by'],
        unique=False,
    )

    # 2. Foreign key index on password_resets(user_id) to eliminate table lock on user deletion
    op.create_index(
        'idx_password_resets_user_id',
        'password_resets',
        ['user_id'],
        unique=False,
    )

    # 3. Composite unique constraint on document_chunks(corpus_doc_id, chunk_index)
    op.create_unique_constraint(
        'uq_document_chunks_corpus_chunk',
        'document_chunks',
        ['corpus_doc_id', 'chunk_index'],
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_document_chunks_corpus_chunk',
        'document_chunks',
        type_='unique',
    )
    op.drop_index('idx_password_resets_user_id', table_name='password_resets')
    op.drop_index('idx_corpus_documents_uploaded_by', table_name='corpus_documents')
