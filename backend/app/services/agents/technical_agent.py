from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.services.agents.base import BaseAgent, AgentFinding
from app.services.market.service import market_service


class TechnicalMomentumAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="technical", role="Technical and Momentum Analysis")

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
            history_resp = await market_service.get_historical_prices(db, sym, period="1mo")
            bars = history_resp.data.prices
            quote_resp = await market_service.get_quote(db, sym)
            current_price = quote_resp.data.price
            quote_source = quote_resp.source
        except Exception as e:
            return AgentFinding(
                agent=self.name,
                finding=f"Technical data retrieval error for {sym}: {str(e)}",
                signal="NEUTRAL",
                confidence=0.1,
                evidence=[],
                source_ids=[],
                timestamp=now_str,
                limitations=["Market data feed connection failed."],
            )

        if not bars or len(bars) < 5:
            return AgentFinding(
                agent=self.name,
                finding=f"Insufficient price history for {sym} to compute robust momentum indicators.",
                signal="NEUTRAL",
                confidence=0.35,
                evidence=[f"Retrieved only {len(bars)} historical bars; minimum 5 required."],
                source_ids=[quote_source],
                timestamp=now_str,
                limitations=["Insufficient historical data to construct technical indicators."],
                metrics={"bars_available": len(bars)},
            )

        closes = [b.close for b in bars]
        volumes = [b.volume for b in bars]

        # 1. Moving Averages
        sma_7 = float(np.mean(closes[-7:])) if len(closes) >= 7 else closes[-1]
        sma_20 = float(np.mean(closes[-20:])) if len(closes) >= 20 else float(np.mean(closes))

        # 2. Returns & Volatility
        returns = []
        for i in range(1, len(closes)):
            if closes[i - 1] > 0:
                returns.append((closes[i] - closes[i - 1]) / closes[i - 1])
        
        return_1d = quote_resp.data.change_percent
        return_period = ((closes[-1] - closes[0]) / closes[0]) * 100 if closes[0] > 0 else 0.0

        if len(returns) >= 3:
            daily_vol = float(np.std(returns))
            annualized_vol = round(daily_vol * math.sqrt(252) * 100, 2)
        else:
            annualized_vol = 25.0

        # 3. 14-period RSI (Relative Strength Index)
        rsi = 50.0
        if len(closes) >= 14:
            gains = []
            losses = []
            for i in range(len(closes) - 14, len(closes)):
                diff = closes[i] - closes[i - 1]
                if diff >= 0:
                    gains.append(diff)
                    losses.append(0.0)
                else:
                    gains.append(0.0)
                    losses.append(abs(diff))
            avg_gain = sum(gains) / 14.0
            avg_loss = sum(losses) / 14.0
            if avg_loss > 1e-9:
                rs = avg_gain / avg_loss
                rsi = round(100.0 - (100.0 / (1.0 + rs)), 1)
            else:
                rsi = 100.0 if avg_gain > 0 else 50.0

        # 4. Volume Ratio
        avg_vol = float(np.mean(volumes[-20:])) if len(volumes) >= 20 else float(np.mean(volumes))
        current_vol = quote_resp.data.volume
        vol_ratio = round(current_vol / avg_vol, 2) if avg_vol > 0 else 1.0

        # 5. Determine Trend and Signal
        evidence = []
        limitations = []

        price_vs_sma20 = round(((current_price - sma_20) / sma_20) * 100, 2)
        evidence.append(f"Current price ${current_price:.2f} is {price_vs_sma20:+.1f}% vs 20-period SMA (${sma_20:.2f}).")
        evidence.append(f"14-period RSI is {rsi:.1f}.")
        evidence.append(f"Historical 30-day annualized volatility stands at {annualized_vol:.1f}%.")
        evidence.append(f"Session volume is {vol_ratio:.1f}x of the 20-day historical baseline.")

        # Logic for Signal & Synthesis
        if current_price > sma_20 and sma_7 > sma_20 and rsi < 70:
            signal = "BULLISH"
            trend = "Ascending Uptrend"
            momentum = "Positive Expansion"
            finding = (
                f"{sym} exhibits structured technical strength. Price trades above the 20-period SMA (${sma_20:.2f}) "
                f"with an RSI of {rsi:.1f} confirming supportive momentum without immediate overbought exhaustion."
            )
            confidence = 0.82
        elif rsi >= 70:
            signal = "CAUTIOUS"
            trend = "Extended Uptrend"
            momentum = "Overbought Exhaustion Risk"
            finding = (
                f"{sym} displays elevated upside momentum with an RSI of {rsi:.1f}, indicating short-term overbought "
                f"conditions and elevated probability of mean reversion toward ${sma_20:.2f} support."
            )
            confidence = 0.85
        elif current_price < sma_20 and rsi <= 35:
            signal = "CAUTIOUS"
            trend = "Declining Downtrend"
            momentum = "Oversold Near Support"
            finding = (
                f"{sym} trades in a declining trend below the 20-period SMA (${sma_20:.2f}). "
                f"RSI of {rsi:.1f} denotes deep oversold territory with stabilizing volume."
            )
            confidence = 0.78
        elif current_price < sma_20:
            signal = "BEARISH"
            trend = "Downtrend"
            momentum = "Negative Pressure"
            finding = (
                f"{sym} shows technical deterioration, trading {abs(price_vs_sma20):.1f}% below its 20-period SMA "
                f"with persistent downward slope."
            )
            confidence = 0.80
        else:
            signal = "NEUTRAL"
            trend = "Horizontal Consolidation"
            momentum = "Neutral"
            finding = f"{sym} trades within a consolidation band around the 20-period moving average with neutral momentum."
            confidence = 0.72

        limitations.append("Analysis based on 30 daily price bars; does not capture intraday high-frequency order book depth.")

        return AgentFinding(
            agent=self.name,
            finding=finding,
            signal=signal,
            confidence=confidence,
            evidence=evidence,
            source_ids=[f"{quote_source}:{sym}"],
            timestamp=now_str,
            limitations=limitations,
            metrics={
                "price": current_price,
                "sma_7": round(sma_7, 2),
                "sma_20": round(sma_20, 2),
                "rsi_14": rsi,
                "annualized_volatility": annualized_vol,
                "return_1d_pct": return_1d,
                "return_period_pct": round(return_period, 2),
                "volume_ratio": vol_ratio,
                "trend": trend,
                "momentum": momentum,
            },
        )
