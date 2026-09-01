from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.services.agents.base import AgentFinding
from app.services.agents.conflict_detector import SignalConflict


class SynthesisResult(BaseModel):
    overall_assessment: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_factors: List[str]
    opposing_factors: List[str]
    uncertainties: List[str]
    evidence_summary: List[str]
    limitations: List[str]


class SynthesisAgent:
    """
    Synthesizes multi-agent findings, detected conflicts, and factual evidence
    into an integrated institutional assessment without hallucination or arbitrary winner selection.
    """

    @staticmethod
    def synthesize(
        symbol: str,
        findings: List[AgentFinding],
        conflicts: List[SignalConflict],
    ) -> SynthesisResult:
        if not findings:
            return SynthesisResult(
                overall_assessment="Insufficient Data for Synthesis",
                confidence=0.0,
                supporting_factors=[],
                opposing_factors=[],
                uncertainties=["No specialized agents succeeded in providing analysis."],
                evidence_summary=[],
                limitations=["No agent telemetry available."],
            )

        supporting_factors: List[str] = []
        opposing_factors: List[str] = []
        uncertainties: List[str] = []
        all_evidence: List[str] = []
        all_limitations: List[str] = []

        bullish_count = 0
        bearish_count = 0
        cautious_count = 0
        total_conf = 0.0

        for f in findings:
            total_conf += f.confidence
            all_evidence.extend(f.evidence)
            all_limitations.extend(f.limitations)

            if f.signal == "BULLISH":
                bullish_count += 1
                supporting_factors.append(f"[{f.agent.capitalize()}] {f.finding}")
            elif f.signal in ("BEARISH", "CAUTIOUS"):
                if f.signal == "BEARISH":
                    bearish_count += 1
                else:
                    cautious_count += 1
                opposing_factors.append(f"[{f.agent.capitalize()}] {f.finding}")
            else:
                supporting_factors.append(f"[{f.agent.capitalize()}] Baseline stable: {f.finding}")

        # Note any conflicts as key uncertainties
        for c in conflicts:
            uncertainties.append(f"Conflict: {c.description}")

        # Base confidence calculation
        avg_conf = total_conf / len(findings)
        # Apply conflict discount
        conflict_penalty = 0.08 * len([c for c in conflicts if c.severity == "high"]) + 0.04 * len([c for c in conflicts if c.severity == "medium"])
        synthesis_conf = round(max(0.35, min(0.95, avg_conf - conflict_penalty)), 2)

        # Formulate Overall Assessment
        if bullish_count >= 2 and bearish_count == 0 and not conflicts:
            overall = "Favorable Multi-Factor Expansion"
        elif bullish_count >= 2 and (cautious_count > 0 or conflicts):
            overall = "Moderately Favorable with Pullback & Valuation Caution"
        elif bearish_count >= 2:
            overall = "Cautious / Elevated Technical & Fundamental Headwinds"
        elif conflicts:
            overall = "Divergent Signals: Strong Fundamentals Countered by Technical Friction"
        elif bullish_count > bearish_count:
            overall = "Constructive Outlook with Moderate Uncertainty"
        else:
            overall = "Neutral / Balanced Consolidation"

        return SynthesisResult(
            overall_assessment=overall,
            confidence=synthesis_conf,
            supporting_factors=supporting_factors,
            opposing_factors=opposing_factors,
            uncertainties=uncertainties,
            evidence_summary=all_evidence[:8],  # Keep top salient evidence points
            limitations=list(dict.fromkeys(all_limitations)),
        )
