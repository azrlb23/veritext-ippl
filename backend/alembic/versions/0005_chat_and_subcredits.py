"""Phase 6 Chat and subcredits schema migration.

Revision ID: 0005_chat_and_subcredits
Revises: 0004_phase6_system_config
Create Date: 2026-11-08 00:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005_chat_and_subcredits"
down_revision: str | None = "0004_phase6_system_config"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("token_wallets", sa.Column("ai_trial_remaining", sa.Integer(), nullable=False, server_default="3"))
    op.add_column("token_wallets", sa.Column("ai_chat_allowance_remaining", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("token_wallets", sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

    op.add_column("audit_sentences", sa.Column("current_text", sa.Text(), nullable=True))
    op.add_column("audit_sentences", sa.Column("match_type", sa.String(length=20), nullable=False, server_default="NONE"))
    op.add_column("audit_sentences", sa.Column("similarity_score", sa.Numeric(5, 2), nullable=False, server_default="0.00"))
    op.add_column("audit_sentences", sa.Column("matched_source_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("audit_sentences", sa.Column("is_modified", sa.Boolean(), nullable=False, server_default="false"))

    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, server_default="Konsultasi Naskah Ilmiah"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_chat_sessions_user_id", "chat_sessions", ["user_id"])
    op.create_index("idx_chat_sessions_document_id", "chat_sessions", ["document_id"])

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="USER"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("mode", sa.String(length=30), nullable=True, server_default="CONSULTATION"),
        sa.Column("suggested_options", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("applied_to_document", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("target_sentence_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("audit_sentences.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_chat_messages_session_id", "chat_messages", ["session_id"])


def downgrade() -> None:
    op.drop_index("idx_chat_messages_session_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("idx_chat_sessions_document_id", table_name="chat_sessions")
    op.drop_index("idx_chat_sessions_user_id", table_name="chat_sessions")
    op.drop_table("chat_sessions")

    op.drop_column("audit_sentences", "is_modified")
    op.drop_column("audit_sentences", "matched_source_id")
    op.drop_column("audit_sentences", "similarity_score")
    op.drop_column("audit_sentences", "match_type")
    op.drop_column("audit_sentences", "current_text")

    op.drop_column("token_wallets", "created_at")
    op.drop_column("token_wallets", "ai_chat_allowance_remaining")
    op.drop_column("token_wallets", "ai_trial_remaining")
