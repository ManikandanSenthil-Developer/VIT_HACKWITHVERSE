from typing import Dict, List
from pydantic import BaseModel, Field
from app.services.agents.base import AgentFinding


class SignalConflict(BaseModel):
    conflict_type: str
    conflicting_agents: List[str]
    conflicting_signals: Dict[str, str]
    description: str
    severity: str  # high, medium, low
    evidence_summary: List[str] = Field(default_factory=list)


class ConflictDetector:
    """
    Critical MATS analytical component.
    Identifies multidimensional divergence between technical momentum, fundamental valuation,
    market sentiment, and official SEC risk disclosures rather than muting disagreements via averaging.
    """

    @staticmethod
    def detect_conflicts(findings: List[AgentFinding]) -> List[SignalConflict]:
        conflicts: List[SignalConflict] = []
        findings_by_agent: Dict[str, AgentFinding] = {f.agent: f for f in findings}

        tech = findings_by_agent.get("technical")
        fund = findings_by_agent.get("fundamental")
        sent = findings_by_agent.get("sentiment")
        rag = findings_by_agent.get("rag_research")

        # 1. Major Technical vs Fundamental Divergence
        if tech and fund:
            if tech.signal == "BEARISH" and fund.signal == "BULLISH":
                conflicts.append(
                    SignalConflict(
                        conflict_type="TECHNICAL_DOWNTREND_VS_FUNDAMENTAL_EXPANSION",
                        conflicting_agents=["technical", "fundamental"],
                        conflicting_signals={"technical": tech.signal, "fundamental": fund.signal},
                        description=(
                            "Technical indicators show deteriorating price momentum below key moving averages, "
                            "whereas balance sheet reporting confirms resilient profitability and revenue expansion. "
                            "This suggests short-term market selling pressure despite underlying corporate solvency."
                        ),
                        severity="high",
                        evidence_summary=[tech.evidence[0] if tech.evidence else "", fund.evidence[0] if fund.evidence else ""],
                    )
                )
            elif tech.signal == "BULLISH" and fund.signal in ("BEARISH", "CAUTIOUS"):
                conflicts.append(
                    SignalConflict(
                        conflict_type="VALUATION_OR_LEVERAGE_VS_MOMENTUM_DISCONNECT",
                        conflicting_agents=["technical", "fundamental"],
                        conflicting_signals={"technical": tech.signal, "fundamental": fund.signal},
                        description=(
                            "Technical momentum indicates aggressive upward price discovery, but fundamental metrics "
                            "signal elevated valuation multiples or debt exposure that may constrain long-term multiples expansion."
                        ),
                        severity="medium",
                        evidence_summary=[tech.evidence[0] if tech.evidence else "", fund.evidence[0] if fund.evidence else ""],
                    )
                )

        # 2. Technical vs Sentiment Divergence
        if tech and sent:
            if tech.signal == "BULLISH" and sent.signal == "BEARISH":
                conflicts.append(
                    SignalConflict(
                        conflict_type="TECHNICAL_STRENGTH_VS_INSTITUTIONAL_DISTRIBUTION",
                        conflicting_agents=["technical", "sentiment"],
                        conflicting_signals={"technical": tech.signal, "sentiment": sent.signal},
                        description=(
                            "Price retains an upward trend structure, but recent order flow volume and volatility skew "
                            "indicate increased distribution or risk-off institutional sentiment."
                        ),
                        severity="medium",
                        evidence_summary=[tech.evidence[0] if tech.evidence else "", sent.evidence[0] if sent.evidence else ""],
                    )
                )

        # 3. Fundamental Strength vs RAG Disclosed Regulatory/Supply Chain Headwinds
        if fund and rag:
            if fund.signal == "BULLISH" and rag.signal == "CAUTIOUS":
                conflicts.append(
                    SignalConflict(
                        conflict_type="QUANTITATIVE_GROWTH_VS_QUALITATIVE_DISCLOSURE_RISKS",
                        conflicting_agents=["fundamental", "rag_research"],
                        conflicting_signals={"fundamental": fund.signal, "rag_research": rag.signal},
                        description=(
                            "Reported financial results verify strong operating cash flows and margin expansion, "
                            "yet official SEC Item 1A disclosures identify material operational dependencies (foundry capacity, regulatory investigations) "
                            "that represent potential external shocks."
                        ),
                        severity="medium",
                        evidence_summary=[fund.evidence[0] if fund.evidence else "", rag.evidence[0] if rag.evidence else ""],
                    )
                )

        return conflicts
