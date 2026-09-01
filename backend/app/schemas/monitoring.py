from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MarketEventItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    event_type: str
    severity: str
    title: str
    description: str
    evidence_json: Optional[str] = None
    source: str
    confidence: float
    detected_at: datetime


class AlertItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    event_id: Optional[int] = None
    symbol: str
    priority: str
    severity: str
    title: str
    explanation: str
    agent_synthesis_json: Optional[str] = None
    status: str
    feedback: str
    created_at: datetime
    seen_at: Optional[datetime] = None


class AlertUpdate(BaseModel):
    status: Optional[str] = None  # NEW, SEEN, ACKNOWLEDGED, DISMISSED, RESOLVED
    feedback: Optional[str] = None  # HELPFUL, NOT_HELPFUL, UNSPECIFIED


class DailyBriefResponse(BaseModel):
    date: str
    portfolio_summary: str
    portfolio_return_today_pct: float
    key_developments: List[Dict[str, Any]]
    what_deserves_attention: List[str]
    what_changed: List[str]
    sources_analyzed: List[str]
    disclaimer: str = (
        "Daily intelligence brief synthesized from verified market quotes, SEC filings, "
        "and multi-agent anomaly detections. For decision support only."
    )


class MonitoringRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: int
    run_type: str
    status: str
    events_detected: int
    alerts_created: int
    execution_time_ms: float
    created_at: datetime
    error_message: Optional[str] = None


class SimulateEventRequest(BaseModel):
    symbol: str = Field(default="NVDA")
    event_type: str = Field(default="PRICE_ANOMALY")
    price_change_pct: float = Field(default=-4.5)
    volume_multiple: float = Field(default=2.2)
    title: Optional[str] = None
    description: Optional[str] = None
