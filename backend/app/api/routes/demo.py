"""
MATS Demo Resilience & Scenario Controller
Provides deterministic demo dataset status, state reset, and 3 distinct hackathon demo scenarios.
"""
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.watchlist import Watchlist
from app.models.monitoring import Alert, MarketEvent
from app.models.document import Document
from app.models.market import Company, MarketSnapshot
from app.schemas.intelligence import AnalysisRequest, AnalysisResponse
from app.services.agents.orchestrator import orchestrator
from app.services.monitoring.event_detector import event_detector
from app.services.monitoring.alert_prioritizer import alert_prioritizer
from app.services.risk.portfolio_intelligence import portfolio_intelligence_service
from app.services.risk.risk_engine import risk_engine
from app.services.audit.audit_service import audit_service

from app.services.monitoring.anomaly_detector import DetectedAnomaly

router = APIRouter()


@router.get("/status")
def get_demo_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Check readiness and presence of deterministic demo dataset."""
    demo_user = db.query(User).filter(User.email == "demo@mats.ai").first()
    companies_count = db.query(Company).count()
    documents_count = db.query(Document).count()
    snapshots_count = db.query(MarketSnapshot).count()

    portfolio_ready = False
    holdings_count = 0
    if demo_user:
        port = db.query(Portfolio).filter(Portfolio.user_id == demo_user.id).first()
        if port:
            holdings_count = db.query(Holding).filter(Holding.portfolio_id == port.id).count()
            portfolio_ready = holdings_count >= 3

    is_ready = bool(demo_user and portfolio_ready and companies_count >= 4 and documents_count >= 2)

    return {
        "status": "READY FOR DEMO" if is_ready else "DEMO DATA INCOMPLETE",
        "demo_user_exists": bool(demo_user),
        "demo_portfolio_ready": portfolio_ready,
        "demo_holdings_count": holdings_count,
        "companies_count": companies_count,
        "documents_count": documents_count,
        "market_snapshots_count": snapshots_count,
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/reset")
def reset_demo_environment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """
    Safely reset demo state for the authenticated user (or demo account).
    Re-seeds baseline holdings and clears transient simulated demo alerts.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(
            user_id=current_user.id,
            name="Core Alpha Growth Portfolio",
            description="Reset baseline demo portfolio",
            cash_balance=18500.0,
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    # Clear user's alerts and holdings
    db.query(Alert).filter(Alert.user_id == current_user.id).delete()
    db.query(Holding).filter(Holding.portfolio_id == portfolio.id).delete()
    db.commit()

    # Re-seed pristine demo holdings
    baseline_holdings = [
        {"symbol": "NVDA", "quantity": 30.0, "buy_price": 118.50, "current_price": 128.40},
        {"symbol": "AAPL", "quantity": 40.0, "buy_price": 195.00, "current_price": 224.20},
        {"symbol": "MSFT", "quantity": 25.0, "buy_price": 412.00, "current_price": 448.50},
        {"symbol": "JNJ", "quantity": 35.0, "buy_price": 156.00, "current_price": 162.80},
    ]
    for h in baseline_holdings:
        db.add(Holding(
            portfolio_id=portfolio.id,
            symbol=h["symbol"],
            quantity=h["quantity"],
            buy_price=h["buy_price"],
            current_value=h["quantity"] * h["current_price"],
        ))
    db.commit()

    audit_service.log_event(
        db=db,
        action="DEMO_RESET",
        user_id=current_user.id,
        resource_type="DemoEnvironment",
        details={"status": "pristine_baseline_restored", "holdings_count": 4},
        status="SUCCESS",
    )

    return {
        "status": "success",
        "message": "Demo environment reset to pristine baseline. 4 holdings re-seeded, temporary alerts cleared.",
    }


@router.post("/scenarios/1", response_model=AnalysisResponse)
async def run_scenario_1_normal_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    DEMO SCENARIO 1: Comprehensive Multi-Agent Analysis
    Demonstrates harmonious agent execution on NVDA with high confidence and SEC 10-K RAG citations.
    """
    req = AnalysisRequest(
        query="Perform a complete research-oriented analysis of NVDA for long-term investment.",
        symbol="NVDA",
        analysis_type="comprehensive",
    )
    return await orchestrator.run_analysis(db=db, user_id=current_user.id, request=req)


@router.post("/scenarios/2", response_model=AnalysisResponse)
async def run_scenario_2_agent_disagreement(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    DEMO SCENARIO 2: Transparent Agent Disagreement & Conflict Detection
    Demonstrates genuine signal clash (Technical Momentum Bullish vs Fundamental Valuation Bearish) on TSLA.
    """
    req = AnalysisRequest(
        query="Examine technical momentum and valuation clash on TSLA.",
        symbol="TSLA",
        analysis_type="comprehensive",
    )
    return await orchestrator.run_analysis(db=db, user_id=current_user.id, request=req)


@router.post("/scenarios/3")
async def run_scenario_3_portfolio_risk_alert(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    DEMO SCENARIO 3: Portfolio Risk Alert & Exposure Severity Upgrading
    Simulates a 6.8% intraday decline in NVDA (which constitutes >25% of the portfolio).
    The system detects the event, calculates portfolio concentration weight,
    upgrades severity to HIGH/URGENT, activates autonomous multi-agent analysis,
    and publishes a prioritized alert into the proactive intelligence feed.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio found for current user")

    # 1. Detect Event with Personalized Exposure
    anomaly = DetectedAnomaly(
        event_type="PRICE_ANOMALY",
        symbol="NVDA",
        magnitude=-6.8,
        title="Sharp Price Retracement in NVDA (-6.8%)",
        description="Significant intraday drop detected with elevated 2.45x trading volume.",
        evidence=["Price declined -6.8% from previous close", "Volume exceeded 30-day baseline by 145%"],
        confidence=0.92,
    )
    event = event_detector.classify_and_persist(db, anomaly, user_portfolio_weight=28.5)

    # 2. Prioritize & Deduplicate Alert
    alert = alert_prioritizer.prioritize_and_persist(
        db=db,
        user_id=current_user.id,
        event=event,
        portfolio_weight=28.5,
        is_in_watchlist=True,
    )

    # 3. Compute Updated Portfolio Risk Assessment
    positions, sector_exposures, metrics = await portfolio_intelligence_service.evaluate_portfolio(db, portfolio)
    risk_explanation = risk_engine.evaluate_risk(
        positions=positions,
        sector_exposures=sector_exposures,
        metrics=metrics,
        active_events_count=1,
        annualized_vol=42.0,
        max_drawdown=19.5,
    )

    audit_service.log_event(
        db=db,
        action="DEMO_SCENARIO_3",
        user_id=current_user.id,
        resource_type="Alert",
        resource_id=str(alert.id),
        details={"symbol": "NVDA", "event_type": event.event_type, "severity": alert.severity},
        status="SUCCESS",
    )

    return {
        "scenario": "SCENARIO 3: Heavy Portfolio Holding Anomaly & Alert",
        "symbol": "NVDA",
        "price_movement_pct": -6.8,
        "event_detected": {
            "id": event.id,
            "type": event.event_type,
            "severity": event.severity,
            "exposure_weight_pct": 28.5,
        },
        "alert_created": {
            "id": alert.id,
            "priority": alert.priority,
            "severity": alert.severity,
            "title": alert.title,
            "explanation": alert.explanation,
        },
        "updated_portfolio_risk_score": risk_explanation.risk_score,
        "risk_level": risk_explanation.risk_level,
        "message": "Scenario 3 successfully executed. Prioritized alert is now active in Proactive Intelligence Feed.",
    }
