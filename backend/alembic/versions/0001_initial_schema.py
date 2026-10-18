"""initial schema with 14 tables and pgvector

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-11 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector";')

    # 2. users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('institution', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), server_default='TRIAL', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('failed_login_count', sa.SmallInteger(), server_default='0', nullable=False),
        sa.Column('lockout_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("role IN ('TRIAL', 'PREMIUM', 'REVIEWER', 'ADMIN')", name='chk_users_role'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])

    # 3. sessions
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=255), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('refresh_token_hash')
    )
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'])

    # 4. password_resets
    op.create_table(
        'password_resets',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )

    # 5. token_wallets
    op.create_table(
        'token_wallets',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('balance', sa.Integer(), server_default='0', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('balance >= 0', name='chk_wallet_balance_positive'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_token_wallets_user_id', 'token_wallets', ['user_id'])

    # 6. token_transactions
    op.create_table(
        'token_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('wallet_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('balance_after', sa.Integer(), nullable=False),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("transaction_type IN ('DEBIT_AUDIT', 'CREDIT_TOPUP', 'CREDIT_REFUND', 'CREDIT_ADMIN', 'DEBIT_ADMIN')", name='chk_transaction_type'),
        sa.ForeignKeyConstraint(['wallet_id'], ['token_wallets.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_token_transactions_wallet_id', 'token_transactions', ['wallet_id'])
    op.create_index('idx_token_transactions_created_at', 'token_transactions', [sa.text('created_at DESC')])

    # 7. invoices
    op.create_table(
        'invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', sa.String(length=100), nullable=False),
        sa.Column('snap_token', sa.Text(), nullable=True),
        sa.Column('package_name', sa.String(length=100), nullable=False),
        sa.Column('token_amount', sa.Integer(), nullable=False),
        sa.Column('gross_amount', sa.BigInteger(), nullable=False),
        sa.Column('payment_method', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('midtrans_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), server_default=sa.text("now() + interval '24 hours'"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("status IN ('PENDING', 'PAID', 'EXPIRED', 'FAILED', 'CANCEL')", name='chk_invoice_status'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id')
    )
    op.create_index('idx_invoices_user_id', 'invoices', ['user_id'])
    op.create_index('idx_invoices_order_id', 'invoices', ['order_id'])
    op.create_index('idx_invoices_status', 'invoices', ['status'])

    # 8. documents
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_filename', sa.String(length=500), nullable=False),
        sa.Column('stored_filename', sa.String(length=500), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('sha256_hash', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='UPLOADED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('UPLOADED', 'PROCESSING', 'READY', 'ERROR', 'DELETED')", name='chk_document_status'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stored_filename')
    )
    op.create_index('idx_documents_user_id', 'documents', ['user_id'])
    op.create_index('idx_documents_status', 'documents', ['status'])
    op.create_index('idx_documents_created_at', 'documents', [sa.text('created_at DESC')])

    # 9. audit_tasks
    op.create_table(
        'audit_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('celery_task_id', sa.String(length=255), nullable=True),
        sa.Column('audit_depth', sa.String(length=50), server_default='FULL', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='QUEUED', nullable=False),
        sa.Column('progress_pct', sa.SmallInteger(), server_default='0', nullable=False),
        sa.Column('current_stage', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("audit_depth IN ('TIER1_ONLY', 'FULL')", name='chk_audit_depth'),
        sa.CheckConstraint("status IN ('QUEUED', 'PROCESSING', 'SUCCESS', 'FAILED', 'CANCELLED', 'REVOKED')", name='chk_audit_status'),
        sa.CheckConstraint('progress_pct BETWEEN 0 AND 100', name='chk_progress_pct'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('celery_task_id')
    )
    op.create_index('idx_audit_tasks_user_id', 'audit_tasks', ['user_id'])
    op.create_index('idx_audit_tasks_document_id', 'audit_tasks', ['document_id'])
    op.create_index('idx_audit_tasks_status', 'audit_tasks', ['status'])
    op.create_index('idx_audit_tasks_celery_id', 'audit_tasks', ['celery_task_id'])

    # 10. audit_sentences
    op.create_table(
        'audit_sentences',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('audit_task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sentence_index', sa.Integer(), nullable=False),
        sa.Column('sentence_text', sa.Text(), nullable=False),
        sa.Column('start_char', sa.Integer(), nullable=False),
        sa.Column('end_char', sa.Integer(), nullable=False),
        sa.Column('word_count', sa.SmallInteger(), nullable=False),
        sa.Column('is_citation', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.ForeignKeyConstraint(['audit_task_id'], ['audit_tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('audit_task_id', 'sentence_index', name='uq_audit_task_sentence_index')
    )
    op.create_index('idx_audit_sentences_task_id', 'audit_sentences', ['audit_task_id'])

    # 11. audit_reports
    op.create_table(
        'audit_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('audit_task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('verification_uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('score_lexical', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('score_semantic', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('score_stylometric', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('score_composite', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('heatmap_annotations', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('matched_sources', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('pdf_path', sa.String(length=500), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['audit_task_id'], ['audit_tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('audit_task_id'),
        sa.UniqueConstraint('verification_uuid')
    )
    op.create_index('idx_audit_reports_task_id', 'audit_reports', ['audit_task_id'])
    op.create_index('idx_audit_reports_verification_uuid', 'audit_reports', ['verification_uuid'])

    # 12. corpus_documents
    op.create_table(
        'corpus_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('category', sa.String(length=255), nullable=True),
        sa.Column('academic_year', sa.String(length=20), nullable=True),
        sa.Column('stored_filename', sa.String(length=500), nullable=False),
        sa.Column('sha256_hash', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='PENDING_INDEX', nullable=False),
        sa.Column('total_chunks', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("status IN ('PENDING_INDEX', 'INDEXING', 'INDEXED', 'ERROR', 'DELETED')", name='chk_corpus_status'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stored_filename')
    )
    op.create_index('idx_corpus_documents_status', 'corpus_documents', ['status'])
    op.create_index('idx_corpus_documents_category', 'corpus_documents', ['category'])
    op.create_index('idx_corpus_documents_sha256', 'corpus_documents', ['sha256_hash'])

    # 13. document_chunks (pgvector 384 dimensions)
    op.execute("""
        CREATE TABLE document_chunks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            corpus_doc_id UUID NOT NULL REFERENCES corpus_documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            embedding vector(384) NOT NULL,
            start_char INTEGER,
            end_char INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)
    op.execute("""
        CREATE INDEX idx_document_chunks_vector
            ON document_chunks
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
    """)
    op.create_index('idx_document_chunks_corpus_doc_id', 'document_chunks', ['corpus_doc_id'])

    # 14. lexical_fingerprints
    op.create_table(
        'lexical_fingerprints',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('corpus_doc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fingerprint_hash', sa.BigInteger(), nullable=False),
        sa.Column('position_start', sa.Integer(), nullable=True),
        sa.Column('position_end', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['corpus_doc_id'], ['corpus_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_lexical_fingerprints_hash', 'lexical_fingerprints', ['fingerprint_hash'])
    op.create_index('idx_lexical_fingerprints_corpus_doc_id', 'lexical_fingerprints', ['corpus_doc_id'])

    # 15. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('actor_ip', sa.String(length=45), nullable=True),
        sa.Column('actor_user_agent', sa.Text(), nullable=True),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action_result', sa.String(length=50), server_default='SUCCESS', nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("action_result IN ('SUCCESS', 'FAILURE', 'BLOCKED')", name='chk_audit_log_action_result'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_actor_id', 'audit_logs', ['actor_id'])
    op.create_index('idx_audit_logs_action_type', 'audit_logs', ['action_type'])
    op.create_index('idx_audit_logs_created_at', 'audit_logs', [sa.text('created_at DESC')])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])

    # Append-only immutability rules for audit_logs
    op.execute("CREATE RULE audit_logs_no_update AS ON UPDATE TO audit_logs DO INSTEAD NOTHING;")
    op.execute("CREATE RULE audit_logs_no_delete AS ON DELETE TO audit_logs DO INSTEAD NOTHING;")


def downgrade() -> None:
    op.execute("DROP RULE IF EXISTS audit_logs_no_delete ON audit_logs;")
    op.execute("DROP RULE IF EXISTS audit_logs_no_update ON audit_logs;")
    op.drop_table('audit_logs')
    op.drop_table('lexical_fingerprints')
    op.drop_table('document_chunks')
    op.drop_table('corpus_documents')
    op.drop_table('audit_reports')
    op.drop_table('audit_sentences')
    op.drop_table('audit_tasks')
    op.drop_table('documents')
    op.drop_table('invoices')
    op.drop_table('token_transactions')
    op.drop_table('token_wallets')
    op.drop_table('password_resets')
    op.drop_table('sessions')
    op.drop_table('users')
