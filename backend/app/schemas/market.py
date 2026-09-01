from datetime import datetime
from typing import Generic, List, Optional, TypeVar, Dict, Any
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class MarketResponseWrapper(BaseModel, Generic[T]):
    """Standard container guaranteeing traceability and data freshness status."""
    data: T
    source: str
    retrieved_at: datetime
    fresh: bool
    cached: bool = False
    status_note: Optional[str] = None


class MarketQuoteData(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: float
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class PricePoint(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float
    volume: float

    model_config = ConfigDict(from_attributes=True)


class HistoricalPriceData(BaseModel):
    symbol: str
    period: str  # 1d, 5d, 1mo, 3mo, 6mo, 1y
    count: int
    prices: List[PricePoint]


class CompanyProfileData(BaseModel):
    symbol: str
    name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = "USA"
    website: Optional[str] = None
    market_cap: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class FundamentalDataMetric(BaseModel):
    symbol: str
    period_type: str
    fiscal_year: Optional[int] = None
    fiscal_quarter: Optional[int] = None
    report_date: Optional[datetime] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    free_cash_flow: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    metrics_breakdown: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


MarketQuoteResponse = MarketResponseWrapper[MarketQuoteData]
HistoricalPriceResponse = MarketResponseWrapper[HistoricalPriceData]
CompanyProfileResponse = MarketResponseWrapper[CompanyProfileData]
FundamentalResponse = MarketResponseWrapper[FundamentalDataMetric]
