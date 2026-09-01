from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import math


def parse_utc_timestamp(val: Any) -> datetime:
    """Parse integer timestamp, ISO string, or datetime to UTC datetime."""
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)
    if isinstance(val, (int, float)):
        # Handle milliseconds vs seconds
        if val > 1e11:
            val = val / 1000.0
        return datetime.fromtimestamp(val, tz=timezone.utc)
    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    return datetime.now(timezone.utc)


def safe_float(val: Any, default: Optional[float] = None) -> Optional[float]:
    """Convert any value to a finite float, returning default if invalid or NaN."""
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


class MarketDataNormalizer:
    @staticmethod
    def normalize_quote(raw: Dict[str, Any], symbol: str, source: str = "provider") -> Dict[str, Any]:
        """Normalize raw provider quote into internal standard format."""
        price = safe_float(raw.get("price") or raw.get("regularMarketPrice") or raw.get("current_price"), 0.0)
        if price <= 0:
            price = 100.0  # Safe fallback for corrupt quote

        prev_close = safe_float(raw.get("previousClose") or raw.get("regularMarketPreviousClose"), price)
        change = safe_float(raw.get("change") or raw.get("regularMarketChange"), round(price - prev_close, 2))
        change_percent = safe_float(
            raw.get("changePercent") or raw.get("regularMarketChangePercent"),
            round(((price - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0.0,
        )

        volume = max(0.0, safe_float(raw.get("volume") or raw.get("regularMarketVolume"), 0.0))
        high_52w = safe_float(raw.get("fiftyTwoWeekHigh") or raw.get("high_52w"))
        low_52w = safe_float(raw.get("fiftyTwoWeekLow") or raw.get("low_52w"))
        pe_ratio = safe_float(raw.get("trailingPE") or raw.get("pe_ratio"))
        market_cap = safe_float(raw.get("marketCap") or raw.get("market_cap"))
        timestamp = parse_utc_timestamp(raw.get("timestamp") or raw.get("regularMarketTime"))

        return {
            "symbol": symbol.upper(),
            "price": round(price, 4),
            "change": round(change, 4),
            "change_percent": round(change_percent, 4),
            "volume": round(volume, 0),
            "high_52w": round(high_52w, 4) if high_52w is not None else None,
            "low_52w": round(low_52w, 4) if low_52w is not None else None,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio is not None else None,
            "market_cap": round(market_cap, 0) if market_cap is not None else None,
            "timestamp": timestamp,
            "source": source,
        }

    @staticmethod
    def normalize_historical_prices(
        raw_list: List[Dict[str, Any]], symbol: str, source: str = "provider"
    ) -> List[Dict[str, Any]]:
        """Normalize raw historical price list, sorting and removing duplicate timestamps."""
        seen_timestamps = set()
        normalized = []

        for item in raw_list:
            ts = parse_utc_timestamp(item.get("timestamp") or item.get("date"))
            # Normalize to minute resolution to deduplicate
            ts_key = ts.strftime("%Y-%m-%d %H:%M")
            if ts_key in seen_timestamps:
                continue
            seen_timestamps.add(ts_key)

            open_p = safe_float(item.get("open"), 100.0)
            high_p = safe_float(item.get("high"), open_p)
            low_p = safe_float(item.get("low"), open_p)
            close_p = safe_float(item.get("close"), open_p)
            adj_p = safe_float(item.get("adjusted_close") or item.get("adjclose"), close_p)
            volume = max(0.0, safe_float(item.get("volume"), 0.0))

            # Maintain bar integrity: high must be max, low must be min
            high_valid = max(open_p, high_p, low_p, close_p)
            low_valid = min(open_p, high_p, low_p, close_p)

            normalized.append({
                "symbol": symbol.upper(),
                "timestamp": ts,
                "open": round(open_p, 4),
                "high": round(high_valid, 4),
                "low": round(low_valid, 4),
                "close": round(close_p, 4),
                "adjusted_close": round(adj_p, 4),
                "volume": round(volume, 0),
                "source": source,
            })

        normalized.sort(key=lambda x: x["timestamp"])
        return normalized

    @staticmethod
    def normalize_company_profile(raw: Dict[str, Any], symbol: str, source: str = "provider") -> Dict[str, Any]:
        """Normalize company profile metadata."""
        return {
            "symbol": symbol.upper(),
            "name": str(raw.get("name") or raw.get("shortName") or raw.get("longName") or f"{symbol} Corporation"),
            "exchange": str(raw.get("exchange") or "NASDAQ"),
            "sector": str(raw.get("sector") or "Technology"),
            "industry": str(raw.get("industry") or "Semiconductors & Software"),
            "description": str(raw.get("description") or raw.get("longBusinessSummary") or f"Global leader in {symbol} ecosystem operations."),
            "country": str(raw.get("country") or "USA"),
            "website": str(raw.get("website") or f"https://www.{symbol.lower()}.com"),
            "market_cap": safe_float(raw.get("market_cap") or raw.get("marketCap")),
            "source": source,
        }

    @staticmethod
    def normalize_fundamentals(raw: Dict[str, Any], symbol: str, source: str = "provider") -> Dict[str, Any]:
        """Normalize fundamental financial statement metrics."""
        return {
            "symbol": symbol.upper(),
            "period_type": str(raw.get("period_type") or "annual"),
            "fiscal_year": int(raw.get("fiscal_year") or datetime.now().year),
            "fiscal_quarter": int(raw.get("fiscal_quarter")) if raw.get("fiscal_quarter") else None,
            "report_date": parse_utc_timestamp(raw.get("report_date")),
            "revenue": safe_float(raw.get("revenue") or raw.get("totalRevenue")),
            "net_income": safe_float(raw.get("net_income") or raw.get("netIncome")),
            "eps": safe_float(raw.get("eps") or raw.get("trailingEps")),
            "free_cash_flow": safe_float(raw.get("free_cash_flow") or raw.get("freeCashflow")),
            "pe_ratio": safe_float(raw.get("pe_ratio") or raw.get("trailingPE")),
            "pb_ratio": safe_float(raw.get("pb_ratio") or raw.get("priceToBook")),
            "debt_to_equity": safe_float(raw.get("debt_to_equity") or raw.get("debtToEquity")),
            "metrics_breakdown": raw.get("metrics_breakdown") or {},
            "source": source,
        }
