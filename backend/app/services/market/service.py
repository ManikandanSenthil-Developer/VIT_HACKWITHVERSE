from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security_validation import sanitize_symbol
from app.models.market import Company, Security, PriceHistory, MarketSnapshot, FundamentalData
from app.services.cache.cache_service import cache_service
from app.services.market.normalizer import MarketDataNormalizer
from app.services.market.provider import HybridMarketDataProvider
from app.schemas.market import (
    MarketQuoteResponse,
    MarketQuoteData,
    HistoricalPriceResponse,
    HistoricalPriceData,
    PricePoint,
    CompanyProfileResponse,
    CompanyProfileData,
    FundamentalResponse,
    FundamentalDataMetric,
)


class MarketService:
    def __init__(self, provider=None):
        self.provider = provider or HybridMarketDataProvider()

    def _ensure_security(self, db: Session, symbol: str) -> Security:
        """Helper to ensure Company and Security entities exist in DB."""
        security = db.query(Security).filter(Security.symbol == symbol).first()
        if not security:
            company = db.query(Company).filter(Company.symbol == symbol).first()
            if not company:
                company = Company(
                    symbol=symbol,
                    name=f"{symbol} Corporation",
                    exchange="NASDAQ",
                    sector="Technology",
                )
                db.add(company)
                db.commit()
                db.refresh(company)

            security = Security(
                company_id=company.id,
                symbol=symbol,
                name=company.name,
                security_type="Common Stock",
                currency="USD",
                is_active=True,
            )
            db.add(security)
            db.commit()
            db.refresh(security)
        return security

    async def get_quote(self, db: Session, symbol: str) -> MarketQuoteResponse:
        sym = sanitize_symbol(symbol)
        cache_key = f"quote:{sym}"

        # 1. Check in-memory cache
        cached = cache_service.get(cache_key, allow_stale=False)
        if cached:
            val, ret_at, src, fresh = cached
            return MarketQuoteResponse(
                data=MarketQuoteData(**val),
                source=src,
                retrieved_at=ret_at,
                fresh=fresh,
                cached=True,
            )

        # 2. Query provider
        try:
            raw = await self.provider.get_raw_quote(sym)
            source = raw.get("_source", "provider")
            normalized = MarketDataNormalizer.normalize_quote(raw, sym, source=source)
            retrieved_at = datetime.now(timezone.utc)

            # Persist to database (MarketSnapshot)
            security = self._ensure_security(db, sym)
            snapshot = db.query(MarketSnapshot).filter(MarketSnapshot.security_id == security.id).first()
            if not snapshot:
                snapshot = MarketSnapshot(
                    security_id=security.id,
                    symbol=sym,
                    price=normalized["price"],
                    change=normalized["change"],
                    change_percent=normalized["change_percent"],
                    volume=normalized["volume"],
                    high_52w=normalized["high_52w"],
                    low_52w=normalized["low_52w"],
                    pe_ratio=normalized["pe_ratio"],
                    market_cap=normalized["market_cap"],
                    timestamp=normalized["timestamp"],
                    source=source,
                    is_fresh=True,
                    retrieved_at=retrieved_at,
                )
                db.add(snapshot)
            else:
                snapshot.price = normalized["price"]
                snapshot.change = normalized["change"]
                snapshot.change_percent = normalized["change_percent"]
                snapshot.volume = normalized["volume"]
                snapshot.high_52w = normalized["high_52w"]
                snapshot.low_52w = normalized["low_52w"]
                snapshot.pe_ratio = normalized["pe_ratio"]
                snapshot.market_cap = normalized["market_cap"]
                snapshot.timestamp = normalized["timestamp"]
                snapshot.source = source
                snapshot.is_fresh = True
                snapshot.retrieved_at = retrieved_at

            db.commit()

            # Store in cache
            cache_service.set(cache_key, normalized, ttl_seconds=settings.CACHE_QUOTE_TTL_SECONDS, source=source)

            return MarketQuoteResponse(
                data=MarketQuoteData(**normalized),
                source=source,
                retrieved_at=retrieved_at,
                fresh=True,
                cached=False,
            )

        except Exception as e:
            # 3. Degraded mode fallback: Check DB for last known snapshot
            security = db.query(Security).filter(Security.symbol == sym).first()
            if security and security.snapshot:
                snap = security.snapshot
                return MarketQuoteResponse(
                    data=MarketQuoteData(
                        symbol=sym,
                        price=snap.price,
                        change=snap.change,
                        change_percent=snap.change_percent,
                        volume=snap.volume,
                        high_52w=snap.high_52w,
                        low_52w=snap.low_52w,
                        pe_ratio=snap.pe_ratio,
                        market_cap=snap.market_cap,
                        timestamp=snap.timestamp,
                    ),
                    source=snap.source,
                    retrieved_at=snap.retrieved_at,
                    fresh=False,
                    cached=True,
                    status_note="LIVE MARKET DATA UNAVAILABLE: Showing last successfully retrieved snapshot.",
                )

            # Re-raise if no data exists at all
            raise e

    async def get_historical_prices(self, db: Session, symbol: str, period: str = "1mo") -> HistoricalPriceResponse:
        sym = sanitize_symbol(symbol)
        cache_key = f"history:{sym}:{period}"

        cached = cache_service.get(cache_key, allow_stale=False)
        if cached:
            val, ret_at, src, fresh = cached
            return HistoricalPriceResponse(
                data=HistoricalPriceData(
                    symbol=sym,
                    period=period,
                    count=len(val),
                    prices=[PricePoint(**p) for p in val],
                ),
                source=src,
                retrieved_at=ret_at,
                fresh=fresh,
                cached=True,
            )

        raw_list = await self.provider.get_raw_historical_prices(sym, period=period)
        source = raw_list[0].get("_source", "provider") if raw_list else "provider"
        normalized = MarketDataNormalizer.normalize_historical_prices(raw_list, sym, source=source)
        retrieved_at = datetime.now(timezone.utc)

        # Persist bars into PriceHistory table
        security = self._ensure_security(db, sym)
        for bar in normalized:
            existing = (
                db.query(PriceHistory)
                .filter(PriceHistory.symbol == sym, PriceHistory.timestamp == bar["timestamp"])
                .first()
            )
            if not existing:
                ph = PriceHistory(
                    security_id=security.id,
                    symbol=sym,
                    timestamp=bar["timestamp"],
                    open=bar["open"],
                    high=bar["high"],
                    low=bar["low"],
                    close=bar["close"],
                    adjusted_close=bar["adjusted_close"],
                    volume=bar["volume"],
                    source=source,
                )
                db.add(ph)
        db.commit()

        cache_service.set(cache_key, normalized, ttl_seconds=settings.CACHE_HISTORY_TTL_SECONDS, source=source)

        return HistoricalPriceResponse(
            data=HistoricalPriceData(
                symbol=sym,
                period=period,
                count=len(normalized),
                prices=[PricePoint(**p) for p in normalized],
            ),
            source=source,
            retrieved_at=retrieved_at,
            fresh=True,
            cached=False,
        )

    async def get_company_profile(self, db: Session, symbol: str) -> CompanyProfileResponse:
        sym = sanitize_symbol(symbol)
        cache_key = f"company:{sym}"

        cached = cache_service.get(cache_key, allow_stale=False)
        if cached:
            val, ret_at, src, fresh = cached
            return CompanyProfileResponse(
                data=CompanyProfileData(**val),
                source=src,
                retrieved_at=ret_at,
                fresh=fresh,
                cached=True,
            )

        raw = await self.provider.get_raw_company_profile(sym)
        source = raw.get("_source", "provider")
        normalized = MarketDataNormalizer.normalize_company_profile(raw, sym, source=source)
        retrieved_at = datetime.now(timezone.utc)

        # Update or create Company in DB
        company = db.query(Company).filter(Company.symbol == sym).first()
        if not company:
            company = Company(
                symbol=sym,
                name=normalized["name"],
                exchange=normalized["exchange"],
                sector=normalized["sector"],
                industry=normalized["industry"],
                description=normalized["description"],
                country=normalized["country"],
                website=normalized["website"],
                market_cap=normalized["market_cap"],
                source=source,
            )
            db.add(company)
        else:
            company.name = normalized["name"]
            company.exchange = normalized["exchange"]
            company.sector = normalized["sector"]
            company.industry = normalized["industry"]
            company.description = normalized["description"]
            company.country = normalized["country"]
            company.website = normalized["website"]
            company.market_cap = normalized["market_cap"]
            company.source = source
        db.commit()

        cache_service.set(cache_key, normalized, ttl_seconds=settings.CACHE_COMPANY_TTL_SECONDS, source=source)

        return CompanyProfileResponse(
            data=CompanyProfileData(**normalized),
            source=source,
            retrieved_at=retrieved_at,
            fresh=True,
            cached=False,
        )

    async def get_fundamentals(self, db: Session, symbol: str) -> FundamentalResponse:
        sym = sanitize_symbol(symbol)
        cache_key = f"fundamentals:{sym}"

        cached = cache_service.get(cache_key, allow_stale=False)
        if cached:
            val, ret_at, src, fresh = cached
            return FundamentalResponse(
                data=FundamentalDataMetric(**val),
                source=src,
                retrieved_at=ret_at,
                fresh=fresh,
                cached=True,
            )

        raw = await self.provider.get_raw_fundamentals(sym)
        source = raw.get("_source", "provider")
        normalized = MarketDataNormalizer.normalize_fundamentals(raw, sym, source=source)
        retrieved_at = datetime.now(timezone.utc)

        # Store in DB
        company = db.query(Company).filter(Company.symbol == sym).first()
        if not company:
            company = Company(symbol=sym, name=f"{sym} Corporation")
            db.add(company)
            db.commit()
            db.refresh(company)

        fund = FundamentalData(
            company_id=company.id,
            symbol=sym,
            period_type=normalized["period_type"],
            fiscal_year=normalized["fiscal_year"],
            fiscal_quarter=normalized["fiscal_quarter"],
            report_date=normalized["report_date"],
            revenue=normalized["revenue"],
            net_income=normalized["net_income"],
            eps=normalized["eps"],
            free_cash_flow=normalized["free_cash_flow"],
            pe_ratio=normalized["pe_ratio"],
            pb_ratio=normalized["pb_ratio"],
            debt_to_equity=normalized["debt_to_equity"],
            metrics_json=json.dumps(normalized["metrics_breakdown"]),
            source=source,
            retrieved_at=retrieved_at,
        )
        db.add(fund)
        db.commit()

        cache_service.set(cache_key, normalized, ttl_seconds=settings.CACHE_FUNDAMENTALS_TTL_SECONDS, source=source)

        return FundamentalResponse(
            data=FundamentalDataMetric(**normalized),
            source=source,
            retrieved_at=retrieved_at,
            fresh=True,
            cached=False,
        )


market_service = MarketService()
