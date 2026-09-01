import pytest
from app.services.market.normalizer import MarketDataNormalizer


def test_quote_normalization():
    raw_payload = {
        "regularMarketPrice": 128.45,
        "regularMarketPreviousClose": 125.00,
        "regularMarketVolume": 45000000,
        "regularMarketTime": "2026-09-01T12:00:00Z",
        "fiftyTwoWeekHigh": 140.0,
        "fiftyTwoWeekLow": 80.0,
        "trailingPE": 64.2,
        "marketCap": 3100000000000,
    }
    normalized = MarketDataNormalizer.normalize_quote(raw_payload, symbol="NVDA", source="test_provider")
    assert normalized["symbol"] == "NVDA"
    assert normalized["price"] == 128.45
    assert normalized["change"] == 3.45
    assert normalized["change_percent"] == 2.76
    assert normalized["volume"] == 45000000
    assert normalized["source"] == "test_provider"


def test_quote_normalization_with_corrupt_nulls():
    corrupt_payload = {
        "price": None,
        "change": None,
        "volume": -500,  # Invalid negative volume
        "timestamp": None,
    }
    normalized = MarketDataNormalizer.normalize_quote(corrupt_payload, symbol="AAPL", source="fallback")
    assert normalized["symbol"] == "AAPL"
    assert normalized["price"] > 0
    assert normalized["volume"] == 0.0  # Normalized to non-negative
    assert normalized["timestamp"] is not None


def test_historical_price_normalization_ordering_and_dedup():
    raw_bars = [
        {"date": "2026-08-02T16:00:00Z", "open": 102, "high": 105, "low": 101, "close": 104, "volume": 1000},
        {"date": "2026-08-01T16:00:00Z", "open": 100, "high": 103, "low": 99, "close": 102, "volume": 1200},
        {"date": "2026-08-01T16:00:00Z", "open": 100, "high": 103, "low": 99, "close": 102, "volume": 1200},  # Duplicate
    ]
    bars = MarketDataNormalizer.normalize_historical_prices(raw_bars, symbol="MSFT")
    assert len(bars) == 2
    # Ensure chronological sort
    assert bars[0]["timestamp"] < bars[1]["timestamp"]
    assert bars[0]["high"] >= bars[0]["low"]


def test_market_quote_api_flow(client):
    # First call: fetches from provider & caches
    res = client.get("/api/v1/market/quote/NVDA")
    assert res.status_code == 200
    data = res.json()
    assert data["data"]["symbol"] == "NVDA"
    assert data["fresh"] is True
    assert "source" in data
    assert data["data"]["price"] > 0

    # Second immediate call: should be served from short-lived cache
    res_cached = client.get("/api/v1/market/quote/NVDA")
    assert res_cached.status_code == 200
    assert res_cached.json()["cached"] is True


def test_market_history_api(client):
    res = client.get("/api/v1/market/history/AAPL?period=1mo")
    assert res.status_code == 200
    data = res.json()
    assert data["data"]["symbol"] == "AAPL"
    assert data["data"]["count"] > 0
    assert len(data["data"]["prices"]) > 0


def test_company_and_fundamentals_api(client):
    c_res = client.get("/api/v1/market/company/MSFT")
    assert c_res.status_code == 200
    assert c_res.json()["data"]["symbol"] == "MSFT"

    f_res = client.get("/api/v1/market/fundamentals/MSFT")
    assert f_res.status_code == 200
    assert f_res.json()["data"]["symbol"] == "MSFT"
    assert f_res.json()["data"]["revenue"] > 0
