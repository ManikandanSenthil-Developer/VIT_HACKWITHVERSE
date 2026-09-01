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
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    exchange = Column(String(50), default="NASDAQ")
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    country = Column(String(50), default="USA")
    website = Column(String(255), nullable=True)
    market_cap = Column(Float, nullable=True)
    source = Column(String(50), default="provider")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    securities = relationship("Security", back_populates="company", cascade="all, delete-orphan")
    fundamentals = relationship("FundamentalData", back_populates="company", cascade="all, delete-orphan")


class Security(Base):
    __tablename__ = "securities"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    security_type = Column(String(50), default="Common Stock")  # Common Stock, ETF, ADR
    currency = Column(String(10), default="USD")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    company = relationship("Company", back_populates="securities")
    price_history = relationship("PriceHistory", back_populates="security", cascade="all, delete-orphan")
    snapshot = relationship("MarketSnapshot", back_populates="security", uselist=False, cascade="all, delete-orphan")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(Integer, ForeignKey("securities.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adjusted_close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    source = Column(String(50), default="provider")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "timestamp", name="uq_symbol_timestamp"),
        Index("ix_price_history_symbol_timestamp", "symbol", "timestamp"),
    )

    # Relationships
    security = relationship("Security", back_populates="price_history")


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(Integer, ForeignKey("securities.id", ondelete="CASCADE"), unique=True, nullable=False)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    change = Column(Float, default=0.0)
    change_percent = Column(Float, default=0.0)
    volume = Column(Float, default=0.0)
    high_52w = Column(Float, nullable=True)
    low_52w = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    source = Column(String(50), default="provider")
    is_fresh = Column(Boolean, default=True)
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    security = relationship("Security", back_populates="snapshot")


class FundamentalData(Base):
    __tablename__ = "fundamental_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    period_type = Column(String(20), default="annual")  # annual, quarterly, ttm
    fiscal_year = Column(Integer, nullable=True)
    fiscal_quarter = Column(Integer, nullable=True)
    report_date = Column(DateTime, nullable=True)
    
    # Financial metrics
    revenue = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)
    free_cash_flow = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    metrics_json = Column(Text, nullable=True)  # Extensible JSON for custom ratios/breakdowns
    source = Column(String(50), default="provider")
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_fundamental_symbol_period", "symbol", "period_type", "fiscal_year"),
    )

    # Relationships
    company = relationship("Company", back_populates="fundamentals")
