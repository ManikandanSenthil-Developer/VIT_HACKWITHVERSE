from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.adaptive import AgentExecutionMetric


class AgentEvaluatorService:
    """
    Evaluates and records empirical performance metrics for specialized agents.
    Calculates operational reliability (availability, latency, evidence counts).
    Strictly differentiates operational reliability from investment predictive accuracy.
    """

    KNOWN_AGENTS = [
        "technical",
        "fundamental",
        "sentiment",
        "rag",
        "counterargument",
        "risk",
    ]

    @classmethod
    def record_execution(
        cls,
        db: Session,
        agent_name: str,
        task_type: str,
        execution_time_ms: float,
        evidence_count: int = 0,
        confidence: float = 0.85,
        status: str = "SUCCESS",
        analysis_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> AgentExecutionMetric:
        """Records telemetry for an individual agent execution run."""
        metric = AgentExecutionMetric(
            agent_name=agent_name.lower().strip(),
            task_type=task_type,
            execution_time_ms=round(execution_time_ms, 2),
            evidence_count=evidence_count,
            confidence=round(confidence, 2),
            status=status.upper(),
            analysis_id=analysis_id,
            error_message=error_message,
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    @classmethod
    def get_agent_reliability(cls, db: Session, agent_name: str) -> Dict[str, Any]:
        """Calculates measurable historical reliability for a specific agent."""
        clean_name = agent_name.lower().strip()
        metrics = db.query(AgentExecutionMetric).filter(AgentExecutionMetric.agent_name == clean_name).all()

        total = len(metrics)
        if total == 0:
            # Seeded baseline for cold start
            return {
                "agent_name": clean_name,
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "success_rate_pct": 100.0,
                "avg_latency_ms": 150.0,
                "avg_confidence": 0.85,
                "evidence_extracted_total": 0,
                "evaluation_notice": "NO STORED RUNS. Reliability baseline active. Does NOT imply investment accuracy.",
            }

        successes = sum(1 for m in metrics if m.status == "SUCCESS")
        failures = total - successes
        avg_lat = round(sum(m.execution_time_ms for m in metrics) / total, 1)
        avg_conf = round(sum(m.confidence for m in metrics) / total, 2)
        total_ev = sum(m.evidence_count for m in metrics)

        return {
            "agent_name": clean_name,
            "total_runs": total,
            "successful_runs": successes,
            "failed_runs": failures,
            "success_rate_pct": round((successes / total) * 100.0, 1),
            "avg_latency_ms": avg_lat,
            "avg_confidence": avg_conf,
            "evidence_extracted_total": total_ev,
            "evaluation_notice": "Empirical reliability reflects software execution and evidence extraction, NOT market prediction accuracy.",
        }

    @classmethod
    def get_all_reliability(cls, db: Session) -> List[Dict[str, Any]]:
        """Returns reliability telemetry across all specialized agents."""
        return [cls.get_agent_reliability(db, agent) for agent in cls.KNOWN_AGENTS]


agent_evaluator_service = AgentEvaluatorService()
