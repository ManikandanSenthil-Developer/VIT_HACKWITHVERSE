from datetime import datetime, timezone
import json
import logging
from typing import Any, Callable, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.watchlist import Watchlist
from app.models.market import Company, Security, MarketSnapshot, FundamentalData, PriceHistory
from app.models.monitoring import Alert, MarketEvent
from app.models.intelligence import AnalysisHistory
from app.services.market.service import market_service
from app.services.risk.portfolio_intelligence import portfolio_intelligence_service
from app.services.risk.risk_engine import risk_engine
from app.services.risk.scenario_engine import ScenarioEngine
from app.schemas.risk import ScenarioRequest
from app.services.retrieval.vector_search import VectorSearchService
from app.schemas.rag import RagSearchRequest
from app.services.agents.technical_agent import TechnicalMomentumAgent
from app.services.agents.fundamental_agent import FundamentalAgent
from app.services.agents.sentiment_agent import SentimentMarketAgent

logger = logging.getLogger("mats.copilot.tools")


class CopilotToolRegistry:
    """
    Safe tool registry providing access to portfolio, market, RAG, risk,
    and specialized agent intelligence for the Investor Copilot.
    Every tool enforces input sanitization, user authorization, and safe fallbacks.
    """

    def __init__(self):
        self.technical_agent = TechnicalMomentumAgent()
        self.fundamental_agent = FundamentalAgent()
        self.sentiment_agent = SentimentMarketAgent()

    async def execute_tool(
        self,
        tool_name: str,
        db: Session,
        user_id: int,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Dispatches to registered tool handler with error boundaries and timing."""
        handlers: Dict[str, Callable] = {
            "get_company": self._tool_get_company,
            "get_market_data": self._tool_get_market_data,
            "get_historical_data": self._tool_get_historical_data,
            "get_portfolio": self._tool_get_portfolio,
            "get_watchlist": self._tool_get_watchlist,
            "get_risk": self._tool_get_risk,
            "get_alerts": self._tool_get_alerts,
            "search_research": self._tool_search_research,
            "run_technical_analysis": self._tool_run_technical_analysis,
            "run_fundamental_analysis": self._tool_run_fundamental_analysis,
            "run_sentiment_analysis": self._tool_run_sentiment_analysis,
            "run_scenario": self._tool_run_scenario,
            "get_analysis_history": self._tool_get_analysis_history,
        }

        if tool_name not in handlers:
            return {"success": False, "error": f"Tool '{tool_name}' is not registered."}

        try:
            result = await handlers[tool_name](db=db, user_id=user_id, **parameters)
            return {"success": True, "tool": tool_name, "data": result}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
            return {"success": False, "tool": tool_name, "error": f"Tool execution failed: {str(e)}"}

    async def _tool_get_company(self, db: Session, user_id: int, symbol: str, **kwargs) -> Dict[str, Any]:
        sym = symbol.upper().strip()
        comp = db.query(Company).filter(Company.symbol == sym).first()
        if not comp:
            return {"symbol": sym, "found": False, "note": f"Company profile for {sym} unavailable in database."}

        fund = (
            db.query(FundamentalData)
            .filter(FundamentalData.company_id == comp.id)
            .order_by(FundamentalData.fiscal_year.desc())
            .first()
        )
        return {
            "symbol": sym,
            "found": True,
            "name": comp.name,
            "sector": comp.sector or "Unavailable",
            "industry": comp.industry or "Unavailable",
            "description": comp.description or "Unavailable",
            "fundamentals": {
                "fiscal_year": fund.fiscal_year if fund else "Unavailable",
                "pe_ratio": fund.pe_ratio if fund else "Unavailable",
                "pb_ratio": fund.pb_ratio if fund else "Unavailable",
                "debt_to_equity": fund.debt_to_equity if fund else "Unavailable",
                "revenue": fund.revenue if fund else "Unavailable",
                "net_income": fund.net_income if fund else "Unavailable",
                "free_cash_flow": fund.free_cash_flow if fund else "Unavailable",
            },
        }

    async def _tool_get_market_data(self, db: Session, user_id: int, symbol: str, **kwargs) -> Dict[str, Any]:
        sym = symbol.upper().strip()
        quote_resp = await market_service.get_quote(db, sym)
        q = quote_resp.data
        return {
            "symbol": q.symbol,
            "price": q.price,
            "change": q.change,
            "change_percent": q.change_percent,
            "volume": q.volume,
            "pe_ratio": q.pe_ratio if q.pe_ratio is not None else "Unavailable",
            "market_cap": q.market_cap if q.market_cap is not None else "Unavailable",
            "timestamp": q.timestamp,
            "source": quote_resp.source,
            "fresh": quote_resp.fresh,
            "cached": quote_resp.cached,
        }

    async def _tool_get_historical_data(self, db: Session, user_id: int, symbol: str, limit: int = 30, **kwargs) -> Dict[str, Any]:
        sym = symbol.upper().strip()
        hist_resp = await market_service.get_historical_prices(db, sym, period="1mo")
        prices = hist_resp.data.prices[:limit]
        return {
            "symbol": sym,
            "count": len(prices),
            "source": hist_resp.source,
            "prices": [
                {
                    "timestamp": p.timestamp,
                    "close": p.close,
                    "volume": p.volume,
                    "high": p.high,
                    "low": p.low,
                }
                for p in prices
            ],
        }

    async def _tool_get_portfolio(self, db: Session, user_id: int, **kwargs) -> Dict[str, Any]:
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return {"found": False, "message": "No portfolio on record for authenticated user."}

        positions, sector_exposures, metrics = await portfolio_intelligence_service.evaluate_portfolio(db, portfolio)
        return {
            "found": True,
            "portfolio_id": portfolio.id,
            "name": portfolio.name,
            "cash_balance": portfolio.cash_balance,
            "total_holdings_value": metrics["total_holdings_value"],
            "total_invested": metrics["total_invested"],
            "unrealized_pnl": round(metrics["total_holdings_value"] - metrics["total_invested"], 2),
            "holdings": [
                {
                    "symbol": p.symbol,
                    "quantity": p.quantity,
                    "current_price": p.current_price,
                    "current_value": p.current_value,
                    "weight_percent": p.weight_percent,
                    "sector": p.sector,
                    "pnl_percent": p.pnl_percent,
                }
                for p in positions
            ],
            "sector_exposures": [
                {"sector": s.sector, "weight_percent": s.weight_percent, "holdings_count": s.holdings_count}
                for s in sector_exposures
            ],
        }

    async def _tool_get_watchlist(self, db: Session, user_id: int, **kwargs) -> Dict[str, Any]:
        watchlist = db.query(Watchlist).filter(Watchlist.user_id == user_id).first()
        if not watchlist:
            return {"symbols": [], "count": 0}
        symbols = [s.strip().upper() for s in watchlist.symbols.split(",") if s.strip()]
        return {"symbols": symbols, "count": len(symbols), "name": watchlist.name}

    async def _tool_get_risk(self, db: Session, user_id: int, portfolio_id: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        query = db.query(Portfolio).filter(Portfolio.user_id == user_id)
        if portfolio_id:
            query = query.filter(Portfolio.id == portfolio_id)
        portfolio = query.first()
        if not portfolio:
            return {"found": False, "message": "No portfolio found for risk evaluation."}

        positions, sector_exposures, metrics = await portfolio_intelligence_service.evaluate_portfolio(db, portfolio)
        risk_explanation = risk_engine.evaluate_risk(
            positions=positions,
            sector_exposures=sector_exposures,
            metrics=metrics,
            active_events_count=0,
            annualized_vol=38.5,
            max_drawdown=18.2,
        )
        return {
            "found": True,
            "portfolio_id": portfolio.id,
            "risk_score": risk_explanation.risk_score,
            "risk_level": risk_explanation.risk_level,
            "key_drivers": risk_explanation.key_drivers,
            "factors": [f.model_dump() for f in risk_explanation.factors],
            "summary": risk_explanation.summary,
            "recommendations": risk_explanation.recommendations,
        }

    async def _tool_get_alerts(self, db: Session, user_id: int, limit: int = 5, **kwargs) -> Dict[str, Any]:
        alerts = (
            db.query(Alert)
            .filter(Alert.user_id == user_id)
            .order_by(Alert.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "count": len(alerts),
            "alerts": [
                {
                    "id": a.id,
                    "symbol": a.symbol,
                    "title": a.title,
                    "explanation": a.explanation,
                    "severity": a.severity,
                    "priority": a.priority,
                    "status": a.status,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in alerts
            ],
        }

    async def _tool_search_research(self, db: Session, user_id: int, query: str, symbol: Optional[str] = None, limit: int = 4, **kwargs) -> Dict[str, Any]:
        search_req = RagSearchRequest(
            query=query,
            symbol=symbol.upper() if symbol else None,
            top_k=limit,
        )
        res = await VectorSearchService.search(db=db, request=search_req)
        return {
            "query": query,
            "symbol": symbol,
            "count": len(res.results),
            "results": [
                {
                    "company_symbol": r.citation.company_symbol,
                    "title": r.citation.document_title,
                    "section": r.citation.section,
                    "similarity": round(r.score, 3),
                    "excerpt": r.text[:280] + ("..." if len(r.text) > 280 else ""),
                    "source": r.source,
                }
                for r in res.results
            ],
        }

    async def _tool_run_technical_analysis(self, db: Session, user_id: int, symbol: str, **kwargs) -> Dict[str, Any]:
        finding = await self.technical_agent.analyze(symbol=symbol, query="Technical analysis", db=db)
        return finding.model_dump()

    async def _tool_run_fundamental_analysis(self, db: Session, user_id: int, symbol: str, **kwargs) -> Dict[str, Any]:
        finding = await self.fundamental_agent.analyze(symbol=symbol, query="Fundamental analysis", db=db)
        return finding.model_dump()

    async def _tool_run_sentiment_analysis(self, db: Session, user_id: int, symbol: str, **kwargs) -> Dict[str, Any]:
        finding = await self.sentiment_agent.analyze(symbol=symbol, query="Sentiment analysis", db=db)
        return finding.model_dump()

    async def _tool_run_scenario(
        self,
        db: Session,
        user_id: int,
        target_symbol: Optional[str] = None,
        percentage_change: float = -10.0,
        target_sector: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return {"success": False, "message": "No portfolio to stress test."}

        req = ScenarioRequest(
            target_symbol=target_symbol,
            target_sector=target_sector,
            percentage_change=percentage_change,
            scenario_name=f"Stress Test: {percentage_change}% shock",
        )
        resp = await ScenarioEngine.run_scenario(db=db, portfolio=portfolio, request=req)
        return resp.model_dump()

    async def _tool_get_analysis_history(self, db: Session, user_id: int, symbol: Optional[str] = None, limit: int = 5, **kwargs) -> Dict[str, Any]:
        q = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == user_id)
        if symbol:
            q = q.filter(AnalysisHistory.symbol == symbol.upper().strip())
        records = q.order_by(AnalysisHistory.created_at.desc()).limit(limit).all()
        return {
            "count": len(records),
            "analyses": [
                {
                    "id": r.id,
                    "symbol": r.symbol,
                    "assessment": r.overall_assessment,
                    "confidence": r.confidence,
                    "query": r.query,
                    "summary": r.summary,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ],
        }


tool_registry = CopilotToolRegistry()
