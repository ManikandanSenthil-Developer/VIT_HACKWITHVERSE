from typing import Optional
from app.models.investor_profile import InvestorProfile
from app.services.agents.synthesis_agent import SynthesisResult


class PersonalizationLayer:
    """
    Tailors the presentation and risk emphasis of synthesized financial intelligence
    to match the user's investor profile without ever altering underlying facts or fabricating evidence.
    """

    @staticmethod
    def apply_personalization(
        synthesis: SynthesisResult,
        profile: Optional[InvestorProfile],
    ) -> str:
        if not profile:
            return "Standard Institutional Framing: Objective balance of growth catalysts and systemic risk factors."

        risk = (profile.risk_tolerance or "moderate").lower()
        horizon = (profile.investment_horizon or "medium").lower()

        if risk == "conservative":
            note = (
                f"Personalized for Conservative Profile ({horizon.capitalize()}-term horizon): "
                f"Emphasizing capital preservation, balance sheet solvency, and downside volatility buffers. "
                f"Priority focus is placed on operating cash flow durability and debt obligations."
            )
        elif risk in ("aggressive", "speculative"):
            note = (
                f"Personalized for Aggressive/Growth Profile ({horizon.capitalize()}-term horizon): "
                f"Highlighting momentum expansion drivers, operating leverage, and addressable market catalysts "
                f"while monitoring high-beta volatility swings."
            )
        else:  # moderate
            note = (
                f"Personalized for Moderate Profile ({horizon.capitalize()}-term horizon): "
                f"Balancing core business profitability and valuation multiples against short-term technical resistance."
            )

        return note
