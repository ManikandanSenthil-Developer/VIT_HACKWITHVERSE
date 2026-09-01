from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class AgentExecutionMetric(Base):
    """
    Empirical agent telemetry record.
    Tracks execution latency, evidence counts, confidence, and empirical success/failure status.
    Measures computational availability, not predictive investment accuracy.
    """
    __tablename__ = "agent_execution_metrics"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(50), nullable=False, index=True)  # technical, fundamental, sentiment, rag, counterargument, risk
    analysis_id = Column(String(100), nullable=True, index=True)
    task_type = Column(String(100), nullable=False, index=True)
    execution_time_ms = Column(Float, nullable=False, default=0.0)
    evidence_count = Column(Integer, nullable=False, default=0)
    confidence = Column(Float, nullable=False, default=0.85)
    status = Column(String(20), nullable=False, default="SUCCESS")  # SUCCESS, FAILURE, FALLBACK
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class KnowledgeEntity(Base):
    """
    Nodes in the financial knowledge graph.
    Represents companies, sectors, industries, events, documents, metrics, portfolios, and alerts.
    """
    __tablename__ = "knowledge_entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # COMPANY, SECTOR, INDUSTRY, EVENT, DOCUMENT, METRIC, PORTFOLIO, ALERT
    entity_key = Column(String(100), unique=True, nullable=False, index=True)  # e.g. "COMPANY:NVDA", "SECTOR:TECH"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class KnowledgeRelationship(Base):
    """
    Evidence-backed edges connecting knowledge entities.
    Must always track source provenance and confidence; never created from ungrounded imagination.
    """
    __tablename__ = "knowledge_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("knowledge_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("knowledge_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(50), nullable=False, index=True)  # BELONGS_TO, COMPETES_WITH, AFFECTED_BY, MENTIONED_IN, SUPPORTS, CONTRIBUTES_TO, CONTAINS
    confidence = Column(Float, default=0.95, nullable=False)
    source_provenance = Column(String(255), default="SEC EDGAR / Primary Master Data", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    source = relationship("KnowledgeEntity", foreign_keys=[source_id], backref="outgoing_relations")
    target = relationship("KnowledgeEntity", foreign_keys=[target_id], backref="incoming_relations")


class ResearchHypothesis(Base):
    """
    User research hypothesis with dynamic evidence tracking.
    Evaluates evidence lifecycle without forcing conclusions when data is insufficient.
    """
    __tablename__ = "research_hypotheses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    hypothesis_text = Column(Text, nullable=False)
    status = Column(String(50), default="UNRESOLVED", nullable=False)  # SUPPORTED, PARTIALLY_SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE, UNRESOLVED
    confidence = Column(Float, default=0.70, nullable=False)
    supporting_evidence_json = Column(Text, nullable=True)  # List of supporting evidence strings
    contradicting_evidence_json = Column(Text, nullable=True)  # List of contradicting evidence strings
    last_evaluated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", backref="hypotheses")


class PredictionRecord(Base):
    """
    Prediction journal entry recording model estimates and confidence.
    Enables subsequent retrospective evaluation against actual observed outcomes.
    Never alters historical predictions with hindsight.
    """
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    model_name = Column(String(100), nullable=False, default="scenario_engine_v1")
    predicted_metric = Column(String(100), nullable=False)  # e.g. "price_1mo", "operating_margin"
    predicted_min = Column(Float, nullable=True)
    predicted_max = Column(Float, nullable=True)
    predicted_value = Column(Float, nullable=True)
    confidence = Column(Float, nullable=False, default=0.80)
    actual_observed_value = Column(Float, nullable=True)
    evaluation_status = Column(String(50), default="PENDING_OBSERVATION", nullable=False)  # PENDING_OBSERVATION, WITHIN_RANGE, OUTSIDE_RANGE, EVALUATED
    evaluated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", backref="prediction_records")


class UserResearchProfile(Base):
    """
    Stores non-sensitive user research interests (symbols, sectors, topics)
    to power personalized 'FOR YOU' intelligence feeds.
    Strictly prohibits tracking religion, politics, health, or sensitive attributes.
    """
    __tablename__ = "user_research_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    researched_symbols_json = Column(Text, nullable=True)  # Dict[symbol, count]
    researched_sectors_json = Column(Text, nullable=True)  # Dict[sector, count]
    topics_json = Column(Text, nullable=True)              # Dict[topic, count]
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", backref="research_profile", uselist=False)
