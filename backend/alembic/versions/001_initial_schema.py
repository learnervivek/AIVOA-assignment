"""initial pharma rca schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-23 18:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Investigations Table
    op.create_table(
        'investigations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('deviation_number', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('api_product_name', sa.String(length=255), nullable=False),
        sa.Column('batch_lot_number', sa.String(length=100), nullable=False),
        sa.Column('equipment_id', sa.String(length=100), nullable=False),
        sa.Column('manufacturing_stage', sa.String(length=150), nullable=False),
        sa.Column('incident_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='Major'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('immediate_containment', sa.Text(), nullable=True),
        sa.Column('raw_input_text', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='text'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_investigations_id'), 'investigations', ['id'], unique=False)
    op.create_index(op.f('ix_investigations_deviation_number'), 'investigations', ['deviation_number'], unique=True)
    op.create_index(op.f('ix_investigations_api_product_name'), 'investigations', ['api_product_name'], unique=False)
    op.create_index(op.f('ix_investigations_batch_lot_number'), 'investigations', ['batch_lot_number'], unique=False)
    op.create_index(op.f('ix_investigations_equipment_id'), 'investigations', ['equipment_id'], unique=False)
    op.create_index(op.f('ix_investigations_status'), 'investigations', ['status'], unique=False)

    # 2. RCA Analyses Table
    op.create_table(
        'rca_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('investigation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('methodology', sa.String(length=50), nullable=False, server_default='fishbone'),
        sa.Column('five_whys_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('fishbone_6m_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('potential_root_causes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('missing_evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['investigation_id'], ['investigations.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_rca_analyses_id'), 'rca_analyses', ['id'], unique=False)
    op.create_index(op.f('ix_rca_analyses_investigation_id'), 'rca_analyses', ['investigation_id'], unique=False)

    # 3. CAPA Recommendations Table
    op.create_table(
        'capa_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('investigation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False, server_default='Corrective'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('owner', sa.String(length=150), nullable=False),
        sa.Column('target_due_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Proposed'),
        sa.Column('is_ai_suggested', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['investigation_id'], ['investigations.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_capa_recommendations_id'), 'capa_recommendations', ['id'], unique=False)
    op.create_index(op.f('ix_capa_recommendations_investigation_id'), 'capa_recommendations', ['investigation_id'], unique=False)
    op.create_index(op.f('ix_capa_recommendations_status'), 'capa_recommendations', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_capa_recommendations_status'), table_name='capa_recommendations')
    op.drop_index(op.f('ix_capa_recommendations_investigation_id'), table_name='capa_recommendations')
    op.drop_index(op.f('ix_capa_recommendations_id'), table_name='capa_recommendations')
    op.drop_table('capa_recommendations')

    op.drop_index(op.f('ix_rca_analyses_investigation_id'), table_name='rca_analyses')
    op.drop_index(op.f('ix_rca_analyses_id'), table_name='rca_analyses')
    op.drop_table('rca_analyses')

    op.drop_index(op.f('ix_investigations_status'), table_name='investigations')
    op.drop_index(op.f('ix_investigations_equipment_id'), table_name='investigations')
    op.drop_index(op.f('ix_investigations_batch_lot_number'), table_name='investigations')
    op.drop_index(op.f('ix_investigations_api_product_name'), table_name='investigations')
    op.drop_index(op.f('ix_investigations_deviation_number'), table_name='investigations')
    op.drop_index(op.f('ix_investigations_id'), table_name='investigations')
    op.drop_table('investigations')
