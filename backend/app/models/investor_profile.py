from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class InvestorProfile(Base):
    __tablename__ = "investor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Investor attributes
    risk_tolerance = Column(String(50), default="moderate")  # conservative, moderate, aggressive, speculative
    investment_horizon = Column(String(50), default="medium")  # short (<1yr), medium (1-5yr), long (5+yr)
    preferred_sectors = Column(String(255), default="Technology,Healthcare,Clean Energy")
    target_return = Column(Float, default=12.0)  # annual percentage target
    experience_level = Column(String(50), default="intermediate")  # beginner, intermediate, advanced, professional
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")
