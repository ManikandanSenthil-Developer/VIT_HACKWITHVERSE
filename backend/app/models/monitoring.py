from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class MarketEvent(Base):
    __tablename__ = "market_events"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)
    event_type = Column(String(50), index=True, nullable=False)  # PRICE_ANOMALY, VOLUME_SURGE, VOLATILITY_SPIKE, REGULATORY_FILING
    severity = Column(String(20), default="MEDIUM", nullable=False)  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=True)
    source = Column(String(100), default="market_surveillance", nullable=False)
    confidence = Column(Float, default=0.8, nullable=False)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    # Relationships
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("market_events.id", ondelete="SET NULL"), nullable=True)
    symbol = Column(String(20), index=True, nullable=False)
    priority = Column(String(20), default="IMPORTANT", index=True, nullable=False)  # URGENT, IMPORTANT, FYI
    severity = Column(String(20), default="MEDIUM", nullable=False)  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    title = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    agent_synthesis_json = Column(Text, nullable=True)  # Full multi-agent reasoning trace, agents consulted, findings
    status = Column(String(30), default="NEW", index=True, nullable=False)  # NEW, SEEN, ACKNOWLEDGED, DISMISSED, RESOLVED
    feedback = Column(String(30), default="UNSPECIFIED", nullable=False)  # HELPFUL, NOT_HELPFUL, UNSPECIFIED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    seen_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="alerts")
    event = relationship("MarketEvent", back_populates="alerts")


class ScenarioRun(Base):
    __tablename__ = "scenario_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    scenario_type = Column(String(50), nullable=False)  # HOLDING_SHOCK, SECTOR_SHOCK, POSITION_REBALANCE
    parameters_json = Column(Text, nullable=False)
    impact_summary_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="scenarios")
    portfolio = relationship("Portfolio")


class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_type = Column(String(50), default="scheduled", nullable=False)  # scheduled, manual, demo
    status = Column(String(30), default="completed", nullable=False)  # completed, failed
    events_detected = Column(Integer, default=0, nullable=False)
    alerts_created = Column(Integer, default=0, nullable=False)
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
