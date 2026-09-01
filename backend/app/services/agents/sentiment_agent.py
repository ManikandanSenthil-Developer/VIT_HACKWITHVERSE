from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.services.agents.base import BaseAgent, AgentFinding
from app.services.market.service import market_service


class SentimentMarketAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="sentiment", role="Market Sentiment and Anomaly Detection")

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
            quote_resp = await market_service.get_quote(db, sym)
            history_resp = await market_service.get_historical_prices(db, sym, period="1mo")
            quote = quote_resp.data
            bars = history_resp.data.prices
        except Exception as e:
            return AgentFinding(
                agent=self.name,
                finding=f"Market telemetry unavailable for {sym}: {str(e)}",
                signal="NEUTRAL",
                confidence=0.1,
                evidence=[],
                source_ids=[],
                timestamp=now_str,
                limitations=["Real-time trading volume telemetry offline."],
            )

        volumes = [b.volume for b in bars] if bars else []
        avg_vol = float(np.mean(volumes)) if volumes else quote.volume
        vol_ratio = round(quote.volume / avg_vol, 2) if avg_vol > 0 else 1.0

        daily_change = quote.change_percent
        is_high_volume = vol_ratio > 1.35
        is_extreme_move = abs(daily_change) > 3.5

        # Strictly distinguish FACT from MODEL INTERPRETATION
        facts = [
            f"FACT: {sym} recorded a 24-hour price change of {daily_change:+.2f}%.",
            f"FACT: Session volume reached {quote.volume:,.0f} shares ({vol_ratio:.2f}x of 30-day baseline).",
        ]

        interpretations = []
        if is_high_volume and daily_change > 1.5:
            signal = "BULLISH"
            confidence = 0.82
            interpretations.append(
                "MODEL INTERPRETATION: High-volume upward expansion suggests strong institutional accumulation and aggressive bid support."
            )
            finding = (
                f"{sym} displays constructive institutional sentiment with above-average trading volume ({vol_ratio:.2f}x) "
                f"supporting positive price advancement."
            )
        elif is_high_volume and daily_change < -1.5:
            signal = "BEARISH"
            confidence = 0.80
            interpretations.append(
                "MODEL INTERPRETATION: Elevated turnover during negative price discovery indicates aggressive distribution or institutional derisking."
            )
            finding = (
                f"{sym} reflects risk-off market sentiment characterized by above-average volume on down-draft trading."
            )
        elif is_extreme_move:
            signal = "CAUTIOUS"
            confidence = 0.76
            interpretations.append(
                "MODEL INTERPRETATION: Elevated intra-session price dispersion signals heightened volatility or impending catalyst pricing."
            )
            finding = f"{sym} experiences elevated volatility anomalies requiring close risk monitoring."
        else:
            signal = "NEUTRAL"
            confidence = 0.70
            interpretations.append(
                "MODEL INTERPRETATION: Volume and price displacement reside within normal historical distribution curves."
            )
            finding = f"{sym} reflects balanced, stable market sentiment without abnormal volume spikes or order flow skew."

        evidence = facts + interpretations

        return AgentFinding(
            agent=self.name,
            finding=finding,
            signal=signal,
            confidence=confidence,
            evidence=evidence,
            source_ids=[f"{quote_resp.source}:{sym}:telemetry"],
            timestamp=now_str,
            limitations=[
                "Sentiment score is an algorithmic interpretation derived from volume/price anomalies, not an objective consensus metric."
            ],
            metrics={
                "volume_ratio": vol_ratio,
                "daily_change_pct": daily_change,
                "is_volume_anomaly": is_high_volume,
                "is_volatility_anomaly": is_extreme_move,
            },
        )
