from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    request_id = Column(String(64), unique=True, index=True, nullable=False)
    query = Column(Text, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    analysis_type = Column(String(50), default="comprehensive")
    
    # Synthesis results
    overall_assessment = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    recommendation_json = Column(Text, nullable=False)
    
    # Multi-agent breakdown
    agents_consulted_json = Column(Text, nullable=False)
    findings_json = Column(Text, nullable=False)
    conflicts_json = Column(Text, nullable=False)
    
    # Audit & Provenance
    reasoning_trace_json = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=False)
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_analysis_user_symbol", "user_id", "symbol"),
    )

    # Relationships
    user = relationship("User", back_populates="analyses")
