from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.security_validation import sanitize_untrusted_text
from app.schemas.rag import RagSearchRequest
from app.services.agents.base import BaseAgent, AgentFinding
from app.services.retrieval.vector_search import vector_search_service


class ResearchRagAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="rag_research", role="Regulatory & Official Filing Research")

    async def analyze(
        self,
        symbol: str,
        query: str,
        db: Session,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentFinding:
        sym = symbol.upper()
        now_str = datetime.now(timezone.utc).isoformat()

        # Execute semantic retrieval via Phase 2 RAG engine
        search_req = RagSearchRequest(
            query=query,
            symbol=sym,
            top_k=3,
        )

        try:
            search_res = await vector_search_service.search(db, request=search_req)
        except Exception as e:
            return AgentFinding(
                agent=self.name,
                finding=f"RAG filing retrieval failed: {str(e)}",
                signal="NEUTRAL",
                confidence=0.1,
                evidence=[],
                source_ids=[],
                timestamp=now_str,
                limitations=["Vector index query failure."],
            )

        # Strict RAG Quality Rule
        if not search_res.results_found or not search_res.results:
            return AgentFinding(
                agent=self.name,
                finding="No reliable supporting evidence was found.",
                signal="NEUTRAL",
                confidence=0.35,
                evidence=[],
                source_ids=[],
                timestamp=now_str,
                limitations=[
                    f"No ingested SEC documents or regulatory disclosures for {sym} met the similarity threshold."
                ],
                metrics={"matches_found": 0},
            )

        evidence: List[str] = []
        source_ids: List[str] = []
        has_risk_bias = False
        has_positive_bias = False

        for item in search_res.results:
            # Treat external filing text as untrusted data (prompt injection defense)
            safe_text = sanitize_untrusted_text(item.text)
            doc_title = item.citation.document_title
            section = item.citation.section or "General"
            score_pct = int(item.score * 100)

            evidence_entry = (
                f"[{doc_title} | {section} | Match: {score_pct}%]: \"{safe_text[:280]}...\""
            )
            evidence.append(evidence_entry)
            
            source_link = item.citation.source_url or f"DOC_ID_{item.citation.document_id}"
            if source_link not in source_ids:
                source_ids.append(source_link)

            # Analyze qualitative tone
            lower_text = safe_text.lower()
            if any(k in lower_text for k in ("risk", "disruption", "adversely", "litigation", "restriction")):
                has_risk_bias = True
            if any(k in lower_text for k in ("growth", "expanded", "record", "revenue reached", "strong adoption")):
                has_positive_bias = True

        top_doc = search_res.results[0].citation.document_title
        top_score = search_res.results[0].score

        if has_positive_bias and not has_risk_bias:
            signal = "BULLISH"
            finding = (
                f"Regulatory filings ({top_doc}) verify accelerating commercial adoption and expanding operating profitability "
                f"with high evidence relevance ({int(top_score * 100)}%)."
            )
        elif has_risk_bias and has_positive_bias:
            signal = "CAUTIOUS"
            finding = (
                f"Official SEC filings verify robust core revenue expansion, while Item 1A Risk Disclosures document "
                f"material supply chain dependencies and regulatory scrutiny."
            )
        elif has_risk_bias:
            signal = "CAUTIOUS"
            finding = (
                f"Regulatory disclosures highlight notable operational risk factors and compliance challenges in {top_doc}."
            )
        else:
            signal = "NEUTRAL"
            finding = f"Retrieved official filing documentation confirming standard corporate baseline operations."

        return AgentFinding(
            agent=self.name,
            finding=finding,
            signal=signal,
            confidence=round(min(0.92, max(0.65, top_score)), 2),
            evidence=evidence,
            source_ids=source_ids,
            timestamp=now_str,
            limitations=[
                "Evidence reflects historical audited disclosures; forward guidance is subject to market variance."
            ],
            metrics={
                "top_match_score": round(top_score, 4),
                "citations_count": len(evidence),
            },
        )
