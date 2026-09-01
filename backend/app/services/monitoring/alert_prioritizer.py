from datetime import datetime, timezone, timedelta
import json
from typing import Optional
from sqlalchemy.orm import Session
from app.models.monitoring import Alert, MarketEvent


class AlertPrioritizer:
    """
    Evaluates alert priority (URGENT, IMPORTANT, FYI), enforces deduplication,
    and clusters recurring signals to prevent alert fatigue.
    """

    @staticmethod
    def prioritize_and_persist(
        db: Session,
        user_id: int,
        event: MarketEvent,
        portfolio_weight: float,
        is_in_watchlist: bool,
        synthesis_data: Optional[dict] = None,
    ) -> Alert:
        # Priority mapping:
        # High portfolio weight (> 20%) or CRITICAL severity -> URGENT
        # In watchlist or MEDIUM/HIGH severity -> IMPORTANT
        # Otherwise -> FYI
        if portfolio_weight >= 20.0 or event.severity in ("CRITICAL", "HIGH"):
            priority = "URGENT" if portfolio_weight >= 20.0 else "IMPORTANT"
        elif is_in_watchlist or event.severity == "MEDIUM":
            priority = "IMPORTANT"
        else:
            priority = "FYI"

        # Deduplication check: Has an alert for this user and symbol been created in the last 2 hours?
        two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.user_id == user_id,
                Alert.symbol == event.symbol,
                Alert.status.in_(["NEW", "SEEN"]),
                Alert.created_at >= two_hours_ago,
            )
            .first()
        )

        if existing_alert:
            # Cluster existing alert rather than generating redundant noise
            existing_alert.title = f"Multiple market signals detected for {event.symbol}"
            existing_alert.explanation = (
                f"MATS continuous surveillance has detected multiple converging anomalies on {event.symbol}. "
                f"Latest event: {event.title}. {event.description}"
            )
            if priority == "URGENT":
                existing_alert.priority = "URGENT"
            if synthesis_data:
                existing_alert.agent_synthesis_json = json.dumps(synthesis_data)
            db.commit()
            db.refresh(existing_alert)
            return existing_alert

        # Formulate proactive explanation
        explanation = (
            f"MATS automated surveillance flagged {event.symbol} due to {event.title.lower()}. "
            f"{'You hold this asset with a ' + str(round(portfolio_weight, 1)) + '% allocation weight.' if portfolio_weight > 0 else 'This security resides in your priority watchlist.'} "
            f"Autonomous multi-agent investigation completed with {int(event.confidence * 100)}% confidence."
        )

        alert = Alert(
            user_id=user_id,
            event_id=event.id,
            symbol=event.symbol,
            priority=priority,
            severity=event.severity,
            title=event.title,
            explanation=explanation,
            agent_synthesis_json=json.dumps(synthesis_data) if synthesis_data else None,
            status="NEW",
            feedback="UNSPECIFIED",
            created_at=datetime.now(timezone.utc),
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert


alert_prioritizer = AlertPrioritizer()
