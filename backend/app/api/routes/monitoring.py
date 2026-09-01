from typing import Any, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.monitoring import MonitoringRun
from app.models.user import User
from app.schemas.monitoring import (
    MonitoringRunResponse,
    SimulateEventRequest,
    AlertItem,
)
from app.services.monitoring.scheduler import monitoring_scheduler

router = APIRouter()


@router.post("/run", response_model=MonitoringRunResponse)
async def trigger_monitoring_cycle(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Trigger an on-demand autonomous surveillance sweep across active watchlists and portfolios."""
    run_record = await monitoring_scheduler.run_surveillance_cycle(
        db=db,
        user_id=current_user.id,
        run_type="manual",
    )
    return run_record


@router.post("/simulate-event", response_model=AlertItem)
async def simulate_demo_market_event(
    request: SimulateEventRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Controlled demo simulation endpoint for hackathon judges.
    Simulates real-time market anomaly on target ticker, invokes specialized multi-agent
    investigations, assesses portfolio risk impact, and generates an explainable proactive alert.
    """
    alert = await monitoring_scheduler.simulate_demo_event(
        db=db,
        user_id=current_user.id,
        req=request,
    )
    return alert


@router.get("/status", response_model=Optional[MonitoringRunResponse])
def get_latest_monitoring_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get the telemetry status of the most recent autonomous surveillance cycle."""
    return (
        db.query(MonitoringRun)
        .order_by(MonitoringRun.created_at.desc())
        .first()
    )
