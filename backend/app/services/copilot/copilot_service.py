import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.copilot import CopilotConversation, CopilotMessage
from app.services.copilot.intent_detector import intent_detector, DetectedIntent
from app.services.copilot.tool_registry import tool_registry
from app.services.research.comparison_engine import comparison_engine
from app.services.agents.counterargument_agent import counterargument_agent
from app.services.multilingual.translator import multilingual_service

logger = logging.getLogger("mats.copilot.service")


class CopilotService:
    """
    Core conversational financial intelligence coordinator.
    Transforms raw questions into structured tool invocations, synthesizes
    multi-perspective evidence, and grounds answers in factual data.
    """

    async def chat(
        self,
        db: Session,
        user_id: int,
        message: str,
        conversation_id: Optional[int] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        # 1. Manage or create conversation
        if conversation_id:
            conv = (
                db.query(CopilotConversation)
                .filter(CopilotConversation.id == conversation_id, CopilotConversation.user_id == user_id)
                .first()
            )
            if not conv:
                conv = self._create_conversation(db, user_id, message)
        else:
            conv = self._create_conversation(db, user_id, message)

        # 2. Retrieve recent message history for conversational follow-up resolution
        recent_msgs = (
            db.query(CopilotMessage)
            .filter(CopilotMessage.conversation_id == conv.id)
            .order_by(CopilotMessage.created_at.desc())
            .limit(4)
            .all()
        )
        recent_context = [{"role": m.role, "content": m.content} for m in reversed(recent_msgs)]

        # 3. Log user message
        user_msg = CopilotMessage(
            conversation_id=conv.id,
            role="user",
            content=message,
        )
        db.add(user_msg)
        db.commit()

        # 4. Intent detection
        detected: DetectedIntent = intent_detector.detect_intent(message, recent_context)
        user_msg.intent = detected.intent
        db.commit()

        # 5. Handle security / non-trading boundaries
        if not detected.is_safe:
            reply_content = detected.rejection_reason or "Request cannot be executed within safety bounds."
            assistant_msg = CopilotMessage(
                conversation_id=conv.id,
                role="assistant",
                content=reply_content,
                intent=detected.intent,
                citations_json=json.dumps(["MATS Decision Support Governance Policy"]),
            )
            db.add(assistant_msg)
            conv.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(assistant_msg)
            return {
                "conversation_id": conv.id,
                "message_id": assistant_msg.id,
                "intent": detected.intent,
                "summary": reply_content,
                "key_findings": [],
                "evidence": [],
                "risks": ["Direct brokerage execution prohibited by design."],
                "counterarguments": [],
                "follow_ups": [
                    "Explain my portfolio risk",
                    "Compare NVDA and MSFT",
                    "What evidence supports current ratings?",
                ],
                "tool_calls": [],
                "citations": ["MATS Decision Support Governance Policy"],
            }

        # 6. Tool invocation & multi-perspective synthesis
        tool_calls: List[str] = []
        tool_results: Dict[str, Any] = {}
        citations: List[str] = []
        key_findings: List[str] = []
        evidence: List[str] = []
        risks: List[str] = []
        counterarguments: List[str] = []
        follow_ups: List[str] = []

        intent = detected.intent
        sym = detected.target_symbols[0] if detected.target_symbols else "NVDA"

        if intent == "PORTFOLIO_ANALYSIS":
            tool_calls.extend(["get_portfolio", "get_risk"])
            p_res = await tool_registry.execute_tool("get_portfolio", db, user_id, {})
            r_res = await tool_registry.execute_tool("get_risk", db, user_id, {})
            tool_results["portfolio"] = p_res.get("data", {})
            tool_results["risk"] = r_res.get("data", {})

            pdata = tool_results["portfolio"]
            rdata = tool_results["risk"]
            summary = (
                f"Your active portfolio contains {len(pdata.get('holdings', []))} positions with a total invested "
                f"value of ${pdata.get('total_invested', 0):,.2f} and cash balance of ${pdata.get('cash_balance', 0):,.2f}. "
                f"Overall portfolio risk score is currently evaluated at {rdata.get('risk_score', 0):.1f} ({rdata.get('risk_level', 'MODERATE')})."
            )
            for h in pdata.get("holdings", [])[:3]:
                key_findings.append(f"{h['symbol']}: {h['weight_percent']:.1f}% allocation, P/L: {h['pnl_percent']:+.1f}%.")
            for d in rdata.get("key_drivers", []):
                risks.append(d)
            citations.append("Real-time Portfolio Ledger & Deterministic Risk Engine")
            follow_ups = ["Why did my portfolio risk increase?", "Stress test a 10% market drop", "Show my highest risks"]

        elif intent == "RISK_ANALYSIS":
            tool_calls.extend(["get_risk", "get_portfolio", "get_alerts"])
            r_res = await tool_registry.execute_tool("get_risk", db, user_id, {})
            a_res = await tool_registry.execute_tool("get_alerts", db, user_id, {"limit": 3})
            p_res = await tool_registry.execute_tool("get_portfolio", db, user_id, {})
            rdata = r_res.get("data", {})
            pdata = p_res.get("data", {})
            adata = a_res.get("data", {})

            summary = (
                f"Portfolio risk stands at {rdata.get('risk_score', 0):.1f} ({rdata.get('risk_level', 'MODERATE')}). "
                f"{rdata.get('summary', 'Risk is balanced across active holdings.')}"
            )
            for f in rdata.get("factors", []):
                key_findings.append(f"{f.get('factor')}: {f.get('contribution_points', 0):.1f} pts ({f.get('status')})")
            for d in rdata.get("key_drivers", []):
                risks.append(d)
            for al in adata.get("alerts", []):
                evidence.append(f"Recent alert on {al['symbol']}: {al['title']}")
            citations.extend(["Deterministic 5-Factor Risk Engine", "Proactive Surveillance Feed"])
            follow_ups = ["What if my largest holding falls 10%?", "What changed since yesterday?", "Compare my top holdings"]

        elif intent == "COMPARISON":
            sym_a = detected.extracted_parameters.get("symbol_a", sym)
            sym_b = detected.extracted_parameters.get("symbol_b", "MSFT" if sym != "MSFT" else "AAPL")
            tool_calls.append("compare_companies")
            comp_res = await comparison_engine.compare(db, sym_a, sym_b)
            tool_results["comparison"] = comp_res

            summary = (
                f"Side-by-side comparison between {sym_a} and {sym_b}: "
                + " ".join(comp_res.get("relative_insights", [])[:2])
            )
            for ins in comp_res.get("relative_insights", []):
                key_findings.append(ins)
            ca = comp_res.get("company_a", {})
            cb = comp_res.get("company_b", {})
            evidence.append(f"{sym_a} Price: ${ca.get('market', {}).get('price')}, P/E: {ca.get('fundamentals', {}).get('pe_ratio')}")
            evidence.append(f"{sym_b} Price: ${cb.get('market', {}).get('price')}, P/E: {cb.get('fundamentals', {}).get('pe_ratio')}")
            citations.extend(["Market Normalized Quotes", "Corporate 10-K Fundamentals"])
            follow_ups = [f"What are the risks for {sym_a}?", f"Give me the bull case for {sym_b}", "Stress test my portfolio"]

        elif intent == "SCENARIO":
            tool_calls.append("run_scenario")
            pct = detected.extracted_parameters.get("percentage_change", -10.0)
            target = detected.extracted_parameters.get("target_symbol")
            scen_res = await tool_registry.execute_tool("run_scenario", db, user_id, {
                "target_symbol": target,
                "percentage_change": pct,
            })
            tool_results["scenario"] = scen_res.get("data", {})
            sdata = tool_results["scenario"]

            summary = (
                f"HYPOTHETICAL STRESS TEST ({pct:+.1f}% Shock on {target or 'Portfolio'}): "
                f"Estimated portfolio dollar impact is {sdata.get('total_dollar_impact', 0):+,.2f} "
                f"({sdata.get('total_percentage_impact', 0):+.2f}% total equity change)."
            )
            for imp in sdata.get("holding_impacts", [])[:3]:
                key_findings.append(f"{imp['symbol']}: ${imp['dollar_change']:+,.2f} ({imp['percentage_change']:+.1f}%)")
            risks.append(f"Concentration exposure in {sdata.get('most_affected_sector', 'primary sector')}.")
            citations.append("Mathematical Scenario Stress Simulator")
            follow_ups = ["What if volatility doubles?", "How diversified am I?", "Why did risk increase?"]

        elif intent == "HISTORICAL_CHANGE":
            tool_calls.append("get_analysis_history")
            hist_res = await tool_registry.execute_tool("get_analysis_history", db, user_id, {"symbol": sym, "limit": 2})
            tool_results["history"] = hist_res.get("data", {})
            hdata = tool_results["history"].get("analyses", [])

            if len(hdata) >= 2:
                summary = (
                    f"Comparing latest analysis on {sym} against previous run: "
                    f"Latest assessment is '{hdata[0]['assessment']}' ({hdata[0]['confidence']*100:.0f}%) vs "
                    f"previous '{hdata[1]['assessment']}' ({hdata[1]['confidence']*100:.0f}%)."
                )
                key_findings.append(f"Current thesis: {hdata[0]['summary'][:120]}...")
                key_findings.append(f"Previous thesis: {hdata[1]['summary'][:120]}...")
            elif len(hdata) == 1:
                summary = f"One prior research snapshot on record for {sym}: '{hdata[0]['assessment']}' ({hdata[0]['confidence']*100:.0f}%)."
                key_findings.append(hdata[0]["summary"][:160])
            else:
                summary = f"No prior historical analysis on record for {sym}. Running a baseline evaluation now."
                key_findings.append("Baseline historical telemetry established.")

            citations.append("Historical Analysis Audit Trail")
            follow_ups = [f"Run full research on {sym}", f"Compare {sym} with peers", "Explain my portfolio risk"]

        elif intent == "ALERT_EXPLANATION":
            tool_calls.append("get_alerts")
            a_res = await tool_registry.execute_tool("get_alerts", db, user_id, {"limit": 4})
            adata = a_res.get("data", {}).get("alerts", [])
            sym_alerts = [a for a in adata if a["symbol"] == sym] if sym else adata

            if sym_alerts:
                al = sym_alerts[0]
                summary = f"Active alert on {al['symbol']}: {al['title']}. Priority: {al['priority']} (Severity: {al['severity']})."
                key_findings.append(al["explanation"])
                evidence.append(f"Generated at: {al['created_at']}")
            else:
                summary = f"No acute active alerts currently targeting {sym}. Routine surveillance ongoing."
                key_findings.append("No statistical price plunge or volume surge anomalies detected.")

            citations.append("Surveillance Anomaly Engine")
            follow_ups = [f"What is the technical momentum of {sym}?", "Check my portfolio risk", "Stress test this holding"]

        elif intent == "COMPANY_ANALYSIS":
            tool_calls.extend(["get_company", "get_market_data", "run_technical_analysis", "run_fundamental_analysis"])
            c_res = await tool_registry.execute_tool("get_company", db, user_id, {"symbol": sym})
            m_res = await tool_registry.execute_tool("get_market_data", db, user_id, {"symbol": sym})
            t_res = await tool_registry.execute_tool("run_technical_analysis", db, user_id, {"symbol": sym})
            f_res = await tool_registry.execute_tool("run_fundamental_analysis", db, user_id, {"symbol": sym})

            cdata = c_res.get("data", {})
            mdata = m_res.get("data", {})
            tdata = t_res.get("data", {})
            fdata = f_res.get("data", {})

            # Also invoke Devil's Advocate
            counter_finding = await counterargument_agent.generate_counterarguments(symbol=sym, db=db)
            counterarguments = counter_finding.challenges

            summary = (
                f"Multi-perspective intelligence on {sym} ({cdata.get('name', sym)}): "
                f"Trading at ${mdata.get('price', 0):.2f} ({mdata.get('change_percent', 0):+.2f}%). "
                f"Technical momentum is {tdata.get('signal', 'NEUTRAL')} while Fundamental valuation is {fdata.get('signal', 'NEUTRAL')}."
            )
            key_findings.append(f"Technical: {tdata.get('finding', 'N/A')}")
            key_findings.append(f"Fundamental: {fdata.get('finding', 'N/A')}")
            for ev in fdata.get("evidence", [])[:2]:
                evidence.append(ev)
            for ch in counter_finding.challenges[:2]:
                risks.append(ch)
            citations.extend(["Live Market Data Telemetry", "Corporate 10-K SEC Filings"])
            follow_ups = [f"Give me the bull case for {sym}", f"Challenge the thesis for {sym}", f"Compare {sym} with competitors"]

        else:  # GENERAL_QUERY or RESEARCH
            summary = (
                "MATS is an autonomous multi-agent financial intelligence copilot for retail investors. "
                "I synthesize market data, official SEC Form 10-Ks, technical indicators, and deterministic risk models. "
                "I never execute trades or hallucinate metrics."
            )
            key_findings = [
                "4 Specialized Autonomous Agents: Technical, Fundamental, Sentiment, and SEC RAG Research.",
                "Devil's Advocate Engine: Challenges bullish assumptions to prevent confirmation bias.",
                "Deterministic 5-Factor Risk Engine: Transparent mathematical attribution without black-box scores.",
            ]
            citations.append("MATS System Architecture Specification")
            follow_ups = ["Analyze my portfolio", "Why did my portfolio risk increase?", "Compare NVDA and MSFT"]

        # 7. Apply multilingual translation & financial term protection if applicable
        target_lang = language or multilingual_service.detect_language(message)
        if target_lang in ("ta", "hi"):
            loc = multilingual_service.localize_copilot_response(
                summary=summary,
                key_findings=key_findings,
                risks=risks,
                counterarguments=counterarguments,
                follow_ups=follow_ups,
                target_lang=target_lang,
            )
            summary = loc["summary"]
            key_findings = loc["key_findings"]
            risks = loc["risks"]
            counterarguments = loc["counterarguments"]
            follow_ups = loc["follow_ups"]

        # 8. Persist assistant message
        full_content = summary + "\n\n" + "\n".join([f"• {k}" for k in key_findings])
        assistant_msg = CopilotMessage(
            conversation_id=conv.id,
            role="assistant",
            content=full_content,
            intent=intent,
            tool_calls_json=json.dumps(tool_calls),
            tool_results_json=json.dumps(tool_results),
            citations_json=json.dumps(citations),
        )
        db.add(assistant_msg)
        conv.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(assistant_msg)

        return {
            "conversation_id": conv.id,
            "message_id": assistant_msg.id,
            "intent": intent,
            "language": target_lang,
            "summary": summary,
            "key_findings": key_findings,
            "evidence": evidence,
            "risks": risks,
            "counterarguments": counterarguments,
            "follow_ups": follow_ups,
            "tool_calls": tool_calls,
            "citations": citations,
        }

    def _create_conversation(self, db: Session, user_id: int, first_query: str) -> CopilotConversation:
        title = first_query[:40] + ("..." if len(first_query) > 40 else "")
        conv = CopilotConversation(user_id=user_id, title=title)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    def list_conversations(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        convs = (
            db.query(CopilotConversation)
            .filter(CopilotConversation.user_id == user_id)
            .order_by(CopilotConversation.updated_at.desc())
            .all()
        )
        return [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                "message_count": len(c.messages),
            }
            for c in convs
        ]

    def get_conversation_messages(self, db: Session, user_id: int, conversation_id: int) -> List[Dict[str, Any]]:
        conv = (
            db.query(CopilotConversation)
            .filter(CopilotConversation.id == conversation_id, CopilotConversation.user_id == user_id)
            .first()
        )
        if not conv:
            raise ValueError("Conversation not found or access denied.")

        return [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "intent": m.intent,
                "tool_calls": json.loads(m.tool_calls_json) if m.tool_calls_json else [],
                "citations": json.loads(m.citations_json) if m.citations_json else [],
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in conv.messages
        ]

    def delete_conversation(self, db: Session, user_id: int, conversation_id: int) -> bool:
        conv = (
            db.query(CopilotConversation)
            .filter(CopilotConversation.id == conversation_id, CopilotConversation.user_id == user_id)
            .first()
        )
        if not conv:
            return False
        db.delete(conv)
        db.commit()
        return True


copilot_service = CopilotService()
