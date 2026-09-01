from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session


class AgentFinding(BaseModel):
    agent: str
    finding: str
    signal: str  # BULLISH, BEARISH, NEUTRAL, CAUTIOUS
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)
    timestamp: str
    limitations: List[str] = Field(default_factory=list)
    metrics: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    @abstractmethod
    async def analyze(
        self,
        symbol: str,
        query: str,
        db: Session,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentFinding:
        """Execute specialized financial analysis for target symbol."""
        pass
