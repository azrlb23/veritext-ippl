"""Asisten AI dengan konteks banyak naskah (opsi B).

chat_sessions.document_id menjadi opsional dan relasi chat_session_documents ditambahkan.

Revision ID: 0006_chat_multi_document
Revises: 0005_chat_and_subcredits
Create Date: 2026-11-08 12:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0006_chat_multi_document"
down_revision: str | None = "0005_chat_and_subcredits"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("chat_sessions", "document_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    op.create_table(
        "chat_session_documents",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_chat_session_documents_document_id", "chat_session_documents", ["document_id"])
    op.execute(
        "INSERT INTO chat_session_documents (session_id, document_id) "
        "SELECT id, document_id FROM chat_sessions WHERE document_id IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_index("idx_chat_session_documents_document_id", table_name="chat_session_documents")
    op.drop_table("chat_session_documents")
    op.execute("DELETE FROM chat_sessions WHERE document_id IS NULL")
    op.alter_column("chat_sessions", "document_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)
