from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.intelligence import AnalysisHistory
from app.models.monitoring import Alert
from app.models.user import User
from app.schemas.intelligence import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisHistoryItem,
    AgentStatusInfo,
)
from app.schemas.monitoring import DailyBriefResponse, AlertItem
from app.services.agents.orchestrator import orchestrator
from app.services.monitoring.daily_brief import daily_brief_service

router = APIRouter()


from app.core.rate_limiter import rate_limit_dependency
from app.services.audit.audit_service import audit_service


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit_dependency(max_requests=25, window_seconds=60, by_user=True, action="ai_analyze"))],
)
async def analyze_financial_target(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Execute multi-agent autonomous financial research analysis.
    Decomposes user query across Technical, Fundamental, Sentiment, and RAG Research agents,
    detects signal conflicts, synthesizes evidence, and applies investor profile personalization.
    """
    result = await orchestrator.run_analysis(db=db, user_id=current_user.id, request=request)
    audit_service.log_event(
        db=db,
        action="AI_ANALYSIS",
        user_id=current_user.id,
        resource_type="Security",
        resource_id=request.symbol,
        details={
            "symbol": request.symbol,
            "analysis_type": request.analysis_type,
            "overall_assessment": result.overall_assessment,
            "confidence": result.confidence,
        },
        status="SUCCESS",
    )
    return result


@router.get("/history", response_model=List[AnalysisHistoryItem])
def get_analysis_history(
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve history of prior multi-agent intelligence requests for authenticated user."""
    return (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.user_id == current_user.id)
        .order_by(AnalysisHistory.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/agents", response_model=List[AgentStatusInfo])
def get_available_agents() -> Any:
    """List all specialized autonomous agents, roles, and real-time operational status."""
    return [
        AgentStatusInfo(
            agent_id="technical",
            name="Technical & Momentum Agent",
            role="Evaluates OHLCV bars, moving averages, 14-period RSI, volatility, and price trend.",
            status="online",
            capabilities=["trend_detection", "momentum_oscillator", "volatility_modelling"],
        ),
        AgentStatusInfo(
            agent_id="fundamental",
            name="Fundamental Analysis Agent",
            role="Audits reported income statements, revenue, P/E multiples, margins, and debt leverage.",
            status="online",
            capabilities=["balance_sheet_audit", "valuation_multiples", "cash_flow_durability"],
        ),
        AgentStatusInfo(
            agent_id="sentiment",
            name="Sentiment & Market Anomaly Agent",
            role="Identifies volume anomalies and intra-session price displacement vs historical distributions.",
            status="online",
            capabilities=["volume_anomaly_detection", "volatility_dispersion", "fact_interpretation_separation"],
        ),
        AgentStatusInfo(
            agent_id="rag_research",
            name="RAG Regulatory Research Agent",
            role="Performs grounded semantic retrieval across SEC 10-K and 10-Q regulatory filings.",
            status="online",
            capabilities=["semantic_vector_retrieval", "provenance_citations", "zero_hallucination_guard"],
        ),
    ]


@router.get("/daily-brief", response_model=DailyBriefResponse)
async def get_daily_intelligence_brief(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Generate synthesized daily financial intelligence brief for current user."""
    return await daily_brief_service.generate_brief(db=db, user_id=current_user.id)


@router.get("/feed", response_model=List[AlertItem])
def get_intelligence_feed(
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve prioritized proactive intelligence feed for user dashboard."""
    return (
        db.query(Alert)
        .filter(Alert.user_id == current_user.id, Alert.status != "DISMISSED")
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/{analysis_id}", response_model=AnalysisHistoryItem)
def get_analysis_by_id(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve specific past analysis record by ID."""
    record = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.id == analysis_id, AnalysisHistory.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found.",
        )
    return record
