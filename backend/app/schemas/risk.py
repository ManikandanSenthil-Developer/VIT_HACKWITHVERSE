from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PositionHealth(BaseModel):
    symbol: str
    quantity: float
    buy_price: float
    current_price: float
    current_value: float
    unrealized_pnl: float
    pnl_percent: float
    weight_percent: float
    sector: str


class SectorExposure(BaseModel):
    sector: str
    value: float
    weight_percent: float


class RiskScoreFactor(BaseModel):
    factor: str
    weight: float
    contribution: float
    description: str


class RiskScoreExplanation(BaseModel):
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    risk_score: int  # 0 to 100
    reasons: List[str]
    factor_contributions: List[RiskScoreFactor]


class PortfolioHealthResponse(BaseModel):
    portfolio_id: int
    name: str
    total_value: float
    cash_balance: float
    invested_value: float
    total_unrealized_pnl: float
    total_return_percent: float
    currency: str
    risk_level: str
    risk_score: int
    risk_explanation: RiskScoreExplanation
    concentration_top_asset_weight: float
    concentration_hhi: float
    sector_breakdown: List[SectorExposure]
    positions: List[PositionHealth]
    largest_risk_exposure: str
    annualized_volatility: float
    max_historical_drawdown: float
    watchlist_overlap: List[str]
    data_freshness: Dict[str, str]


class ScenarioRequest(BaseModel):
    portfolio_id: int
    shock_type: str = Field(default="holding_shock")  # holding_shock, sector_shock, position_rebalance
    target_symbol: Optional[str] = None
    target_sector: Optional[str] = None
    percentage_change: float = Field(default=-10.0)  # e.g. -10.0, +5.0
    quantity_adjustment: Optional[float] = None


class ScenarioHoldingImpact(BaseModel):
    symbol: str
    current_price: float
    scenario_price: float
    current_value: float
    scenario_value: float
    value_difference: float
    difference_percent: float


class ScenarioResponse(BaseModel):
    portfolio_id: int
    scenario_name: str
    shock_type: str
    target: str
    percentage_change: float
    current_total_value: float
    scenario_total_value: float
    total_difference_usd: float
    total_difference_percent: float
    holdings_impact: List[ScenarioHoldingImpact]
    disclaimer: str = (
        "Hypothetical mathematical scenario — not an investment forecast or guaranteed outcome. "
        "Calculated strictly using proportional holding weights and current market valuation."
    )
