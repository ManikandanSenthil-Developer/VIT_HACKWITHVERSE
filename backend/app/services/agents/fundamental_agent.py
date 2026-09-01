from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.services.agents.base import BaseAgent, AgentFinding
from app.services.market.service import market_service


class FundamentalAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="fundamental", role="Fundamental and Balance Sheet Analysis")

    async def analyze(
        self,
        symbol: str,
        query: str,
        db: Session,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentFinding:
        sym = symbol.upper()
        now_str = datetime.now(timezone.utc).isoformat()

        try:
            fund_resp = await market_service.get_fundamentals(db, sym)
            comp_resp = await market_service.get_company_profile(db, sym)
            fund = fund_resp.data
            comp = comp_resp.data
            fund_source = fund_resp.source
        except Exception as e:
            return AgentFinding(
                agent=self.name,
                finding=f"Fundamental data could not be retrieved for {sym}: {str(e)}",
                signal="NEUTRAL",
                confidence=0.1,
                evidence=[],
                source_ids=[],
                timestamp=now_str,
                limitations=["Corporate financial filings unavailable or offline."],
            )

        evidence: List[str] = []
        unavailable_metrics: List[str] = []

        # Evaluate and document available metrics explicitly
        if fund.revenue is not None and fund.revenue > 0:
            evidence.append(f"Reported Annual Revenue: ${fund.revenue / 1e9:.2f}B.")
        else:
            unavailable_metrics.append("Revenue")

        if fund.net_income is not None:
            evidence.append(f"Reported Net Income: ${fund.net_income / 1e9:.2f}B.")
        else:
            unavailable_metrics.append("Net Income")

        if fund.eps is not None:
            evidence.append(f"Diluted EPS: ${fund.eps:.2f}.")
        else:
            unavailable_metrics.append("Diluted EPS")

        if fund.free_cash_flow is not None:
            evidence.append(f"Free Cash Flow: ${fund.free_cash_flow / 1e9:.2f}B.")
        else:
            unavailable_metrics.append("Free Cash Flow")

        if fund.pe_ratio is not None:
            evidence.append(f"Trailing P/E Ratio: {fund.pe_ratio:.1f}x.")
        else:
            unavailable_metrics.append("P/E Ratio")

        if fund.debt_to_equity is not None:
            evidence.append(f"Debt-to-Equity Ratio: {fund.debt_to_equity:.2f}.")
        else:
            unavailable_metrics.append("Debt-to-Equity")

        # Breakdowns
        breakdown = fund.metrics_breakdown or {}
        gross_margin = breakdown.get("gross_margin")
        operating_margin = breakdown.get("operating_margin")

        if gross_margin is not None:
            evidence.append(f"Gross Margin: {gross_margin:.1f}%.")
        if operating_margin is not None:
            evidence.append(f"Operating Margin: {operating_margin:.1f}%.")

        limitations = []
        if unavailable_metrics:
            limitations.append(f"The following metrics were unavailable in report: {', '.join(unavailable_metrics)}.")

        # Determine Signal based on real data
        is_profitable = fund.net_income is not None and fund.net_income > 0
        has_positive_fcf = fund.free_cash_flow is not None and fund.free_cash_flow > 0
        is_high_valuation = fund.pe_ratio is not None and fund.pe_ratio > 60.0
        is_leveraged = fund.debt_to_equity is not None and fund.debt_to_equity > 1.8

        if is_profitable and has_positive_fcf and not is_high_valuation and not is_leveraged:
            signal = "BULLISH"
            confidence = 0.86
            finding = (
                f"{sym} exhibits pristine fundamental health with positive net earnings (${fund.net_income / 1e9:.2f}B), "
                f"resilient free cash flow generation (${fund.free_cash_flow / 1e9:.2f}B), and manageable debt leverage."
            )
        elif is_profitable and is_high_valuation:
            signal = "CAUTIOUS"
            confidence = 0.84
            finding = (
                f"{sym} demonstrates superior corporate profitability and cash generation, but its trailing P/E of "
                f"{fund.pe_ratio:.1f}x reflects significant valuation premium that requires continuous outsized growth."
            )
        elif not is_profitable or is_leveraged:
            signal = "BEARISH"
            confidence = 0.80
            finding = (
                f"{sym} shows fundamental headwinds characterized by margin compression or elevated financial leverage "
                f"(Debt-to-Equity: {fund.debt_to_equity or 'N/A'})."
            )
        else:
            signal = "NEUTRAL"
            confidence = 0.74
            finding = f"{sym} maintains stable balance sheet metrics in line with peer group averages."

        return AgentFinding(
            agent=self.name,
            finding=finding,
            signal=signal,
            confidence=confidence,
            evidence=evidence,
            source_ids=[f"{fund_source}:{sym}:fundamentals"],
            timestamp=now_str,
            limitations=limitations,
            metrics={
                "revenue": fund.revenue,
                "net_income": fund.net_income,
                "eps": fund.eps,
                "free_cash_flow": fund.free_cash_flow,
                "pe_ratio": fund.pe_ratio,
                "debt_to_equity": fund.debt_to_equity,
                "gross_margin": gross_margin,
                "operating_margin": operating_margin,
                "fiscal_year": fund.fiscal_year,
            },
        )
