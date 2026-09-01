from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class CopilotConversation(Base):
    __tablename__ = "copilot_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Research Session")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    messages = relationship("CopilotMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="CopilotMessage.created_at")


class CopilotMessage(Base):
    __tablename__ = "copilot_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("copilot_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)  # e.g. 'PORTFOLIO_ANALYSIS', 'COMPARISON', etc.
    tool_calls_json = Column(Text, nullable=True)  # JSON array of tools invoked
    tool_results_json = Column(Text, nullable=True)  # JSON dictionary of tool findings
    citations_json = Column(Text, nullable=True)  # JSON array of citations
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    conversation = relationship("CopilotConversation", back_populates="messages")


class DecisionJournalEntry(Base):
    __tablename__ = "decision_journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    thesis_title = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    risk_assessment = Column(Text, nullable=True)
    confidence = Column(Float, default=0.8, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE", nullable=False)  # 'ACTIVE', 'SUPPORTED', 'PARTIALLY_SUPPORTED', 'CONTRADICTED'
    last_reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ResearchThesis(Base):
    __tablename__ = "research_theses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    bull_case_json = Column(Text, nullable=False)  # JSON array of points
    bear_case_json = Column(Text, nullable=False)  # JSON array of points
    counterarguments_json = Column(Text, nullable=False)  # JSON array from Devil's Advocate
    invalidation_conditions_json = Column(Text, nullable=False)  # JSON array
    what_to_monitor_json = Column(Text, nullable=False)  # JSON array
    evidence_citations_json = Column(Text, nullable=False)  # JSON array
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
