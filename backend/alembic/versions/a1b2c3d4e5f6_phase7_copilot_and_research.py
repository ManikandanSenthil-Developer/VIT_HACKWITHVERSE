"""phase7_copilot_and_research

Revision ID: a1b2c3d4e5f6
Revises: 7c8de411741c
Create Date: 2026-09-01 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '7c8de411741c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Copilot Conversations
    op.create_table(
        'copilot_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_copilot_conversations_id'), 'copilot_conversations', ['id'], unique=False)
    op.create_index(op.f('ix_copilot_conversations_user_id'), 'copilot_conversations', ['user_id'], unique=False)

    # 2. Copilot Messages
    op.create_table(
        'copilot_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(length=100), nullable=True),
        sa.Column('tool_calls_json', sa.Text(), nullable=True),
        sa.Column('tool_results_json', sa.Text(), nullable=True),
        sa.Column('citations_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['copilot_conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_copilot_messages_id'), 'copilot_messages', ['id'], unique=False)
    op.create_index(op.f('ix_copilot_messages_conversation_id'), 'copilot_messages', ['conversation_id'], unique=False)

    # 3. Decision Journal Entries
    op.create_table(
        'decision_journal_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('thesis_title', sa.String(length=255), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('risk_assessment', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('last_reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decision_journal_entries_id'), 'decision_journal_entries', ['id'], unique=False)
    op.create_index(op.f('ix_decision_journal_entries_user_id'), 'decision_journal_entries', ['user_id'], unique=False)
    op.create_index(op.f('ix_decision_journal_entries_symbol'), 'decision_journal_entries', ['symbol'], unique=False)

    # 4. Research Theses
    op.create_table(
        'research_theses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('bull_case_json', sa.Text(), nullable=False),
        sa.Column('bear_case_json', sa.Text(), nullable=False),
        sa.Column('counterarguments_json', sa.Text(), nullable=False),
        sa.Column('invalidation_conditions_json', sa.Text(), nullable=False),
        sa.Column('what_to_monitor_json', sa.Text(), nullable=False),
        sa.Column('evidence_citations_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_theses_id'), 'research_theses', ['id'], unique=False)
    op.create_index(op.f('ix_research_theses_user_id'), 'research_theses', ['user_id'], unique=False)
    op.create_index(op.f('ix_research_theses_symbol'), 'research_theses', ['symbol'], unique=False)


def downgrade() -> None:
    op.drop_table('research_theses')
    op.drop_table('decision_journal_entries')
    op.drop_table('copilot_messages')
    op.drop_table('copilot_conversations')
