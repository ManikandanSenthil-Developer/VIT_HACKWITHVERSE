from typing import Dict, List, Optional
from app.schemas.risk import PositionHealth, SectorExposure, RiskScoreExplanation, RiskScoreFactor


class RiskEngine:
    """
    Deterministic, fully explainable portfolio risk assessment engine.
    Eliminates black-box scoring by attributing exact mathematical weights to
    concentration, sector exposure, historical volatility, drawdown, and active anomalies.
    """

    @staticmethod
    def evaluate_risk(
        positions: List[PositionHealth],
        sector_exposures: List[SectorExposure],
        metrics: Dict[str, float],
        active_events_count: int = 0,
        annualized_vol: float = 38.5,
        max_drawdown: float = 18.2,
    ) -> RiskScoreExplanation:
        reasons: List[str] = []
        factors: List[RiskScoreFactor] = []

        top_weight = metrics.get("top_weight", 0.0)
        top_sector_weight = sector_exposures[0].weight_percent if sector_exposures else 0.0
        top_sector_name = sector_exposures[0].sector if sector_exposures else "Diversified"

        # 1. Asset Concentration (Weight: 25%)
        if top_weight > 50.0:
            conc_score = 95.0
            reasons.append(f"Critical asset concentration: Single top position accounts for {top_weight:.1f}% of portfolio equity.")
        elif top_weight > 35.0:
            conc_score = 75.0
            reasons.append(f"Elevated asset concentration: Single position represents {top_weight:.1f}% of total portfolio value.")
        elif top_weight > 20.0:
            conc_score = 45.0
            reasons.append(f"Moderate position sizing: Largest holding sits at {top_weight:.1f}%.")
        else:
            conc_score = 15.0
            reasons.append(f"Well-balanced asset distribution: Largest holding is limited to {top_weight:.1f}%.")

        conc_contrib = round(0.25 * conc_score, 2)
        factors.append(
            RiskScoreFactor(
                factor="Asset Concentration",
                weight=0.25,
                contribution=conc_contrib,
                description=f"Largest position weight: {top_weight:.1f}% (Baseline benchmark <= 20.0%).",
            )
        )

        # 2. Sector Concentration (Weight: 15%)
        if top_sector_weight > 50.0:
            sec_score = 85.0
            reasons.append(f"High sector concentration: {top_sector_name} comprises {top_sector_weight:.1f}% of exposures.")
        elif top_sector_weight > 30.0:
            sec_score = 55.0
            reasons.append(f"Moderate sector bias toward {top_sector_name} ({top_sector_weight:.1f}%).")
        else:
            sec_score = 20.0
            reasons.append(f"Healthy multi-sector diversification ({top_sector_weight:.1f}% max sector exposure).")

        sec_contrib = round(0.15 * sec_score, 2)
        factors.append(
            RiskScoreFactor(
                factor="Sector Concentration",
                weight=0.15,
                contribution=sec_contrib,
                description=f"Primary sector ({top_sector_name}) exposure: {top_sector_weight:.1f}%.",
            )
        )

        # 3. Holding Volatility (Weight: 25%)
        if annualized_vol > 50.0:
            vol_score = 95.0
            reasons.append(f"Extreme historical price volatility ({annualized_vol:.1f}% annualized).")
        elif annualized_vol > 35.0:
            vol_score = 70.0
            reasons.append(f"Elevated price variance across high-beta growth holdings ({annualized_vol:.1f}% annualized).")
        elif annualized_vol > 20.0:
            vol_score = 40.0
            reasons.append(f"Moderate, standard market volatility ({annualized_vol:.1f}% annualized).")
        else:
            vol_score = 15.0
            reasons.append(f"Low, defensive price volatility profile ({annualized_vol:.1f}% annualized).")

        vol_contrib = round(0.25 * vol_score, 2)
        factors.append(
            RiskScoreFactor(
                factor="Portfolio Volatility",
                weight=0.25,
                contribution=vol_contrib,
                description=f"Weighted annualized historical volatility: {annualized_vol:.1f}%.",
            )
        )

        # 4. Maximum Historical Drawdown (Weight: 20%)
        if max_drawdown > 30.0:
            dd_score = 90.0
            reasons.append(f"High peak-to-trough historical drawdown exposure ({max_drawdown:.1f}%).")
        elif max_drawdown > 18.0:
            dd_score = 65.0
            reasons.append(f"Moderate historical peak-to-trough retracement profile ({max_drawdown:.1f}%).")
        else:
            dd_score = 25.0
            reasons.append(f"Resilient capital preservation with low maximum drawdown ({max_drawdown:.1f}%).")

        dd_contrib = round(0.20 * dd_score, 2)
        factors.append(
            RiskScoreFactor(
                factor="Historical Drawdown",
                weight=0.20,
                contribution=dd_contrib,
                description=f"Maximum historical peak-to-trough retracement: {max_drawdown:.1f}%.",
            )
        )

        # 5. Active Market Events / Telemetry Anomalies (Weight: 15%)
        if active_events_count >= 2:
            event_score = 85.0
            reasons.append(f"Multiple active market anomalies ({active_events_count}) currently detected on portfolio securities.")
        elif active_events_count == 1:
            event_score = 55.0
            reasons.append("Active price or volume anomaly currently flags one portfolio holding.")
        else:
            event_score = 10.0
            reasons.append("No active statistical market anomalies detected across holdings.")

        event_contrib = round(0.15 * event_score, 2)
        factors.append(
            RiskScoreFactor(
                factor="Active Market Events",
                weight=0.15,
                contribution=event_contrib,
                description=f"Active statistical anomalies currently detected: {active_events_count}.",
            )
        )

        total_score = int(round(conc_contrib + sec_contrib + vol_contrib + dd_contrib + event_contrib))
        total_score = max(5, min(95, total_score))

        if total_score >= 80:
            risk_level = "CRITICAL"
        elif total_score >= 60:
            risk_level = "HIGH"
        elif total_score >= 35:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        return RiskScoreExplanation(
            risk_level=risk_level,
            risk_score=total_score,
            reasons=reasons,
            factor_contributions=factors,
        )


risk_engine = RiskEngine()
