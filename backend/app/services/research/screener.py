from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.market import Company, FundamentalData, MarketSnapshot


class ScreenerEngine:
    """
    Deterministic financial screener.
    Filters securities using factual database metrics and provides
    clear, explainable 'Why Included?' attribution for every match.
    """

    @staticmethod
    def screen_securities(
        db: Session,
        sector: Optional[str] = None,
        max_pe: Optional[float] = None,
        min_pe: Optional[float] = None,
        max_debt_to_equity: Optional[float] = None,
        min_change_percent: Optional[float] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        companies = db.query(Company).all()
        results: List[Dict[str, Any]] = []

        for comp in companies:
            sym = comp.symbol
            fund = (
                db.query(FundamentalData)
                .filter(FundamentalData.company_id == comp.id)
                .order_by(FundamentalData.fiscal_year.desc())
                .first()
            )
            snap = (
                db.query(MarketSnapshot)
                .filter(MarketSnapshot.symbol == sym)
                .order_by(MarketSnapshot.timestamp.desc())
                .first()
            )

            # Filtering checks
            if sector and comp.sector:
                if sector.lower() not in comp.sector.lower():
                    continue

            pe = fund.pe_ratio if fund and fund.pe_ratio is not None else None
            if max_pe is not None and (pe is None or pe > max_pe):
                continue
            if min_pe is not None and (pe is None or pe < min_pe):
                continue

            de = fund.debt_to_equity if fund and fund.debt_to_equity is not None else None
            if max_debt_to_equity is not None and (de is None or de > max_debt_to_equity):
                continue

            chg = snap.change_percent if snap and snap.change_percent is not None else None
            if min_change_percent is not None and (chg is None or chg < min_change_percent):
                continue

            # Explainability construction
            reasons: List[str] = []
            if sector and comp.sector:
                reasons.append(f"Sector match: {comp.sector}")
            if pe is not None:
                reasons.append(f"P/E multiple: {pe:.1f}x")
            if de is not None:
                reasons.append(f"Debt-to-Equity: {de:.2f}")
            if chg is not None:
                reasons.append(f"Intraday change: {chg:+.2f}%")
            if fund and fund.revenue:
                reasons.append(f"Reported revenue: ${fund.revenue:,.0f}")

            why_included = "Included because: " + "; ".join(reasons) if reasons else "Matched baseline screening criteria."

            results.append({
                "symbol": sym,
                "name": comp.name,
                "sector": comp.sector or "Unavailable",
                "price": snap.price if snap else "Unavailable",
                "change_percent": chg if chg is not None else "Unavailable",
                "pe_ratio": pe if pe is not None else "Unavailable",
                "debt_to_equity": de if de is not None else "Unavailable",
                "revenue": fund.revenue if fund and fund.revenue is not None else "Unavailable",
                "why_included": why_included,
            })

        return results[:limit]


screener_engine = ScreenerEngine()
