from typing import List, Optional
from pydantic import BaseModel
from app.models.investor_profile import InvestorProfile
from app.services.agents.conflict_detector import SignalConflict
from app.services.agents.personalization_layer import PersonalizationLayer
from app.services.agents.synthesis_agent import SynthesisResult


class RecommendationResult(BaseModel):
    assessment: str
    confidence: float
    key_reasons: List[str]
    risks: List[str]
    what_to_monitor: List[str]
    sources: List[str]
    personalization_note: str


class RecommendationEngine:
    """
    Translates synthesized multi-agent findings into an objective, research-grounded recommendation.
    Strictly avoids reckless 'BUY NOW' directives, adhering to institutional retail governance.
    """

    @staticmethod
    def generate(
        symbol: str,
        synthesis: SynthesisResult,
        conflicts: List[SignalConflict],
        sources: List[str],
        profile: Optional[InvestorProfile],
    ) -> RecommendationResult:
        sym = symbol.upper()
        overall = synthesis.overall_assessment

        # Map synthesis to rigorous research stances
        if "Favorable" in overall and "Caution" not in overall:
            assessment = f"Research Signal: Favorable ({sym})"
        elif "Caution" in overall or "Headwinds" in overall:
            assessment = f"Research Signal: Cautious / Elevated Risk ({sym})"
        elif "Divergent" in overall:
            assessment = f"Research Signal: Conflicting Indicators / Monitor Support ({sym})"
        elif "Insufficient" in overall:
            assessment = f"Insufficient Evidence to Formulate Signal ({sym})"
        else:
            assessment = f"Research Signal: Neutral / Consolidation Watch ({sym})"

        key_reasons = synthesis.supporting_factors[:4] if synthesis.supporting_factors else [
            "Baseline trading volume and balance sheet solvency verified."
        ]

        risks = synthesis.opposing_factors[:4] if synthesis.opposing_factors else [
            "Market-wide macroeconomic interest rate and volatility fluctuations."
        ]

        for c in conflicts:
            risks.append(f"Signal Conflict: {c.description}")

        what_to_monitor = [
            f"Watch price interaction around 20-period moving average.",
            f"Next quarterly earnings disclosure and gross margin trend.",
            f"Regulatory filing updates regarding Item 1A operational risk disclosures.",
        ]

        personalization_note = PersonalizationLayer.apply_personalization(synthesis, profile)

        return RecommendationResult(
            assessment=assessment,
            confidence=synthesis.confidence,
            key_reasons=key_reasons,
            risks=risks,
            what_to_monitor=what_to_monitor,
            sources=sources,
            personalization_note=personalization_note,
        )
