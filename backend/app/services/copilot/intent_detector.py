import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DetectedIntent(BaseModel):
    intent: str
    target_symbols: List[str]
    is_follow_up: bool
    is_safe: bool
    rejection_reason: Optional[str] = None
    extracted_parameters: Dict[str, Any] = {}


KNOWN_SYMBOLS = {"NVDA", "AAPL", "MSFT", "TSLA", "JNJ", "TCS", "INFY", "AMZN", "GOOGL", "META"}


class IntentDetector:
    """
    Classifies user natural-language financial requests into actionable intents.
    Resolves conversational follow-up references using recent chat context,
    enforces trade execution rejection, and neutralizes prompt injections.
    """

    @staticmethod
    def detect_intent(
        query: str,
        recent_messages: Optional[List[Dict[str, Any]]] = None,
    ) -> DetectedIntent:
        q_clean = query.strip()
        q_lower = q_clean.lower()

        # 1. Decision-support boundary check: Prohibit trade execution
        trade_patterns = [
            r"\b(buy|sell|short|execute|place order|transfer money|trade)\b.*\b(shares|stock|options|contracts|portfolio)\b",
            r"\b(execute a trade|place a trade|buy 100 shares|sell all)\b",
        ]
        for p in trade_patterns:
            if re.search(p, q_lower):
                return DetectedIntent(
                    intent="TRADE_EXECUTION_ATTEMPT",
                    target_symbols=[],
                    is_follow_up=False,
                    is_safe=False,
                    rejection_reason=(
                        "Decision Support Notice: MATS is strictly an analytical intelligence and research system. "
                        "It does not execute trades, place orders, or hold brokerage authority. "
                        "All execution must be handled independently by the investor."
                    ),
                )

        # 2. Prompt injection defense
        injection_patterns = [
            r"ignore\b.*(previous|system|safety|rule).*(instruction|rule|constraint|guideline)",
            r"reveal\b.*(system|hidden|prompt|instruction)",
            r"run\b.*(arbitrary|raw).*(sql|shell|bash|python)",
            r"drop\b.*(database|table|all users)",
            r"disregard\b.*(safety|rule|instruction)",
        ]
        for p in injection_patterns:
            if re.search(p, q_lower):
                return DetectedIntent(
                    intent="PROMPT_INJECTION_DEFENSE",
                    target_symbols=[],
                    is_follow_up=False,
                    is_safe=False,
                    rejection_reason=(
                        "Security Boundary Notice: Prompt injection or instruction override attempted. "
                        "MATS operates with immutable security and ethical research boundaries."
                    ),
                )

        # 3. Extract target symbols
        extracted_symbols: List[str] = []
        words = re.findall(r"\b[A-Za-z]{2,8}\b", q_clean)
        for w in words:
            w_up = w.upper()
            if w_up in KNOWN_SYMBOLS and w_up not in extracted_symbols:
                extracted_symbols.append(w_up)

        # 4. Context resolution for follow-ups (e.g. "Why?", "Compare them", "What about competitors?")
        is_follow_up = False
        if not extracted_symbols and recent_messages:
            # Check last 3 assistant/user messages for previously mentioned symbols
            for msg in reversed(recent_messages[-3:]):
                content = msg.get("content", "")
                prev_syms = [s for s in KNOWN_SYMBOLS if re.search(rf"\b{s}\b", content, re.IGNORECASE)]
                if prev_syms:
                    extracted_symbols = prev_syms[:2]
                    is_follow_up = True
                    break

        # 5. Classify intent by semantic patterns
        extracted_params: Dict[str, Any] = {}

        # COMPARISON
        if any(w in q_lower for w in ["compare", "versus", " vs ", "difference between", "better investment"]):
            return DetectedIntent(
                intent="COMPARISON",
                target_symbols=extracted_symbols,
                is_follow_up=is_follow_up,
                is_safe=True,
                extracted_parameters={"symbol_a": extracted_symbols[0] if len(extracted_symbols) > 0 else "NVDA",
                                      "symbol_b": extracted_symbols[1] if len(extracted_symbols) > 1 else "MSFT"},
            )

        # SCENARIO / STRESS TEST
        if any(w in q_lower for w in ["what happens if", "stress test", "falls", "drops", "crashes", "market shock", "plunges"]):
            pct_match = re.search(r"(-?\d+(?:\.\d+)?)\s*%", q_clean)
            pct = float(pct_match.group(1)) if pct_match else -10.0
            if pct > 0 and any(w in q_lower for w in ["drop", "fall", "decline", "crash"]):
                pct = -pct
            extracted_params["percentage_change"] = pct
            if extracted_symbols:
                extracted_params["target_symbol"] = extracted_symbols[0]
            return DetectedIntent(
                intent="SCENARIO",
                target_symbols=extracted_symbols,
                is_follow_up=is_follow_up,
                is_safe=True,
                extracted_parameters=extracted_params,
            )

        # HISTORICAL CHANGE / DIFF
        if any(w in q_lower for w in ["what changed", "since yesterday", "since last checked", "diff", "difference"]):
            return DetectedIntent(
                intent="HISTORICAL_CHANGE",
                target_symbols=extracted_symbols,
                is_follow_up=is_follow_up,
                is_safe=True,
                extracted_parameters={"symbol": extracted_symbols[0] if extracted_symbols else None},
            )

        # ALERT EXPLANATION
        if any(w in q_lower for w in ["alert list", "why is", "alert", "notification", "surveillance"]):
            return DetectedIntent(
                intent="ALERT_EXPLANATION",
                target_symbols=extracted_symbols,
                is_follow_up=is_follow_up,
                is_safe=True,
                extracted_parameters={"symbol": extracted_symbols[0] if extracted_symbols else None},
            )

        # RISK ANALYSIS
        if any(w in q_lower for w in ["risk increase", "why did risk", "risk score", "risk factors", "portfolio risk", "risks should i monitor"]):
            return DetectedIntent(
                intent="RISK_ANALYSIS",
                target_symbols=extracted_symbols,
                is_follow_up=is_follow_up,
                is_safe=True,
                extracted_parameters={},
            )

        # PORTFOLIO ANALYSIS
        if any(w in q_lower for w in ["my portfolio", "holdings", "cash balance", "allocation", "exposed to", "concentration"]):
            return DetectedIntent(
                intent="PORTFOLIO_ANALYSIS",
                target_symbols=extracted_symbols,
                is_follow_up=is_follow_up,
                is_safe=True,
                extracted_parameters={},
            )

        # COMPANY ANALYSIS
        if extracted_symbols:
            return DetectedIntent(
                intent="COMPANY_ANALYSIS",
                target_symbols=extracted_symbols,
                is_follow_up=is_follow_up,
                is_safe=True,
                extracted_parameters={"symbol": extracted_symbols[0]},
            )

        # RESEARCH / DOCUMENT SEARCH
        if any(w in q_lower for w in ["sec", "10-k", "filing", "evidence", "citation", "document", "research", "audit"]):
            return DetectedIntent(
                intent="RESEARCH",
                target_symbols=extracted_symbols,
                is_follow_up=is_follow_up,
                is_safe=True,
                extracted_parameters={"query": q_clean},
            )

        # GENERAL QUERY
        return DetectedIntent(
            intent="GENERAL_QUERY",
            target_symbols=[],
            is_follow_up=is_follow_up,
            is_safe=True,
            extracted_parameters={},
        )


intent_detector = IntentDetector()
