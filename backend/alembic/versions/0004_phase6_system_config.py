"""Phase 6 System Config: Persistent engine hyperparameters & operational settings

Revision ID: 0004_phase6_system_config
Revises: 0003_phase3_pdp_compliance
Create Date: 2026-10-24 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0004_phase6_system_config'
down_revision: Union[str, None] = '0003_phase3_pdp_compliance'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'system_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lexical_weight', sa.Float(), nullable=False, server_default='0.50'),
        sa.Column('semantic_weight', sa.Float(), nullable=False, server_default='0.35'),
        sa.Column('stylometric_weight', sa.Float(), nullable=False, server_default='0.15'),
        sa.Column('similarity_threshold', sa.Float(), nullable=False, server_default='0.78'),
        sa.Column('stylometric_burstiness_threshold', sa.Float(), nullable=False, server_default='0.35'),
        sa.Column('winnowing_kgram', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('winnowing_window', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('hnsw_ef_search', sa.Integer(), nullable=False, server_default='64'),
        sa.Column('hnsw_m', sa.Integer(), nullable=False, server_default='16'),
        sa.Column('retention_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('sandbox_mode', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('system_configs')
