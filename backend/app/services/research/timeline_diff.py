from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.intelligence import AnalysisHistory
from app.models.document import Document
from app.models.monitoring import MarketEvent, Alert


class TimelineAndDiffEngine:
    """
    Constructs unified chronological research timelines and computes
    'What Changed?' diffs between historical analyses to track evolving thesis state.
    """

    @staticmethod
    def get_research_timeline(
        db: Session,
        symbol: str,
        user_id: int,
        limit: int = 15,
    ) -> List[Dict[str, Any]]:
        sym = symbol.upper().strip()
        timeline: List[Dict[str, Any]] = []

        # 1. Historical analyses
        analyses = (
            db.query(AnalysisHistory)
            .filter(AnalysisHistory.user_id == user_id, AnalysisHistory.symbol == sym)
            .order_by(AnalysisHistory.created_at.desc())
            .limit(limit)
            .all()
        )
        for a in analyses:
            timeline.append({
                "type": "ANALYSIS",
                "timestamp": a.created_at.isoformat() if a.created_at else None,
                "title": f"Autonomous Multi-Agent Synthesis ({a.overall_assessment})",
                "summary": a.summary[:200] + ("..." if len(a.summary) > 200 else ""),
                "confidence": a.confidence,
                "id": a.id,
            })

        # 2. Documents & Filings
        docs = (
            db.query(Document)
            .filter(Document.company_symbol == sym)
            .order_by(Document.retrieval_date.desc())
            .limit(limit)
            .all()
        )
        for d in docs:
            timeline.append({
                "type": "DOCUMENT",
                "timestamp": d.retrieval_date.isoformat() if d.retrieval_date else None,
                "title": f"Official Filing Ingested: {d.title}",
                "summary": f"{d.document_type} filing indexed with {d.chunk_count} semantic vector chunks.",
                "trust_level": d.trust_level,
                "id": d.id,
            })

        # 3. Market Events
        events = (
            db.query(MarketEvent)
            .filter(MarketEvent.symbol == sym)
            .order_by(MarketEvent.detected_at.desc())
            .limit(limit)
            .all()
        )
        for e in events:
            timeline.append({
                "type": "MARKET_EVENT",
                "timestamp": e.detected_at.isoformat() if e.detected_at else None,
                "title": f"Surveillance Anomaly: {e.title}",
                "summary": e.description,
                "severity": e.severity,
                "id": e.id,
            })

        # 4. User Alerts
        alerts = (
            db.query(Alert)
            .filter(Alert.user_id == user_id, Alert.symbol == sym)
            .order_by(Alert.created_at.desc())
            .limit(limit)
            .all()
        )
        for al in alerts:
            timeline.append({
                "type": "ALERT",
                "timestamp": al.created_at.isoformat() if al.created_at else None,
                "title": f"Proactive Alert: {al.title}",
                "summary": al.explanation,
                "priority": al.priority,
                "id": al.id,
            })

        # Sort all chronological milestones
        timeline.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        return timeline[:limit]

    @staticmethod
    def compute_analysis_diff(
        previous: Dict[str, Any],
        current: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Computes structured differences between two analyses to highlight:
        - Signal trajectory changes (e.g. Bullish -> Cautious)
        - Confidence drift
        - Emerging or resolved conflicts
        - New risks identified
        """
        changes: List[str] = []

        prev_assess = previous.get("overall_assessment", "UNKNOWN")
        curr_assess = current.get("overall_assessment", "UNKNOWN")
        if prev_assess != curr_assess:
            changes.append(f"Consensus signal changed from {prev_assess} to {curr_assess}.")

        prev_conf = previous.get("confidence", 0.0)
        curr_conf = current.get("confidence", 0.0)
        conf_diff = round((curr_conf - prev_conf) * 100, 1)
        if abs(conf_diff) >= 5.0:
            direction = "improved" if conf_diff > 0 else "weakened"
            changes.append(f"Model confidence {direction} by {abs(conf_diff):.1f}% (from {prev_conf*100:.0f}% to {curr_conf*100:.0f}%).")

        prev_agents = {a.get("agent"): a.get("signal") for a in previous.get("agents", [])}
        curr_agents = {a.get("agent"): a.get("signal") for a in current.get("agents", [])}

        for agent_name, curr_sig in curr_agents.items():
            prev_sig = prev_agents.get(agent_name)
            if prev_sig and prev_sig != curr_sig:
                changes.append(f"{agent_name.capitalize()} Agent shifted from {prev_sig} to {curr_sig}.")

        prev_conflicts = len(previous.get("conflicts", []))
        curr_conflicts = len(current.get("conflicts", []))
        if prev_conflicts != curr_conflicts:
            changes.append(f"Active signal conflicts changed from {prev_conflicts} to {curr_conflicts}.")

        if not changes:
            changes.append("No material deviation detected in core agent signals or consensus confidence.")

        return {
            "symbol": current.get("symbol", previous.get("symbol", "N/A")),
            "previous_date": previous.get("created_at"),
            "current_date": current.get("created_at"),
            "has_material_change": bool(prev_assess != curr_assess or abs(conf_diff) >= 5.0),
            "changes": changes,
            "previous_assessment": prev_assess,
            "current_assessment": curr_assess,
            "confidence_delta": conf_diff,
        }


timeline_diff_engine = TimelineAndDiffEngine()
