"""create complaints table

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'complaints',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=False),
        sa.Column('reporter_contact', sa.String(length=200), nullable=True),
        sa.Column('category', sa.String(length=32), nullable=False),
        sa.Column('priority', sa.String(length=16), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='open'),
        sa.Column('ai_summary', sa.String(length=140), nullable=True),
        sa.Column('triaged_by', sa.String(length=32), nullable=False),
        sa.Column('triage_latency_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('char_length(text) >= 10 AND char_length(text) <= 2000', name='ck_complaints_text_len'),
        sa.CheckConstraint('char_length(location) >= 3 AND char_length(location) <= 200', name='ck_complaints_location_len'),
        sa.CheckConstraint("category IN ('water','electricity','sanitation','roads','streetlights','other')", name='ck_complaints_category'),
        sa.CheckConstraint("priority IN ('high','normal','low')", name='ck_complaints_priority'),
        sa.CheckConstraint("status IN ('open','in_progress','resolved','rejected')", name='ck_complaints_status'),
        sa.CheckConstraint('ai_summary IS NULL OR char_length(ai_summary) <= 140', name='ck_complaints_ai_summary_len'),
        sa.CheckConstraint("ai_summary IS NULL OR ai_summary !~ E'[\\n\\r]'", name='ck_complaints_ai_summary_one_line'),
        sa.CheckConstraint("triaged_by IN ('llm:groq','llm:ollama','rules','rules:fallback','simulated')", name='ck_complaints_triaged_by'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_complaints_status_priority', 'complaints', ['status', 'priority'])
    op.create_index('ix_complaints_created_at', 'complaints', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_complaints_created_at', table_name='complaints')
    op.drop_index('ix_complaints_status_priority', table_name='complaints')
    op.drop_table('complaints')
