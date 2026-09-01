import asyncio
from datetime import datetime, timezone
import json
import time
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.security_validation import sanitize_symbol, validate_research_query
from app.models.intelligence import AnalysisHistory
from app.models.investor_profile import InvestorProfile
from app.schemas.intelligence import (
    AnalysisRequest,
    AnalysisResponse,
    AgentFindingSchema,
    SignalConflictSchema,
    ReasoningTraceSchema,
    RecommendationSchema,
)
from app.services.agents.base import BaseAgent, AgentFinding
from app.services.agents.conflict_detector import ConflictDetector
from app.services.agents.fundamental_agent import FundamentalAgent
from app.services.agents.rag_research_agent import ResearchRagAgent
from app.services.agents.recommendation_engine import RecommendationEngine
from app.services.agents.result_collector import ResultCollector
from app.services.agents.sentiment_agent import SentimentMarketAgent
from app.services.agents.synthesis_agent import SynthesisAgent
from app.services.agents.technical_agent import TechnicalMomentumAgent


class AgentOrchestrator:
    """
    Master Multi-Agent Orchestrator.
    Directs task decomposition, selective agent routing, parallel execution with timeout guards,
    isolated error handling, signal conflict detection, evidence synthesis, and user personalization.
    """

    def __init__(self):
        self.technical_agent = TechnicalMomentumAgent()
        self.fundamental_agent = FundamentalAgent()
        self.sentiment_agent = SentimentMarketAgent()
        self.research_agent = ResearchRagAgent()

    def route_query_agents(self, query: str, analysis_type: str) -> List[BaseAgent]:
        """Intelligently determine which specialized agents should execute."""
        q = query.lower()
        atype = analysis_type.lower()

        if atype == "technical":
            return [self.technical_agent, self.sentiment_agent]
        if atype == "fundamental":
            return [self.fundamental_agent, self.research_agent]
        if atype == "sentiment":
            return [self.sentiment_agent, self.technical_agent]

        # Automatic semantic routing based on query intent
        is_pure_tech = any(k in q for k in ("technical", "rsi", "momentum", "moving average", "chart", "support", "resistance"))
        is_pure_fund = any(k in q for k in ("pe ratio", "valuation", "balance sheet", "net income", "debt to equity", "free cash flow"))

        if is_pure_tech and not is_pure_fund and "long-term" not in q and "invest" not in q:
            return [self.technical_agent, self.sentiment_agent]
        if is_pure_fund and not is_pure_tech:
            return [self.fundamental_agent, self.research_agent]

        # Broad research or default comprehensive
        return [
            self.technical_agent,
            self.fundamental_agent,
            self.sentiment_agent,
            self.research_agent,
        ]

    async def execute_agent_with_guard(
        self,
        agent: BaseAgent,
        symbol: str,
        query: str,
        db: Session,
        timeout_seconds: float = 8.0,
    ) -> tuple[Optional[AgentFinding], Optional[Dict[str, str]], float]:
        """Execute a single agent with strict timeout protection and failure isolation."""
        start = time.time()
        try:
            finding = await asyncio.wait_for(
                agent.analyze(symbol=symbol, query=query, db=db),
                timeout=timeout_seconds,
            )
            elapsed_ms = (time.time() - start) * 1000
            return finding, None, elapsed_ms
        except asyncio.TimeoutError:
            elapsed_ms = (time.time() - start) * 1000
            return None, {"agent": agent.name, "reason": "timeout"}, elapsed_ms
        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            return None, {"agent": agent.name, "reason": str(e)}, elapsed_ms

    async def run_analysis(
        self,
        db: Session,
        user_id: int,
        request: AnalysisRequest,
    ) -> AnalysisResponse:
        start_total = time.time()
        request_id = f"mats_req_{uuid.uuid4().hex[:12]}"

        # 1. Input sanitization & security validation
        clean_query = validate_research_query(request.query)
        clean_symbol = sanitize_symbol(request.symbol)

        # 2. Retrieve user context for personalization
        profile = db.query(InvestorProfile).filter(InvestorProfile.user_id == user_id).first()

        # 3. Decide which agents should run
        agents_to_run = self.route_query_agents(clean_query, request.analysis_type)

        # 4. Asynchronous parallel execution with timeouts and error isolation
        tasks = [
            self.execute_agent_with_guard(
                agent=agent,
                symbol=clean_symbol,
                query=clean_query,
                db=db,
            )
            for agent in agents_to_run
        ]

        results = await asyncio.gather(*tasks)

        successful_findings: List[AgentFinding] = []
        failed_agents: List[Dict[str, str]] = []
        execution_times: Dict[str, float] = {}

        for finding, failure, duration_ms in results:
            if finding:
                successful_findings.append(finding)
                execution_times[finding.agent] = round(duration_ms, 2)
            elif failure:
                failed_agents.append(failure)
                execution_times[failure["agent"]] = round(duration_ms, 2)

        # 5. Result Collector
        collected = ResultCollector.collect(
            request_id=request_id,
            findings=successful_findings,
            failed_agents=failed_agents,
            execution_times=execution_times,
        )

        # 6. Conflict Detector
        conflicts = ConflictDetector.detect_conflicts(successful_findings)

        # 7. Synthesis Agent
        synthesis = SynthesisAgent.synthesize(
            symbol=clean_symbol,
            findings=successful_findings,
            conflicts=conflicts,
        )

        # 8. Personalization Layer & Recommendation Engine
        recommendation = RecommendationEngine.generate(
            symbol=clean_symbol,
            synthesis=synthesis,
            conflicts=conflicts,
            sources=collected.sources,
            profile=profile,
        )

        # 9. Disclosures regarding any failed or missing agents
        disclosures = []
        for fa in failed_agents:
            disclosures.append(f"{fa['agent'].capitalize()} analysis was unavailable for this request ({fa['reason']}).")

        # 10. Construct safe, auditable Reasoning Trace
        data_considered = [
            f"Evaluated 30-day OHLCV historical price series for {clean_symbol}",
            f"Evaluated reported balance sheet metrics and income statements for {clean_symbol}",
            f"Evaluated real-time trading volume and anomaly distribution telemetry",
            f"Queried official SEC 10-K and 10-Q regulatory filings for {clean_symbol}",
        ]
        major_findings = [f.finding for f in successful_findings]
        conflicts_detected = [c.description for c in conflicts] if conflicts else ["No conflicting signals detected."]

        reasoning_trace = ReasoningTraceSchema(
            data_considered=data_considered,
            agents_consulted=[agent.name for agent in agents_to_run],
            major_findings=major_findings,
            conflicts_detected=conflicts_detected,
            evidence_used=synthesis.evidence_summary,
            final_assessment=synthesis.overall_assessment,
            confidence=synthesis.confidence,
            limitations=synthesis.limitations,
        )

        total_time_ms = round((time.time() - start_total) * 1000, 2)

        status_str = "completed" if not failed_agents else "partial_failure"

        # 11. Persist Analysis Record in DB
        history_record = AnalysisHistory(
            user_id=user_id,
            request_id=request_id,
            query=clean_query,
            symbol=clean_symbol,
            analysis_type=request.analysis_type,
            overall_assessment=synthesis.overall_assessment,
            confidence=synthesis.confidence,
            recommendation_json=json.dumps(recommendation.model_dump()),
            agents_consulted_json=json.dumps([a.name for a in agents_to_run]),
            findings_json=json.dumps([f.model_dump() for f in successful_findings]),
            conflicts_json=json.dumps([c.model_dump() for c in conflicts]),
            reasoning_trace_json=json.dumps(reasoning_trace.model_dump()),
            sources_json=json.dumps(collected.sources),
            execution_time_ms=total_time_ms,
        )
        db.add(history_record)
        db.commit()

        # 12. Build full response
        return AnalysisResponse(
            request_id=request_id,
            status=status_str,
            symbol=clean_symbol,
            query=clean_query,
            summary=(
                f"Multi-agent assessment for {clean_symbol}: {synthesis.overall_assessment}. "
                f"Consulted {len(successful_findings)} specialized agent(s) with {synthesis.confidence * 100:.0f}% confidence."
            ),
            overall_assessment=synthesis.overall_assessment,
            confidence=synthesis.confidence,
            agents=[AgentFindingSchema(**f.model_dump()) for f in successful_findings],
            successful_agents=collected.successful_agents,
            failed_agents=failed_agents,
            conflicts=[SignalConflictSchema(**c.model_dump()) for c in conflicts],
            recommendation=RecommendationSchema(**recommendation.model_dump()),
            reasoning_trace=reasoning_trace,
            sources=collected.sources,
            freshness={
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "execution_times_ms": execution_times,
            },
            limitations=synthesis.limitations,
            execution_time_ms=total_time_ms,
            disclosures=disclosures,
        )


orchestrator = AgentOrchestrator()
