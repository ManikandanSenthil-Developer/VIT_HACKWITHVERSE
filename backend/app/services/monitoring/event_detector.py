from datetime import datetime, timezone, timedelta
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.monitoring import MarketEvent
from app.services.monitoring.anomaly_detector import DetectedAnomaly


class EventDetector:
    """
    Transforms raw statistical anomalies into classified MarketEvents.
    Adjusts event severity dynamically based on user portfolio exposure weights
    and deduplicates recurring events to avoid spam.
    """

    @staticmethod
    def classify_and_persist(
        db: Session,
        anomaly: DetectedAnomaly,
        user_portfolio_weight: float = 0.0,
    ) -> MarketEvent:
        # Base severity evaluation
        if anomaly.event_type == "PRICE_ANOMALY":
            abs_mag = abs(anomaly.magnitude)
            if abs_mag >= 6.0:
                base_sev = "HIGH"
            elif abs_mag >= 3.5:
                base_sev = "MEDIUM"
            else:
                base_sev = "LOW"
        elif anomaly.event_type == "VOLUME_SURGE":
            base_sev = "HIGH" if anomaly.magnitude >= 2.0 else "MEDIUM"
        elif anomaly.event_type == "REGULATORY_FILING":
            base_sev = "INFO"
        else:
            base_sev = "MEDIUM"

        # Personalize severity by portfolio weight
        # E.g. A 4% move in a stock representing 35% of portfolio -> upgrade to HIGH/CRITICAL
        final_sev = base_sev
        if user_portfolio_weight >= 30.0:
            if base_sev in ("HIGH", "MEDIUM"):
                final_sev = "CRITICAL" if base_sev == "HIGH" else "HIGH"
        elif user_portfolio_weight >= 15.0:
            if base_sev == "MEDIUM":
                final_sev = "HIGH"

        # Deduplication: Check if identical event on this symbol was created in the last 1 hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        existing_event = (
            db.query(MarketEvent)
            .filter(
                MarketEvent.symbol == anomaly.symbol,
                MarketEvent.event_type == anomaly.event_type,
                MarketEvent.detected_at >= one_hour_ago,
            )
            .first()
        )

        if existing_event:
            # Update severity if higher
            if final_sev in ("CRITICAL", "HIGH") and existing_event.severity not in ("CRITICAL", "HIGH"):
                existing_event.severity = final_sev
                db.commit()
            return existing_event

        event = MarketEvent(
            symbol=anomaly.symbol,
            event_type=anomaly.event_type,
            severity=final_sev,
            title=anomaly.title,
            description=anomaly.description,
            evidence_json=json.dumps(anomaly.evidence),
            source="statistical_surveillance_engine",
            confidence=anomaly.confidence,
            detected_at=datetime.now(timezone.utc),
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event


event_detector = EventDetector()
