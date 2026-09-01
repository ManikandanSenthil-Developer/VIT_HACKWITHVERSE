from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    asset_type = Column(String(50), default="Stock")  # Stock, ETF, Crypto, Bond, Commodity
    quantity = Column(Float, default=0.0, nullable=False)
    buy_price = Column(Float, default=0.0, nullable=False)
    current_value = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
