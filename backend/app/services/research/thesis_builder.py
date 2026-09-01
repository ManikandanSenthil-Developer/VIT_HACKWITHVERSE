import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.market import Company, FundamentalData
from app.models.copilot import ResearchThesis
from app.services.market.service import market_service
from app.services.agents.technical_agent import TechnicalMomentumAgent
from app.services.agents.fundamental_agent import FundamentalAgent
from app.services.agents.counterargument_agent import counterargument_agent
from app.services.retrieval.vector_search import VectorSearchService
from app.schemas.rag import RagSearchRequest


class ThesisBuilder:
    """
    Constructs an evidence-backed, balanced investment research thesis.
    Synthesizes a Bull Case, Bear Case, Devil's Advocate Counterarguments,
    Invalidation Conditions, and weighted source provenance.
    """

    def __init__(self):
        self.technical_agent = TechnicalMomentumAgent()
        self.fundamental_agent = FundamentalAgent()

    async def build_thesis(
        self,
        db: Session,
        user_id: int,
        symbol: str,
        save_to_db: bool = False,
    ) -> Dict[str, Any]:
        sym = symbol.upper().strip()

        # 1. Fetch company and fundamentals
        comp = db.query(Company).filter(Company.symbol == sym).first()
        comp_name = comp.name if comp else sym

        fund = (
            db.query(FundamentalData)
            .filter(FundamentalData.symbol == sym)
            .order_by(FundamentalData.fiscal_year.desc())
            .first()
        )

        quote_resp = await market_service.get_quote(db, sym)
        q = quote_resp.data

        # 2. Run Agents
        tech = await self.technical_agent.analyze(symbol=sym, query="Technical thesis", db=db)
        fund_finding = await self.fundamental_agent.analyze(symbol=sym, query="Fundamental thesis", db=db)
        counter = await counterargument_agent.generate_counterarguments(symbol=sym, db=db)

        # 3. Retrieve SEC RAG Filings
        try:
            rag_req = RagSearchRequest(
                query="revenue growth business model market opportunity",
                symbol=sym,
                top_k=3,
            )
            rag_res = await VectorSearchService.search(db=db, request=rag_req)
        except Exception:
            rag_res = None

        # 4. Construct Bull Case
        bull_case: List[str] = []
        if fund and fund.revenue and fund.revenue > 10_000_000_000:
            bull_case.append(f"Substantial scale with reported annual revenue of ${fund.revenue:,.0f}.")
        if fund and fund.net_income and fund.net_income > 0:
            bull_case.append(f"Robust operating profitability with positive net income of ${fund.net_income:,.0f}.")
        if tech.signal in ("BULLISH", "NEUTRAL"):
            bull_case.append(f"Constructive technical structure: {tech.finding}")
        if rag_res and rag_res.results:
            bull_case.append(f"Regulatory disclosure confirmation: \"{rag_res.results[0].text[:140]}...\"")
        if not bull_case:
            bull_case.append(f"Market liquidity and established brand position in {comp.sector if comp else 'the sector'}.")

        # 5. Construct Bear Case
        bear_case: List[str] = []
        if fund and fund.pe_ratio and fund.pe_ratio > 35.0:
            bear_case.append(f"Premium valuation vulnerability: P/E multiple is {fund.pe_ratio:.1f}x.")
        if fund and fund.debt_to_equity and fund.debt_to_equity > 1.5:
            bear_case.append(f"Capital structure leverage: Debt-to-Equity is {fund.debt_to_equity:.2f}.")
        if tech.signal in ("BEARISH", "CAUTIOUS"):
            bear_case.append(f"Momentum headwinds: {tech.finding}")
        for ch in counter.challenges[:2]:
            bear_case.append(ch)

        # 6. Counterarguments (Devil's Advocate)
        counterarguments = counter.challenges

        # 7. Invalidation Conditions
        invalidation_conditions = [
            f"Sustained breakdown below 30-day technical low ($115.00).",
            f"Operating margin contraction > 300 basis points in upcoming fiscal quarterly report.",
        ] + counter.invalidation_triggers

        # 8. What to Monitor
        what_to_monitor = [
            f"Next quarterly Form 10-Q filing and revenue guidance.",
            f"Institutional trading volume divergence vs 30-day baseline.",
            f"Competitor margin trends in {comp.sector if comp else 'sector'}.",
        ]

        # 9. Evidence & Provenance Weighting
        evidence_citations: List[Dict[str, Any]] = []
        if rag_res and rag_res.results:
            for r in rag_res.results:
                evidence_citations.append({
                    "source": r.source,
                    "document_title": r.citation.document_title,
                    "section": r.citation.section or "10-K Disclosure",
                    "reliability_weight": 0.95,  # Official SEC Form 10-K
                    "recency_weight": 0.90,
                    "excerpt": r.text[:200] + "...",
                })

        evidence_citations.append({
            "source": quote_resp.source,
            "document_title": "Market Quote Telemetry",
            "section": "Live Market Data",
            "reliability_weight": 0.98,
            "recency_weight": 1.0,
            "excerpt": f"Current price ${q.price:.2f} ({q.change_percent:+.2f}%), Volume: {q.volume:,}",
        })

        summary = (
            f"Research thesis for {comp_name} ({sym}): Core market thesis remains {fund_finding.signal} "
            f"fundamentally with {tech.signal} technical momentum. However, Devil's Advocate analysis flags "
            f"{len(counterarguments)} key stress factors that could invalidate long-term execution."
        )

        title = f"Research Thesis: {comp_name} ({sym})"

        result = {
            "symbol": sym,
            "company_name": comp_name,
            "title": title,
            "summary": summary,
            "bull_case": bull_case,
            "bear_case": bear_case,
            "counterarguments": counterarguments,
            "invalidation_conditions": invalidation_conditions,
            "what_to_monitor": what_to_monitor,
            "evidence_citations": evidence_citations,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "disclaimer": "This research thesis is an autonomous decision-support synthesis. It challenges bias but does not constitute financial advice.",
        }

        # Optional persistence
        if save_to_db:
            thesis_record = ResearchThesis(
                user_id=user_id,
                symbol=sym,
                title=title,
                summary=summary,
                bull_case_json=json.dumps(bull_case),
                bear_case_json=json.dumps(bear_case),
                counterarguments_json=json.dumps(counterarguments),
                invalidation_conditions_json=json.dumps(invalidation_conditions),
                what_to_monitor_json=json.dumps(what_to_monitor),
                evidence_citations_json=json.dumps(evidence_citations),
            )
            db.add(thesis_record)
            db.commit()
            db.refresh(thesis_record)
            result["id"] = thesis_record.id

        return result


thesis_builder = ThesisBuilder()
