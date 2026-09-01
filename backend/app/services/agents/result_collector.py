from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.services.agents.base import AgentFinding


class CollectedResults(BaseModel):
    request_id: str
    agents: List[str]
    successful_agents: List[str]
    failed_agents: List[Dict[str, str]]
    findings: List[AgentFinding]
    sources: List[str]
    timestamps: List[str]
    execution_times_ms: Dict[str, float] = Field(default_factory=dict)


class ResultCollector:
    """Normalizes heterogenous agent outputs into a standardized collection for downstream synthesis."""

    @staticmethod
    def collect(
        request_id: str,
        findings: List[AgentFinding],
        failed_agents: List[Dict[str, str]],
        execution_times: Dict[str, float],
    ) -> CollectedResults:
        successful_agents = [f.agent for f in findings]
        all_agents = successful_agents + [fa["agent"] for fa in failed_agents]

        # Deduplicate sources
        all_sources = []
        for f in findings:
            for s in f.source_ids:
                if s not in all_sources:
                    all_sources.append(s)

        timestamps = [f.timestamp for f in findings]

        return CollectedResults(
            request_id=request_id,
            agents=all_agents,
            successful_agents=successful_agents,
            failed_agents=failed_agents,
            findings=findings,
            sources=all_sources,
            timestamps=timestamps,
            execution_times_ms=execution_times,
        )
