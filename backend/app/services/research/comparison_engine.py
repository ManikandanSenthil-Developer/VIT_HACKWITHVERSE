from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.market import Company, FundamentalData
from app.services.market.service import market_service
from app.services.agents.technical_agent import TechnicalMomentumAgent
from app.services.agents.sentiment_agent import SentimentMarketAgent
from app.services.retrieval.vector_search import VectorSearchService
from app.schemas.rag import RagSearchRequest


class CompanyComparisonEngine:
    """
    Side-by-side comparative financial intelligence engine.
    Strictly observes factual data boundaries: missing metrics are explicitly
    marked as 'Unavailable' rather than invented or approximated.
    """

    def __init__(self):
        self.technical_agent = TechnicalMomentumAgent()
        self.sentiment_agent = SentimentMarketAgent()

    async def compare(
        self,
        db: Session,
        symbol_a: str,
        symbol_b: str,
    ) -> Dict[str, Any]:
        sym_a = symbol_a.upper().strip()
        sym_b = symbol_b.upper().strip()

        data_a = await self._gather_company_data(db, sym_a)
        data_b = await self._gather_company_data(db, sym_b)

        # Peer detection
        is_same_sector = (
            data_a["profile"]["sector"] != "Unavailable"
            and data_a["profile"]["sector"] == data_b["profile"]["sector"]
        )

        # Relative summary
        relative_insights = []
        if is_same_sector:
            relative_insights.append(f"{sym_a} and {sym_b} are direct peers in the {data_a['profile']['sector']} sector.")
        else:
            relative_insights.append(
                f"{sym_a} ({data_a['profile']['sector']}) and {sym_b} ({data_b['profile']['sector']}) operate in different sectors."
            )

        pe_a = data_a["fundamentals"].get("pe_ratio")
        pe_b = data_b["fundamentals"].get("pe_ratio")
        if pe_a != "Unavailable" and pe_b != "Unavailable":
            diff = abs(pe_a - pe_b)
            higher = sym_a if pe_a > pe_b else sym_b
            lower = sym_b if pe_a > pe_b else sym_a
            relative_insights.append(
                f"{higher} trades at a valuation premium ({max(pe_a, pe_b):.1f}x P/E) vs {lower} ({min(pe_a, pe_b):.1f}x P/E), a {diff:.1f}x multiple spread."
            )

        sig_a = data_a["technical"]["signal"]
        sig_b = data_b["technical"]["signal"]
        relative_insights.append(
            f"Technical momentum: {sym_a} is {sig_a} vs {sym_b} is {sig_b}."
        )

        return {
            "symbol_a": sym_a,
            "symbol_b": sym_b,
            "is_peers": is_same_sector,
            "relative_insights": relative_insights,
            "company_a": data_a,
            "company_b": data_b,
            "disclaimer": "Comparative analysis is provided for objective research purposes. Differences reflect historical financials and reported market metrics.",
        }

    async def _gather_company_data(self, db: Session, symbol: str) -> Dict[str, Any]:
        comp = db.query(Company).filter(Company.symbol == symbol).first()

        profile = {
            "name": comp.name if comp else symbol,
            "sector": comp.sector if comp and comp.sector else "Unavailable",
            "industry": comp.industry if comp and comp.industry else "Unavailable",
        }

        # Quotes
        try:
            q_resp = await market_service.get_quote(db, symbol)
            q = q_resp.data
            market = {
                "price": q.price,
                "change_percent": q.change_percent,
                "volume": q.volume,
                "market_cap": q.market_cap if q.market_cap is not None else "Unavailable",
            }
        except Exception:
            market = {
                "price": "Unavailable",
                "change_percent": "Unavailable",
                "volume": "Unavailable",
                "market_cap": "Unavailable",
            }

        # Fundamentals
        fund = (
            db.query(FundamentalData)
            .filter(FundamentalData.symbol == symbol)
            .order_by(FundamentalData.fiscal_year.desc())
            .first()
        )
        if fund:
            fundamentals = {
                "fiscal_year": fund.fiscal_year,
                "pe_ratio": fund.pe_ratio if fund.pe_ratio is not None else "Unavailable",
                "pb_ratio": fund.pb_ratio if fund.pb_ratio is not None else "Unavailable",
                "debt_to_equity": fund.debt_to_equity if fund.debt_to_equity is not None else "Unavailable",
                "revenue": fund.revenue if fund.revenue is not None else "Unavailable",
                "net_income": fund.net_income if fund.net_income is not None else "Unavailable",
                "free_cash_flow": fund.free_cash_flow if fund.free_cash_flow is not None else "Unavailable",
            }
        else:
            fundamentals = {
                "fiscal_year": "Unavailable",
                "pe_ratio": "Unavailable",
                "pb_ratio": "Unavailable",
                "debt_to_equity": "Unavailable",
                "revenue": "Unavailable",
                "net_income": "Unavailable",
                "free_cash_flow": "Unavailable",
            }

        # Technical finding
        tech_finding = await self.technical_agent.analyze(symbol=symbol, query="Compare technicals", db=db)
        technical = {
            "signal": tech_finding.signal,
            "confidence": tech_finding.confidence,
            "summary": tech_finding.finding,
        }

        # Sentiment finding
        sent_finding = await self.sentiment_agent.analyze(symbol=symbol, query="Compare sentiment", db=db)
        sentiment = {
            "signal": sent_finding.signal,
            "confidence": sent_finding.confidence,
            "summary": sent_finding.finding,
        }

        # Top RAG citation
        try:
            rag_req = RagSearchRequest(query="business overview operations", symbol=symbol, top_k=1)
            rag_res = await VectorSearchService.search(db=db, request=rag_req)
            top_citation = rag_res.results[0].text[:180] + "..." if rag_res.results else "No indexed regulatory filing."
        except Exception:
            top_citation = "No indexed regulatory filing."

        return {
            "profile": profile,
            "market": market,
            "fundamentals": fundamentals,
            "technical": technical,
            "sentiment": sentiment,
            "top_citation": top_citation,
        }


comparison_engine = CompanyComparisonEngine()
