from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.market import (
    MarketQuoteResponse,
    HistoricalPriceResponse,
    CompanyProfileResponse,
    FundamentalResponse,
)
from app.services.market.service import market_service

router = APIRouter()


@router.get("/quote/{symbol}", response_model=MarketQuoteResponse)
async def get_market_quote(
    symbol: str,
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve normalized real-time/cached market quote with data freshness metadata."""
    return await market_service.get_quote(db, symbol=symbol)


@router.get("/history/{symbol}", response_model=HistoricalPriceResponse)
async def get_market_history(
    symbol: str,
    period: str = Query(default="1mo", pattern="^(1d|5d|1mo|3mo|6mo|1y)$"),
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve normalized historical OHLCV price series for charting."""
    return await market_service.get_historical_prices(db, symbol=symbol, period=period)


@router.get("/company/{symbol}", response_model=CompanyProfileResponse)
async def get_company_profile(
    symbol: str,
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve verified company overview, exchange, and industry classification."""
    return await market_service.get_company_profile(db, symbol=symbol)


@router.get("/fundamentals/{symbol}", response_model=FundamentalResponse)
async def get_fundamentals(
    symbol: str,
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve verified financial ratios and fundamental balance sheet metrics."""
    return await market_service.get_fundamentals(db, symbol=symbol)
