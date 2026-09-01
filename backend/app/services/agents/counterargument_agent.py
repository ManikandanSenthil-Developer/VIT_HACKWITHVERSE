from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.services.agents.base import BaseAgent, AgentFinding
from app.services.market.service import market_service
from app.models.market import Company, FundamentalData
from app.services.retrieval.vector_search import VectorSearchService
from app.schemas.rag import RagSearchRequest


class CounterargumentFinding:
    def __init__(
        self,
        symbol: str,
        challenges: List[str],
        evidence: List[str],
        invalidation_triggers: List[str],
        severity: str = "MEDIUM",
        confidence: float = 0.85,
    ):
        self.symbol = symbol.upper()
        self.challenges = challenges
        self.evidence = evidence
        self.invalidation_triggers = invalidation_triggers
        self.severity = severity
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "challenges": self.challenges,
            "evidence": self.evidence,
            "invalidation_triggers": self.invalidation_triggers,
            "severity": self.severity,
            "confidence": self.confidence,
        }


class CounterargumentAgent(BaseAgent):
    """
    Specialized Devil's Advocate Agent.
    Actively stress-tests bullish sentiment, syntheses, and investment theses.
    Searches for valuation stretch, leverage risks, momentum divergence,
    and regulatory headwinds without fabricating negative evidence.
    """

    def __init__(self):
        super().__init__(name="counterargument", role="Devil's Advocate & Risk Challenge")

    async def analyze(
        self,
        symbol: str,
        query: str,
        db: Session,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentFinding:
        challenge = await self.generate_counterarguments(symbol=symbol, db=db, context=context)
        now_str = datetime.now(timezone.utc).isoformat()
        
        summary = (
            f"Devil's Advocate Stress Test for {symbol.upper()}: Identified {len(challenge.challenges)} primary challenges. "
            + (" ".join(challenge.challenges[:2]))
        )

        return AgentFinding(
            agent=self.name,
            finding=summary,
            signal="BEARISH" if challenge.severity in ("HIGH", "CRITICAL") else "CAUTIOUS",
            confidence=challenge.confidence,
            evidence=challenge.evidence,
            source_ids=["balance_sheet", "market_telemetry", "regulatory_filings"],
            timestamp=now_str,
            limitations=["Counterargument analysis explicitly seeks adverse factors to combat confirmation bias."],
            metrics={
                "challenge_count": len(challenge.challenges),
                "severity": challenge.severity,
                "invalidation_triggers": challenge.invalidation_triggers,
            },
        )

    async def generate_counterarguments(
        self,
        symbol: str,
        db: Session,
        context: Optional[Dict[str, Any]] = None,
    ) -> CounterargumentFinding:
        sym = symbol.upper().strip()
        challenges: List[str] = []
        evidence: List[str] = []
        invalidation_triggers: List[str] = []
        severity = "LOW"

        # 1. Check fundamentals for valuation / debt stress
        comp = db.query(Company).filter(Company.symbol == sym).first()
        if comp:
            fund = (
                db.query(FundamentalData)
                .filter(FundamentalData.company_id == comp.id)
                .order_by(FundamentalData.fiscal_year.desc())
                .first()
            )
            if fund:
                if fund.pe_ratio and fund.pe_ratio > 45.0:
                    challenges.append(
                        f"Elevated valuation multiple (P/E {fund.pe_ratio:.1f}x) leaves little margin for execution error."
                    )
                    evidence.append(f"Reported P/E ratio is {fund.pe_ratio:.1f}x (Fiscal Year {fund.fiscal_year}).")
                    severity = "HIGH"
                    invalidation_triggers.append("Multiple contraction if quarterly earnings miss consensus by > 5%.")

                if fund.debt_to_equity and fund.debt_to_equity > 1.8:
                    challenges.append(
                        f"High financial leverage (Debt-to-Equity {fund.debt_to_equity:.2f}) heightens sensitivity to interest rate shifts."
                    )
                    evidence.append(f"Debt-to-Equity is {fund.debt_to_equity:.2f} relative to peer norms.")
                    severity = "HIGH"
                    invalidation_triggers.append("Free cash flow deterioration restricting debt servicing.")

                if fund.free_cash_flow is not None and fund.free_cash_flow < 0:
                    challenges.append("Negative free cash flow requires external capital or dilution to fund operations.")
                    evidence.append(f"Operating FCF is negative (${fund.free_cash_flow:,.0f}).")
                    severity = "CRITICAL"

        # 2. Check market quote telemetry for momentum overextension
        try:
            quote_resp = await market_service.get_quote(db, sym)
            q = quote_resp.data
            if q.change_percent and abs(q.change_percent) >= 5.0:
                challenges.append(
                    f"Intraday volatility ({q.change_percent:+.2f}%) indicates heightened market regime instability."
                )
                evidence.append(f"Single-session price move of {q.change_percent:+.2f}%.")
                if severity == "LOW":
                    severity = "MEDIUM"
        except Exception:
            pass

        # 3. Check official SEC filings for documented regulatory & operational risk factors
        try:
            rag_req = RagSearchRequest(
                query="risk factors supply chain competition regulation",
                symbol=sym,
                top_k=2,
            )
            rag_res = await VectorSearchService.search(db=db, request=rag_req)
            for item in rag_res.results:
                if item.score >= 0.25:
                    excerpt = item.text[:140].replace("\n", " ") + "..."
                    sec_name = item.citation.section or "Item 1A"
                    challenges.append(f"Regulatory & market risk identified in SEC 10-K: {excerpt}")
                    evidence.append(f"SEC 10-K Filing ({sec_name}): \"{excerpt}\"")
                    invalidation_triggers.append(f"Materialization of {sec_name} regulatory warnings.")
                    if severity == "LOW":
                        severity = "MEDIUM"
        except Exception:
            pass

        # 4. Fallback baseline if no acute red flags found
        if not challenges:
            challenges.append(
                f"Macro multiple compression or sector rotation away from {comp.sector if comp and comp.sector else 'this sector'}."
            )
            evidence.append("Broader equity market correlations and macroeconomic tightening conditions.")
            invalidation_triggers.append("Systemic market drawdown exceeding 10%.")
            severity = "LOW"

        return CounterargumentFinding(
            symbol=sym,
            challenges=challenges,
            evidence=evidence,
            invalidation_triggers=invalidation_triggers,
            severity=severity,
            confidence=0.88,
        )


counterargument_agent = CounterargumentAgent()
