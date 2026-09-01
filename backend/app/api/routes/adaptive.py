import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.adaptive import ResearchHypothesis, PredictionRecord

from app.services.evaluation.agent_evaluator import agent_evaluator_service
from app.services.orchestration.dynamic_router import dynamic_router
from app.services.graph.knowledge_graph import knowledge_graph_service
from app.services.graph.event_impact_engine import event_impact_engine
from app.services.evaluation.claim_verifier import claim_verifier_service
from app.services.research.adaptive_research import adaptive_research_service

router = APIRouter()


# ─────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────
class RouteQueryRequest(BaseModel):
    query: str


class EventImpactRequest(BaseModel):
    event_title: str
    affected_symbols: List[str] = Field(default_factory=lambda: ["NVDA"])
    affected_sectors: List[str] = Field(default_factory=lambda: ["technology"])
    severity: str = "HIGH"


class ClaimVerifyRequest(BaseModel):
    symbol: str
    summary_text: str
    agent_signals: dict = Field(default_factory=dict)
    evidence_items: List[str] = Field(default_factory=list)


class HypothesisCreateRequest(BaseModel):
    symbol: str
    title: str
    hypothesis_text: str
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)


class PredictionCreateRequest(BaseModel):
    symbol: str
    predicted_metric: str
    predicted_min: Optional[float] = None
    predicted_max: Optional[float] = None
    predicted_value: Optional[float] = None
    confidence: float = 0.80
    model_name: str = "scenario_engine_v1"


class PredictionEvaluateRequest(BaseModel):
    actual_observed_value: float


# ─────────────────────────────────────────────
# 1. Agent Performance Telemetry
# ─────────────────────────────────────────────
@router.get("/agents/performance")
def get_agent_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns empirical reliability statistics for all specialized agents."""
    return {
        "agents": agent_evaluator_service.get_all_reliability(db),
        "disclaimer": "Reliability measures software execution and evidence extraction, NOT market prediction accuracy.",
    }


# ─────────────────────────────────────────────
# 2. Dynamic Agent Routing
# ─────────────────────────────────────────────
@router.post("/route")
def route_query(
    payload: RouteQueryRequest,
    current_user: User = Depends(get_current_user),
):
    """Dynamically selects agents based on query intent and explains the routing decision."""
    decision = dynamic_router.route_query(payload.query)
    return decision.model_dump()


# ─────────────────────────────────────────────
# 3. Knowledge Graph
# ─────────────────────────────────────────────
@router.get("/graph/company/{symbol}")
def get_company_graph(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves the knowledge graph neighbourhood for a company (peers, sectors, events, filings)."""
    return knowledge_graph_service.get_company_subgraph(db, symbol)


@router.get("/graph/portfolio")
def get_portfolio_graph(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns user-authorized portfolio exposure graph (holdings → sectors → events)."""
    return knowledge_graph_service.get_portfolio_subgraph(db, current_user.id)


# ─────────────────────────────────────────────
# 4. Event Impact Cascade
# ─────────────────────────────────────────────
@router.post("/event-impact")
def compute_event_impact(
    payload: EventImpactRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Computes the 5-layer EVENT → COMPANIES → SECTORS → PORTFOLIO → RISK cascade."""
    return event_impact_engine.evaluate_event_impact(
        db=db,
        user_id=current_user.id,
        event_title=payload.event_title,
        affected_symbols=payload.affected_symbols,
        affected_sectors=payload.affected_sectors,
        severity=payload.severity,
    )


@router.get("/alerts/{alert_id}/why")
def explain_alert_trigger(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns clickable 5-step 'Why did I get this alert?' attribution."""
    return event_impact_engine.explain_alert_trigger(db, alert_id, current_user.id)


# ─────────────────────────────────────────────
# 5. Claim Verification & Numeric Consistency
# ─────────────────────────────────────────────
@router.post("/verify-claims")
def verify_claims(
    payload: ClaimVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verifies AI claims against database ground truth and detects contradictions."""
    result = claim_verifier_service.verify_ai_response(
        db=db,
        symbol=payload.symbol,
        summary_text=payload.summary_text,
        agent_signals=payload.agent_signals,
        evidence_items=payload.evidence_items,
    )
    return result.model_dump()


# ─────────────────────────────────────────────
# 6. Research Completeness & Gap Analysis
# ─────────────────────────────────────────────
@router.get("/research/completeness/{symbol}")
def get_research_completeness(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """Returns multidimensional research completeness scorecard with unknowns and next-best-question."""
    scorecard = adaptive_research_service.evaluate_research_completeness(symbol)
    return scorecard.model_dump()


# ─────────────────────────────────────────────
# 7. Personalized Research Feed
# ─────────────────────────────────────────────
@router.get("/feed")
def get_personalized_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generates a personalized 'FOR YOU' intelligence feed based on research history."""
    # Compile from analysis history and portfolio holdings
    from app.models.intelligence import AnalysisHistory
    from app.models.portfolio import Portfolio

    analyses = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.user_id == current_user.id)
        .order_by(AnalysisHistory.created_at.desc())
        .limit(10)
        .all()
    )

    recent_symbols = list({a.symbol for a in analyses}) if analyses else ["NVDA"]

    feed_items = []
    for sym in recent_symbols[:5]:
        feed_items.append({
            "symbol": sym,
            "type": "RESEARCH_UPDATE",
            "title": f"New intelligence available for {sym}",
            "reason_shown": f"You previously researched {sym} in your last session.",
            "priority": "MEDIUM",
        })

    # Portfolio-based items
    ports = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
    for p in ports:
        for h in p.holdings[:3]:
            if h.symbol not in recent_symbols:
                feed_items.append({
                    "symbol": h.symbol,
                    "type": "HOLDING_INTELLIGENCE",
                    "title": f"Continuous monitoring update for {h.symbol}",
                    "reason_shown": f"{h.symbol} is in your active portfolio (Qty: {h.quantity}).",
                    "priority": "HIGH",
                })

    return {
        "user_id": current_user.id,
        "feed_items": feed_items,
        "total_items": len(feed_items),
        "explanation": "Items are ranked by portfolio exposure and recent research activity.",
    }


# ─────────────────────────────────────────────
# 8. Intelligence Diff ("What Changed?")
# ─────────────────────────────────────────────
@router.get("/memory/diff/{symbol}")
def get_intelligence_diff(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compares previous vs. current intelligence for a symbol to highlight what changed."""
    from app.models.intelligence import AnalysisHistory

    analyses = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.user_id == current_user.id, AnalysisHistory.symbol == symbol.upper())
        .order_by(AnalysisHistory.created_at.desc())
        .limit(2)
        .all()
    )

    if len(analyses) < 2:
        return {
            "symbol": symbol.upper(),
            "has_previous_analysis": False,
            "message": f"No previous analysis found for {symbol.upper()}. Run an analysis first to enable intelligence diffs.",
            "diff": None,
        }

    current = analyses[0]
    previous = analyses[1]

    return {
        "symbol": symbol.upper(),
        "has_previous_analysis": True,
        "current_analysis": {
            "date": current.created_at.isoformat(),
            "assessment": current.overall_assessment,
            "confidence": current.confidence,
            "request_id": current.request_id,
        },
        "previous_analysis": {
            "date": previous.created_at.isoformat(),
            "assessment": previous.overall_assessment,
            "confidence": previous.confidence,
            "request_id": previous.request_id,
        },
        "diff": {
            "assessment_changed": current.overall_assessment != previous.overall_assessment,
            "confidence_delta": round(current.confidence - previous.confidence, 3),
            "time_elapsed_description": f"From {previous.created_at.strftime('%Y-%m-%d')} to {current.created_at.strftime('%Y-%m-%d')}",
        },
    }


# ─────────────────────────────────────────────
# 9. Hypothesis Tracking
# ─────────────────────────────────────────────
@router.post("/hypotheses")
def create_hypothesis(
    payload: HypothesisCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creates a new research hypothesis for tracking and evidence evaluation."""
    hyp = ResearchHypothesis(
        user_id=current_user.id,
        symbol=payload.symbol.upper(),
        title=payload.title,
        hypothesis_text=payload.hypothesis_text,
        supporting_evidence_json=json.dumps(payload.supporting_evidence),
        contradicting_evidence_json=json.dumps(payload.contradicting_evidence),
        status="UNRESOLVED",
        confidence=0.70,
    )
    db.add(hyp)
    db.commit()
    db.refresh(hyp)

    return {
        "id": hyp.id,
        "symbol": hyp.symbol,
        "title": hyp.title,
        "status": hyp.status,
        "created_at": hyp.created_at.isoformat(),
    }


@router.get("/hypotheses")
def list_hypotheses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists all research hypotheses for the authenticated user."""
    hyps = (
        db.query(ResearchHypothesis)
        .filter(ResearchHypothesis.user_id == current_user.id)
        .order_by(ResearchHypothesis.created_at.desc())
        .all()
    )
    return {
        "hypotheses": [
            {
                "id": h.id,
                "symbol": h.symbol,
                "title": h.title,
                "hypothesis_text": h.hypothesis_text,
                "status": h.status,
                "confidence": h.confidence,
                "supporting_evidence": json.loads(h.supporting_evidence_json) if h.supporting_evidence_json else [],
                "contradicting_evidence": json.loads(h.contradicting_evidence_json) if h.contradicting_evidence_json else [],
                "created_at": h.created_at.isoformat(),
            }
            for h in hyps
        ],
        "total": len(hyps),
    }


# ─────────────────────────────────────────────
# 10. Prediction Journal & Calibration
# ─────────────────────────────────────────────
@router.post("/predictions")
def create_prediction(
    payload: PredictionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Records a prediction for subsequent outcome evaluation."""
    pred = PredictionRecord(
        user_id=current_user.id,
        symbol=payload.symbol.upper(),
        model_name=payload.model_name,
        predicted_metric=payload.predicted_metric,
        predicted_min=payload.predicted_min,
        predicted_max=payload.predicted_max,
        predicted_value=payload.predicted_value,
        confidence=payload.confidence,
        evaluation_status="PENDING_OBSERVATION",
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    return {
        "id": pred.id,
        "symbol": pred.symbol,
        "predicted_metric": pred.predicted_metric,
        "status": pred.evaluation_status,
        "created_at": pred.created_at.isoformat(),
    }


@router.post("/predictions/{prediction_id}/evaluate")
def evaluate_prediction(
    prediction_id: int,
    payload: PredictionEvaluateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluates a prediction against actual observed outcome."""
    pred = (
        db.query(PredictionRecord)
        .filter(PredictionRecord.id == prediction_id, PredictionRecord.user_id == current_user.id)
        .first()
    )
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found.")

    pred.actual_observed_value = payload.actual_observed_value
    pred.evaluated_at = datetime.now(timezone.utc)

    # Evaluate against range
    if pred.predicted_min is not None and pred.predicted_max is not None:
        if pred.predicted_min <= payload.actual_observed_value <= pred.predicted_max:
            pred.evaluation_status = "WITHIN_RANGE"
        else:
            pred.evaluation_status = "OUTSIDE_RANGE"
    elif pred.predicted_value is not None:
        divergence = abs(payload.actual_observed_value - pred.predicted_value) / max(pred.predicted_value, 0.01) * 100
        if divergence <= 10.0:
            pred.evaluation_status = "WITHIN_RANGE"
        else:
            pred.evaluation_status = "OUTSIDE_RANGE"
    else:
        pred.evaluation_status = "EVALUATED"

    db.commit()
    db.refresh(pred)

    return {
        "id": pred.id,
        "symbol": pred.symbol,
        "predicted_metric": pred.predicted_metric,
        "predicted_value": pred.predicted_value,
        "predicted_min": pred.predicted_min,
        "predicted_max": pred.predicted_max,
        "actual_observed_value": pred.actual_observed_value,
        "evaluation_status": pred.evaluation_status,
        "confidence": pred.confidence,
        "evaluated_at": pred.evaluated_at.isoformat(),
    }


@router.get("/predictions/calibration")
def get_prediction_calibration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns model confidence calibration telemetry."""
    preds = (
        db.query(PredictionRecord)
        .filter(PredictionRecord.user_id == current_user.id)
        .all()
    )
    evaluated = [p for p in preds if p.evaluation_status in ("WITHIN_RANGE", "OUTSIDE_RANGE")]
    within = sum(1 for p in evaluated if p.evaluation_status == "WITHIN_RANGE")
    outside = sum(1 for p in evaluated if p.evaluation_status == "OUTSIDE_RANGE")
    total_eval = len(evaluated)
    avg_conf = round(sum(p.confidence for p in evaluated) / max(total_eval, 1), 2)

    return {
        "total_predictions": len(preds),
        "evaluated_predictions": total_eval,
        "within_range": within,
        "outside_range": outside,
        "accuracy_pct": round((within / max(total_eval, 1)) * 100.0, 1),
        "average_confidence": avg_conf,
        "calibration_note": "Insufficient data for statistically significant calibration." if total_eval < 20 else "Calibration active.",
        "disclaimer": "Historical prediction accuracy does not guarantee future prediction quality.",
    }
