"""phase9_adaptive_intelligence

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-01 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Agent Execution Metrics
    op.create_table(
        'agent_execution_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(length=50), nullable=False),
        sa.Column('analysis_id', sa.String(length=100), nullable=True),
        sa.Column('task_type', sa.String(length=100), nullable=False),
        sa.Column('execution_time_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('evidence_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='SUCCESS'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_execution_metrics_id'), 'agent_execution_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_agent_execution_metrics_agent_name'), 'agent_execution_metrics', ['agent_name'], unique=False)
    op.create_index(op.f('ix_agent_execution_metrics_task_type'), 'agent_execution_metrics', ['task_type'], unique=False)
    op.create_index(op.f('ix_agent_execution_metrics_analysis_id'), 'agent_execution_metrics', ['analysis_id'], unique=False)

    # 2. Knowledge Entities
    op.create_table(
        'knowledge_entities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_key', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('entity_key')
    )
    op.create_index(op.f('ix_knowledge_entities_id'), 'knowledge_entities', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_entities_entity_type'), 'knowledge_entities', ['entity_type'], unique=False)
    op.create_index(op.f('ix_knowledge_entities_entity_key'), 'knowledge_entities', ['entity_key'], unique=True)

    # 3. Knowledge Relationships
    op.create_table(
        'knowledge_relationships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.95'),
        sa.Column('source_provenance', sa.String(length=255), nullable=False, server_default='SEC EDGAR / Primary Master Data'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['knowledge_entities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'], ['knowledge_entities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_relationships_id'), 'knowledge_relationships', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_relationships_source_id'), 'knowledge_relationships', ['source_id'], unique=False)
    op.create_index(op.f('ix_knowledge_relationships_target_id'), 'knowledge_relationships', ['target_id'], unique=False)
    op.create_index(op.f('ix_knowledge_relationships_relation_type'), 'knowledge_relationships', ['relation_type'], unique=False)

    # 4. Research Hypotheses
    op.create_table(
        'research_hypotheses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('hypothesis_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='UNRESOLVED'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.70'),
        sa.Column('supporting_evidence_json', sa.Text(), nullable=True),
        sa.Column('contradicting_evidence_json', sa.Text(), nullable=True),
        sa.Column('last_evaluated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_hypotheses_id'), 'research_hypotheses', ['id'], unique=False)
    op.create_index(op.f('ix_research_hypotheses_user_id'), 'research_hypotheses', ['user_id'], unique=False)
    op.create_index(op.f('ix_research_hypotheses_symbol'), 'research_hypotheses', ['symbol'], unique=False)

    # 5. Prediction Records
    op.create_table(
        'prediction_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False, server_default='scenario_engine_v1'),
        sa.Column('predicted_metric', sa.String(length=100), nullable=False),
        sa.Column('predicted_min', sa.Float(), nullable=True),
        sa.Column('predicted_max', sa.Float(), nullable=True),
        sa.Column('predicted_value', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.80'),
        sa.Column('actual_observed_value', sa.Float(), nullable=True),
        sa.Column('evaluation_status', sa.String(length=50), nullable=False, server_default='PENDING_OBSERVATION'),
        sa.Column('evaluated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prediction_records_id'), 'prediction_records', ['id'], unique=False)
    op.create_index(op.f('ix_prediction_records_user_id'), 'prediction_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_prediction_records_symbol'), 'prediction_records', ['symbol'], unique=False)

    # 6. User Research Profiles
    op.create_table(
        'user_research_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('researched_symbols_json', sa.Text(), nullable=True),
        sa.Column('researched_sectors_json', sa.Text(), nullable=True),
        sa.Column('topics_json', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_research_profiles_id'), 'user_research_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_user_research_profiles_user_id'), 'user_research_profiles', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_research_profiles_user_id'), table_name='user_research_profiles')
    op.drop_index(op.f('ix_user_research_profiles_id'), table_name='user_research_profiles')
    op.drop_table('user_research_profiles')

    op.drop_index(op.f('ix_prediction_records_symbol'), table_name='prediction_records')
    op.drop_index(op.f('ix_prediction_records_user_id'), table_name='prediction_records')
    op.drop_index(op.f('ix_prediction_records_id'), table_name='prediction_records')
    op.drop_table('prediction_records')

    op.drop_index(op.f('ix_research_hypotheses_symbol'), table_name='research_hypotheses')
    op.drop_index(op.f('ix_research_hypotheses_user_id'), table_name='research_hypotheses')
    op.drop_index(op.f('ix_research_hypotheses_id'), table_name='research_hypotheses')
    op.drop_table('research_hypotheses')

    op.drop_index(op.f('ix_knowledge_relationships_relation_type'), table_name='knowledge_relationships')
    op.drop_index(op.f('ix_knowledge_relationships_target_id'), table_name='knowledge_relationships')
    op.drop_index(op.f('ix_knowledge_relationships_source_id'), table_name='knowledge_relationships')
    op.drop_index(op.f('ix_knowledge_relationships_id'), table_name='knowledge_relationships')
    op.drop_table('knowledge_relationships')

    op.drop_index(op.f('ix_knowledge_entities_entity_key'), table_name='knowledge_entities')
    op.drop_index(op.f('ix_knowledge_entities_entity_type'), table_name='knowledge_entities')
    op.drop_index(op.f('ix_knowledge_entities_id'), table_name='knowledge_entities')
    op.drop_table('knowledge_entities')

    op.drop_index(op.f('ix_agent_execution_metrics_analysis_id'), table_name='agent_execution_metrics')
    op.drop_index(op.f('ix_agent_execution_metrics_task_type'), table_name='agent_execution_metrics')
    op.drop_index(op.f('ix_agent_execution_metrics_agent_name'), table_name='agent_execution_metrics')
    op.drop_index(op.f('ix_agent_execution_metrics_id'), table_name='agent_execution_metrics')
    op.drop_table('agent_execution_metrics')
