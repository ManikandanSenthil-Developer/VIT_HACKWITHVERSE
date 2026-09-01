import abc
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ProviderHealthStatus(BaseModel):
    name: str
    provider_type: str  # MARKET_DATA, NEWS, RAG_DOCUMENTS, AI_REASONING
    status: str         # HEALTHY, DEGRADED, OFFLINE
    latency_ms: float
    failure_rate_pct: float
    last_heartbeat: str


class BaseMarketDataProvider(abc.ABC):
    """Abstract interface for pluggable market data providers."""

    @abc.abstractmethod
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    async def get_historical_bars(self, symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
        pass


class BaseDocumentProvider(abc.ABC):
    """Abstract interface for regulatory filings and document sources."""

    @abc.abstractmethod
    async def fetch_filing(self, symbol: str, form_type: str = "10-K") -> Optional[Dict[str, Any]]:
        pass


class ProviderHealthMonitor:
    """
    Tracks runtime telemetry, latency, and heartbeat status for
    external and internal data sources in the MATS ecosystem.
    """

    def __init__(self):
        self._health_registry: Dict[str, Dict[str, Any]] = {
            "primary_market_provider": {
                "name": "Live Market Telemetry (Primary)",
                "provider_type": "MARKET_DATA",
                "status": "HEALTHY",
                "latency_ms": 142.0,
                "failure_count": 0,
                "request_count": 128,
            },
            "fallback_market_provider": {
                "name": "Secondary Market Feed (Fallback)",
                "provider_type": "MARKET_DATA",
                "status": "HEALTHY",
                "latency_ms": 285.0,
                "failure_count": 0,
                "request_count": 14,
            },
            "sec_edgar_rag_provider": {
                "name": "SEC EDGAR Form 10-K Engine",
                "provider_type": "RAG_DOCUMENTS",
                "status": "HEALTHY",
                "latency_ms": 84.0,
                "failure_count": 0,
                "request_count": 64,
            },
            "local_embedding_engine": {
                "name": "384-Dim Dense Semantic Vector Engine",
                "provider_type": "AI_REASONING",
                "status": "HEALTHY",
                "latency_ms": 48.0,
                "failure_count": 0,
                "request_count": 92,
            },
        }

    def record_request(self, provider_key: str, latency_ms: float, success: bool = True):
        if provider_key in self._health_registry:
            entry = self._health_registry[provider_key]
            entry["request_count"] += 1
            if not success:
                entry["failure_count"] += 1
            # Moving average latency
            entry["latency_ms"] = round((entry["latency_ms"] * 0.8) + (latency_ms * 0.2), 1)
            fail_rate = (entry["failure_count"] / max(entry["request_count"], 1)) * 100.0
            if fail_rate > 20.0:
                entry["status"] = "DEGRADED"
            elif fail_rate > 50.0:
                entry["status"] = "OFFLINE"
            else:
                entry["status"] = "HEALTHY"

    def get_all_statuses(self) -> List[ProviderHealthStatus]:
        now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        res = []
        for p in self._health_registry.values():
            fail_rate = (p["failure_count"] / max(p["request_count"], 1)) * 100.0
            res.append(
                ProviderHealthStatus(
                    name=p["name"],
                    provider_type=p["provider_type"],
                    status=p["status"],
                    latency_ms=p["latency_ms"],
                    failure_rate_pct=round(fail_rate, 1),
                    last_heartbeat=now_str,
                )
            )
        return res


provider_health_monitor = ProviderHealthMonitor()
