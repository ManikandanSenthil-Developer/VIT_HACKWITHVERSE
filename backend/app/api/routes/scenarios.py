import json
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.portfolio import Portfolio
from app.models.monitoring import ScenarioRun
from app.models.user import User
from app.schemas.risk import ScenarioRequest, ScenarioResponse
from app.services.risk.scenario_engine import scenario_engine

router = APIRouter()


@router.post("/run", response_model=ScenarioResponse)
async def run_scenario_stress_test(
    request: ScenarioRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Execute deterministic What-If portfolio stress testing.
    Calculates exact dollar and percentage impact of hypothetical market shocks.
    Non-predictive decision-support calculation.
    """
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.id == request.portfolio_id, Portfolio.user_id == current_user.id)
        .first()
    )
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found or access denied.",
        )

    res = await scenario_engine.run_scenario(db, portfolio, request)

    # Persist scenario run in database
    run_record = ScenarioRun(
        user_id=current_user.id,
        portfolio_id=portfolio.id,
        name=res.scenario_name,
        scenario_type=request.shock_type,
        parameters_json=json.dumps(request.model_dump()),
        impact_summary_json=json.dumps(res.model_dump()),
    )
    db.add(run_record)
    db.commit()

    return res
