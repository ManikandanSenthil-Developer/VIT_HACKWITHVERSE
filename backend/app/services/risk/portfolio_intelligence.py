from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from app.models.holding import Holding
from app.models.portfolio import Portfolio
from app.models.watchlist import Watchlist
from app.models.market import Company
from app.schemas.risk import PositionHealth, SectorExposure
from app.services.market.service import market_service


SECTOR_MAP = {
    "NVDA": "Semiconductors & AI Hardware",
    "AAPL": "Consumer Technology & Services",
    "MSFT": "Cloud & Enterprise Software",
    "TSLA": "Automotive & Clean Energy",
    "AMZN": "E-Commerce & Cloud Infrastructure",
    "GOOGL": "Digital Media & Cloud Services",
    "META": "Social Platforms & Metaverse",
    "HDFCBANK": "Banking & Financial Services",
    "RELIANCE": "Energy & Conglomerate",
    "TCS": "IT Services & Consulting",
    "INFY": "IT Services & Software",
}


class PortfolioIntelligenceService:
    """
    Computes deterministic, factual portfolio-level intelligence.
    Aggregates real-time P/L, position weights, sector exposure distributions,
    and asset concentration without hallucinating values.
    """

    @staticmethod
    async def evaluate_portfolio(
        db: Session,
        portfolio: Portfolio,
    ) -> Tuple[List[PositionHealth], List[SectorExposure], Dict[str, float]]:
        holdings: List[Holding] = portfolio.holdings or []
        positions: List[PositionHealth] = []
        sector_totals: Dict[str, float] = {}

        total_holdings_value = 0.0
        total_invested = 0.0

        # 1. Fetch live quotes and calculate position values
        for h in holdings:
            sym = h.symbol.upper()
            try:
                quote_resp = await market_service.get_quote(db, sym)
                curr_price = quote_resp.data.price
            except Exception:
                curr_price = h.buy_price  # Fallback to cost basis if telemetry is offline

            pos_curr_val = round(h.quantity * curr_price, 2)
            pos_cost = round(h.quantity * h.buy_price, 2)
            pos_pnl = round(pos_curr_val - pos_cost, 2)
            pos_pnl_pct = round((pos_pnl / pos_cost * 100), 2) if pos_cost > 0 else 0.0

            # Determine sector
            comp = db.query(Company).filter(Company.symbol == sym).first()
            sector = comp.sector if comp and comp.sector else SECTOR_MAP.get(sym, "Diversified Equities")

            total_holdings_value += pos_curr_val
            total_invested += pos_cost

            positions.append(
                PositionHealth(
                    symbol=sym,
                    quantity=h.quantity,
                    buy_price=h.buy_price,
                    current_price=curr_price,
                    current_value=pos_curr_val,
                    unrealized_pnl=pos_pnl,
                    pnl_percent=pos_pnl_pct,
                    weight_percent=0.0,  # Will normalize below
                    sector=sector,
                )
            )

        # 2. Normalize position weights and calculate sector exposures
        top_weight = 0.0
        hhi = 0.0

        for p in positions:
            weight = round((p.current_value / total_holdings_value * 100), 2) if total_holdings_value > 0 else 0.0
            p.weight_percent = weight
            if weight > top_weight:
                top_weight = weight
            hhi += (weight / 100) ** 2

            sector_totals[p.sector] = sector_totals.get(p.sector, 0.0) + p.current_value

        sector_exposures = [
            SectorExposure(
                sector=sec,
                value=round(val, 2),
                weight_percent=round((val / total_holdings_value * 100), 2) if total_holdings_value > 0 else 0.0,
            )
            for sec, val in sorted(sector_totals.items(), key=lambda x: x[1], reverse=True)
        ]

        # 3. Watchlist overlap
        watchlists = db.query(Watchlist).filter(Watchlist.user_id == portfolio.user_id).all()
        wl_symbols = set()
        for w in watchlists:
            if w.symbols:
                for s in w.symbols.split(","):
                    wl_symbols.add(s.strip().upper())

        holding_symbols = {p.symbol for p in positions}
        overlap = list(holding_symbols.intersection(wl_symbols))

        metrics = {
            "total_holdings_value": total_holdings_value,
            "total_invested": total_invested,
            "top_weight": top_weight,
            "hhi": round(hhi, 4),
            "watchlist_overlap": overlap,
        }

        return positions, sector_exposures, metrics


portfolio_intelligence_service = PortfolioIntelligenceService()
