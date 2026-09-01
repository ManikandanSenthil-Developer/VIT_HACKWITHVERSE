"""phase8_ecosystem_and_accessibility

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-01 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. User Accessibility Preferences
    op.create_table(
        'user_accessibility_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=10), server_default='en', nullable=False),
        sa.Column('text_size', sa.String(length=20), server_default='normal', nullable=False),
        sa.Column('reduced_motion', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('high_contrast', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('voice_enabled', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_accessibility_preferences_id'), 'user_accessibility_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_user_accessibility_preferences_user_id'), 'user_accessibility_preferences', ['user_id'], unique=True)

    # 2. User Feedbacks
    op.create_table(
        'user_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.String(length=100), nullable=False),
        sa.Column('is_helpful', sa.Boolean(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_feedbacks_id'), 'user_feedbacks', ['id'], unique=False)
    op.create_index(op.f('ix_user_feedbacks_user_id'), 'user_feedbacks', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_feedbacks_target_type'), 'user_feedbacks', ['target_type'], unique=False)
    op.create_index(op.f('ix_user_feedbacks_target_id'), 'user_feedbacks', ['target_id'], unique=False)

    # 3. Broker Connections
    op.create_table(
        'broker_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('broker_name', sa.String(length=100), nullable=False),
        sa.Column('account_id', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('is_read_only', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('last_synced_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_broker_connections_id'), 'broker_connections', ['id'], unique=False)
    op.create_index(op.f('ix_broker_connections_user_id'), 'broker_connections', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_broker_connections_user_id'), table_name='broker_connections')
    op.drop_index(op.f('ix_broker_connections_id'), table_name='broker_connections')
    op.drop_table('broker_connections')

    op.drop_index(op.f('ix_user_feedbacks_target_id'), table_name='user_feedbacks')
    op.drop_index(op.f('ix_user_feedbacks_target_type'), table_name='user_feedbacks')
    op.drop_index(op.f('ix_user_feedbacks_user_id'), table_name='user_feedbacks')
    op.drop_index(op.f('ix_user_feedbacks_id'), table_name='user_feedbacks')
    op.drop_table('user_feedbacks')

    op.drop_index(op.f('ix_user_accessibility_preferences_user_id'), table_name='user_accessibility_preferences')
    op.drop_index(op.f('ix_user_accessibility_preferences_id'), table_name='user_accessibility_preferences')
    op.drop_table('user_accessibility_preferences')
