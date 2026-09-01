# MATS Platform — Architecture & Boundaries

---

## 1. End-to-End System Topology

```
+-------------------------------------------------------------------------+
|                              USER INTERACTION                           |
|  React 18 + Vite + TypeScript Dashboard | Portfolios | Terminal | Trust |
+------------------------------------+------------------------------------+
                                     |  HTTP / JWT (Bearer Token)
                                     v
+------------------------------------+------------------------------------+
|                         SECURITY & API GATEWAY                          |
|  FastAPI (Port 8000) | CORS Whitelist | Security Headers | Rate Limiter |
+------------------+-----------------+-------------------+----------------+
                   |                 |                   |
                   v                 v                   v
            +--------------+  +--------------+   +---------------+
            | User & Auth  |  |  Portfolio   |   |   Audit Log   |
            | (BCrypt/JWT) |  | Intelligence |   |   (Events)    |
            +--------------+  +-------+------+   +---------------+
                                      |
                                      v
+-------------------------------------+-----------------------------------+
|               AUTONOMOUS SURVEILLANCE & RISK ENGINE                     |
|  Anomaly Detector (z-scores) | Event Classifier | Deterministic Risk   |
|  What-If Scenario Stress Testing | Alert Prioritizer & Deduplication   |
+-------------------------------------+-----------------------------------+
                                      |
                                      v
+-------------------------------------+-----------------------------------+
|               MULTI-AGENT AUTONOMOUS INTELLIGENCE                       |
|                   Agent Orchestrator (Asyncio)                          |
|         +---------------+---------------+---------------+               |
|         |               |               |               |               |
|         v               v               v               v               |
|    Technical       Fundamental      Sentiment        Research           |
|    Momentum        Valuation       Market Mood      RAG Filings         |
|         |               |               |               |               |
|         +---------------+---------------+---------------+               |
|                                 |                                       |
|                                 v                                       |
|        Result Collector -> Conflict Detector -> Synthesis Agent         |
|                                 |                                       |
|                                 v                                       |
|                  Personalization Layer -> Recommendation                |
+---------------------------------+---------------------------------------+
                                  |
                                  v
+---------------------------------+---------------------------------------+
|                    DATA & PERSISTENCE LAYER                             |
|  SQLite/Postgres (`mats.db`) | In-Memory Cache TTL | Local Vectors     |
|  SEC Edgar Filings | 384-dim Dense Semantic Embeddings | Citations     |
+-------------------------------------------------------------------------+
```

---

## 2. System Boundaries

### 2.1 Security Boundary
- **External Exposure**: Only ports `5173` (Frontend) and `8000` (FastAPI backend) are bound to `127.0.0.1`.
- **Credential Storage**: Passwords hashed with BCrypt. JWTs signed with `HS256`. No server-side secrets or API keys are exposed to client JavaScript.
- **SSRF Barrier**: File ingestion URLs targeting internal or loopback IP ranges are rejected before connection establishment.

### 2.2 Data Boundary
- **Tenant Isolation**: Every database access to portfolio holdings, watchlists, proactive alerts, scenarios, and research history enforces `user_id == current_user.id`.
- **Cache Isolation**: Cached market quotes and fundamental financial ratios are keyed by symbol without containing user-identifiable data.

### 2.3 AI & Trust Boundary
- **Data vs Instruction Separation**: External inputs are treated strictly as passive data, preventing prompt injection attacks.
- **No Hallucination Policy**: If data or document evidence is unavailable, agents return structured limitations rather than generating unverified numbers.

### 2.4 Decision Support Boundary
- MATS never connects to execution brokers, never places trades, and never handles private banking keys. All insights are presented with clear disclaimers for human evaluation.
