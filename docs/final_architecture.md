# MATS Platform — Final Architecture & System Boundaries

```
===================================================================================
                                USER INTERACTION
===================================================================================
 [ Retail Investor ] <---> [ React 18 / Vite / TypeScript Dark Cyberpunk UI ]
                                       |
                                       |  HTTPS / JWT Bearer
                                       v
===================================================================================
                      [ SECURITY & AUTHENTICATION BOUNDARY ]
===================================================================================
 [ FastAPI HTTP Gateway :8000 ]
   ├── In-Memory Sliding Window Rate Limiter (Login, Register, AI, Ingest)
   ├── Defensive Headers (nosniff, DENY, HSTS, strict-origin)
   ├── Request Correlation ID (X-Request-ID: MATS-REQ-XXXX)
   ├── CORS Whitelist Validation
   └── Authentication Verification (BCrypt / JWT HS256)
                                       |
                                       v
===================================================================================
                      [ MONITORING & SURVEILLANCE BOUNDARY ]
===================================================================================
 [ Autonomous Surveillance Loop (Single-Laptop Local Scheduler) ]
   ├── Target Watchlists & Portfolio Holdings Surveillance
   ├── Anomaly Detector (|Δ%| >= 3.0%, Volume >= 1.35x, SEC Filings)
   └── Event Classifier (Exposure-Weight Severity Personalization)
                                       |
                                       v
===================================================================================
                          [ MULTI-AGENT AI BOUNDARY ]
===================================================================================
 [ Agent Orchestrator (Asyncio Concurrent Dispatch) ]
   ├── Prompt Injection Sanitizer (Delimited Passive Data Encapsulation)
   ├── Query Classifier & Selective Agent Routing
   │     ├── Technical Momentum Agent (OHLCV, Moving Averages, RSI)
   │     ├── Fundamental Valuation Agent (P/E, Debt/Equity, Earnings)
   │     ├── Sentiment & News Agent (Market Mood, Anomaly Signals)
   │     └── Research & Filings Agent (Dense RAG Vectors, Citations)
   │
   ├── [ TRUST BOUNDARY: Conflict Detector ]
   │     └── Preserves & Highlights Divergent Signals (e.g. Bullish Tech vs Bearish Fund)
   │
   ├── [ Synthesis Agent ]
   │     └── Zero-Hallucination Evidence Integration & Confidence Calculation
   │
   └── [ Personalization Layer ]
         └── Investor Profile Risk Framing (Conservative / Moderate / Aggressive)
                                       |
                                       v
===================================================================================
                          [ RISK ENGINE BOUNDARY ]
===================================================================================
 [ Deterministic Portfolio Risk Engine ]
   ├── Real-Time Valuations & HHI Concentration Indices
   ├── 5-Factor Point Attribution (Concentration 25%, Sector 15%, Vol 25%, Drawdown 20%, Events 15%)
   ├── Mathematical What-If Scenario Stress Testing (Non-Predictive Shocks)
   └── Alert Prioritization (URGENT, IMPORTANT, FYI) & 2-Hour Deduplication
                                       |
                                       v
===================================================================================
                            [ DATA & AUDIT BOUNDARY ]
===================================================================================
 [ Persistence & Storage Layer ]
   ├── SQLite Database (`mats.db`) with Foreign Keys & Cascading Deletes
   ├── In-Memory Thread-Safe Cache with Strict TTLs
   ├── Local 384-dimensional Dense Vector Index
   └── Comprehensive Audit Trail (`audit_logs`) Tracking Security & Operations
===================================================================================
```
