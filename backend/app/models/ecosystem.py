from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class UserAccessibilityPreference(Base):
    """
    Persists user accessibility, language, and voice interaction preferences.
    Ensures an inclusive experience across web sessions.
    """
    __tablename__ = "user_accessibility_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    language = Column(String(10), default="en", nullable=False)  # "en", "ta", "hi", etc.
    text_size = Column(String(20), default="normal", nullable=False)  # "normal", "large", "extra_large"
    reduced_motion = Column(Boolean, default=False, nullable=False)
    high_contrast = Column(Boolean, default=False, nullable=False)
    voice_enabled = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", backref="accessibility_preference")


class UserFeedback(Base):
    """
    Collects user feedback ('Helpful' / 'Not Helpful' votes and optional comments)
    for AI analyses, alerts, and research theses to power quality monitoring.
    """
    __tablename__ = "user_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(String(50), nullable=False, index=True)  # COPILOT_MESSAGE, ALERT, ANALYSIS, THESIS
    target_id = Column(String(100), nullable=False, index=True)
    is_helpful = Column(Boolean, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", backref="feedbacks")


class BrokerConnection(Base):
    """
    Mock external brokerage connection (e.g. Zerodha, Interactive Brokers sandbox).
    Strictly enforced as READ-ONLY by architecture; trade execution is completely prohibited.
    """
    __tablename__ = "broker_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    broker_name = Column(String(100), default="Demo Broker (Paper/Mock)", nullable=False)
    account_id = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_read_only = Column(Boolean, default=True, nullable=False)  # Immutable: ALWAYS True
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", backref="broker_connections")
