from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AgentFindingSchema(BaseModel):
    agent: str
    finding: str
    signal: str  # BULLISH, BEARISH, NEUTRAL, CAUTIOUS
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)
    timestamp: str
    limitations: List[str] = Field(default_factory=list)
    metrics: Optional[Dict[str, Any]] = None


class SignalConflictSchema(BaseModel):
    conflict_type: str
    conflicting_agents: List[str]
    conflicting_signals: Dict[str, str]
    description: str
    severity: str  # high, medium, low
    evidence_summary: List[str] = Field(default_factory=list)


class ReasoningTraceSchema(BaseModel):
    data_considered: List[str]
    agents_consulted: List[str]
    major_findings: List[str]
    conflicts_detected: List[str]
    evidence_used: List[str]
    final_assessment: str
    confidence: float
    limitations: List[str]


class RecommendationSchema(BaseModel):
    assessment: str  # e.g. "Research Signal: Favorable", "Cautious: Technical Pullback", "Monitor", "Insufficient Evidence"
    confidence: float
    key_reasons: List[str]
    risks: List[str]
    what_to_monitor: List[str]
    sources: List[str]
    personalization_note: Optional[str] = None


class AnalysisRequest(BaseModel):
    query: str
    symbol: str
    analysis_type: str = "auto"  # auto, comprehensive, technical, fundamental, sentiment


class AnalysisResponse(BaseModel):
    request_id: str
    status: str  # completed, partial_failure, failed
    symbol: str
    query: str
    summary: str
    overall_assessment: str
    confidence: float
    agents: List[AgentFindingSchema]
    successful_agents: List[str]
    failed_agents: List[Dict[str, str]]
    conflicts: List[SignalConflictSchema]
    recommendation: RecommendationSchema
    reasoning_trace: ReasoningTraceSchema
    sources: List[str]
    freshness: Dict[str, Any]
    limitations: List[str]
    execution_time_ms: float
    disclosures: List[str] = Field(default_factory=list)


class AnalysisHistoryItem(BaseModel):
    id: int
    request_id: str
    symbol: str
    query: str
    analysis_type: str
    overall_assessment: str
    confidence: float
    execution_time_ms: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentStatusInfo(BaseModel):
    agent_id: str
    name: str
    role: str
    status: str  # online, ready, degraded
    capabilities: List[str]
