from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class MarketDataProvider(ABC):
    """Abstract interface for external/internal financial market data providers."""

    @abstractmethod
    async def get_raw_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch real-time or delayed quote data for a symbol."""
        pass

    @abstractmethod
    async def get_raw_historical_prices(self, symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
        """Fetch historical price bars for a symbol."""
        pass

    @abstractmethod
    async def get_raw_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Fetch company identity, exchange, and overview metadata."""
        pass

    @abstractmethod
    async def get_raw_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial statement metrics and fundamental ratios."""
        pass
