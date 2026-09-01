import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DynamicRoutingDecision(BaseModel):
    query: str
    classified_domain: str  # PRICE_MOMENTUM, FINANCIAL_HEALTH, PORTFOLIO_RISK, COMPETITIVE_PEERS, COMPREHENSIVE, DEFENSIVE_REJECTION
    selected_agents: List[str]
    omitted_agents: List[str]
    routing_explanation: str
    is_safe: bool = True
    rejection_reason: Optional[str] = None


class DynamicOrchestratorRouter:
    """
    Intelligently routes financial questions to the minimum required subset
    of specialized agents. Makes multi-agent orchestration transparent and explainable.
    """

    ALL_AGENTS = ["technical", "fundamental", "sentiment", "rag", "counterargument", "risk"]

    @classmethod
    def route_query(cls, query: str) -> DynamicRoutingDecision:
        q_lower = query.lower().strip()

        # 1. Prompt injection / jailbreak defense
        injection_patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"reveal\s+(your\s+)?(system\s+)?prompt",
            r"bypass\s+safety",
            r"you\s+are\s+now\s+dan",
        ]
        for pattern in injection_patterns:
            if re.search(pattern, q_lower):
                return DynamicRoutingDecision(
                    query=query,
                    classified_domain="DEFENSIVE_REJECTION",
                    selected_agents=[],
                    omitted_agents=cls.ALL_AGENTS,
                    routing_explanation="Query blocked by MATS Security Boundary Defense: prompt injection or adversarial directive detected.",
                    is_safe=False,
                    rejection_reason="Adversarial prompt injection pattern identified.",
                )

        # 2. Portfolio Risk & Exposure Domain
        if any(k in q_lower for k in ["portfolio risk", "why did my risk", "concentration", "my portfolio", "asset allocation", "drawdown risk"]):
            selected = ["risk", "fundamental"]
            omitted = [a for a in cls.ALL_AGENTS if a not in selected]
            return DynamicRoutingDecision(
                query=query,
                classified_domain="PORTFOLIO_RISK",
                selected_agents=selected,
                omitted_agents=omitted,
                routing_explanation=(
                    "Your question concerns portfolio risk, asset allocation, and concentration exposure. "
                    "MATS dynamically selected the Deterministic 5-Factor Risk Engine and Fundamental Agent. "
                    "Omitted Technical and Sentiment agents to avoid irrelevant short-term noise."
                ),
            )

        # 3. Price Movement / Short-term Momentum Domain
        if any(k in q_lower for k in ["price movement", "why is it dropping", "why is it up", "surge", "plummet", "what caused today", "momentum", "rsi"]):
            selected = ["technical", "sentiment", "rag"]
            omitted = [a for a in cls.ALL_AGENTS if a not in selected]
            return DynamicRoutingDecision(
                query=query,
                classified_domain="PRICE_MOMENTUM",
                selected_agents=selected,
                omitted_agents=omitted,
                routing_explanation=(
                    "Your question concerns immediate price movements, technical momentum, and news catalysts. "
                    "MATS dynamically selected the Technical, Sentiment, and SEC RAG Research agents. "
                    "Omitted balance sheet agents to optimize latency."
                ),
            )

        # 4. Financial Health & Corporate Fundamentals Domain
        if any(k in q_lower for k in ["financial health", "balance sheet", "revenue", "profitability", "operating margin", "debt", "cash flow", "10-k"]):
            selected = ["fundamental", "rag", "counterargument"]
            omitted = [a for a in cls.ALL_AGENTS if a not in selected]
            return DynamicRoutingDecision(
                query=query,
                classified_domain="FINANCIAL_HEALTH",
                selected_agents=selected,
                omitted_agents=omitted,
                routing_explanation=(
                    "Your question concerns solvency, profitability, and regulatory disclosures. "
                    "MATS dynamically selected the Fundamental Agent, SEC RAG Research, and Counterargument Agent. "
                    "Omitted short-term price momentum agents."
                ),
            )

        # 5. Competitive Comparison Domain
        if any(k in q_lower for k in ["compare", "peers", "competitors", "vs", "versus"]):
            selected = ["fundamental", "technical", "rag", "counterargument"]
            omitted = [a for a in cls.ALL_AGENTS if a not in selected]
            return DynamicRoutingDecision(
                query=query,
                classified_domain="COMPETITIVE_PEERS",
                selected_agents=selected,
                omitted_agents=omitted,
                routing_explanation=(
                    "Your question involves comparative multi-entity research. "
                    "MATS dynamically selected Fundamental, Technical, RAG Research, and Counterargument agents. "
                    "Synthesizes comparative metrics across peer entities."
                ),
            )

        # 6. Default / Comprehensive Synthesis Domain
        selected = ["technical", "fundamental", "sentiment", "rag", "counterargument"]
        omitted = ["risk"]
        return DynamicRoutingDecision(
            query=query,
            classified_domain="COMPREHENSIVE",
            selected_agents=selected,
            omitted_agents=omitted,
            routing_explanation=(
                "Your question requires comprehensive multi-domain intelligence. "
                "MATS selected Technical, Fundamental, Sentiment, RAG Research, and Counterargument agents."
            ),
        )


dynamic_router = DynamicOrchestratorRouter()
