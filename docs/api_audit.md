# MATS Full API Endpoint & Security Audit

**Base URL**: `/api/v1`  
**Security Architecture**: PyJWT HS256, BCrypt, In-Memory Sliding-Window Rate Limiting, HTTP Security Headers  

---

## 1. Authentication & User Management
| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :---: | :---: |
| `POST` | `/auth/register` | Register new investor account | No | 10 / min |
| `POST` | `/auth/login` | Authenticate & issue access/refresh tokens | No | 15 / min |
| `POST` | `/auth/refresh` | Exchange refresh token for new access token | No | 30 / min |
| `GET` | `/user/me` | Retrieve authenticated user profile | Yes | None |
| `DELETE`| `/user/me` | Right to be forgotten (cascading purge) | Yes | 5 / min |

---

## 2. Portfolio, Holdings & Watchlist
| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/portfolio/` | List user's active portfolios | Yes | None |
| `POST` | `/portfolio/` | Create new portfolio | Yes | None |
| `GET` | `/portfolio/{id}` | Get portfolio detail & verified holdings | Yes | None |
| `POST` | `/portfolio/{id}/holdings` | Add holding to portfolio (IDOR checked) | Yes | None |
| `DELETE`| `/portfolio/{id}/holdings/{hid}` | Liquidate / delete holding | Yes | None |
| `DELETE`| `/portfolio/{id}` | Delete portfolio and all holdings | Yes | None |
| `GET` | `/watchlist/` | Get user's active watchlist | Yes | None |
| `POST` | `/watchlist/` | Add/update symbols in watchlist | Yes | None |

---

## 3. Market Data & RAG Knowledge Engine
| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/market/quote/{symbol}` | Fetch normalized market quote | Yes | None |
| `GET` | `/market/history/{symbol}` | Fetch 30-day OHLCV price series | Yes | None |
| `GET` | `/market/company/{symbol}` | Fetch company profile & fundamentals | Yes | None |
| `POST` | `/rag/ingest` | Upload & chunk regulatory SEC Form 10-K | Yes | 15 / min |
| `GET` | `/rag/search` | Dense vector similarity retrieval | Yes | None |
| `GET` | `/rag/documents` | List indexed filing documents | Yes | None |

---

## 4. Multi-Agent Intelligence, Risk & Monitoring
| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :---: | :---: |
| `POST` | `/intelligence/analyze` | Multi-agent research query decomposition | Yes | 25 / min |
| `GET` | `/intelligence/history` | User's recent analysis reports | Yes | None |
| `GET` | `/intelligence/daily-brief` | Synthesized daily financial intelligence | Yes | None |
| `GET` | `/risk/portfolio/{id}` | Deterministic 5-factor risk scoring | Yes | None |
| `POST` | `/scenarios/run` | Mathematical What-If stress testing | Yes | None |
| `GET` | `/alerts/` | Filtered proactive alerts feed | Yes | None |
| `PATCH`| `/alerts/{id}` | Dismiss or update alert status | Yes | None |
| `POST` | `/alerts/dismiss-all` | Batch dismiss all active alerts | Yes | None |
| `POST` | `/monitoring/run` | Trigger autonomous surveillance sweep | Yes | None |
| `GET` | `/monitoring/metrics` | System operational metrics & latency | No | None |

---

## 5. Demo Resilience & Scenarios (Phase 6)
| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/demo/status` | Verify demo dataset completeness | No | None |
| `POST` | `/demo/reset` | Reset demo state to pristine baseline | Yes | None |
| `POST` | `/demo/scenarios/1` | Run Scenario 1: Normal NVDA Analysis | Yes | None |
| `POST` | `/demo/scenarios/2` | Run Scenario 2: TSLA Agent Conflict | Yes | None |
| `POST` | `/demo/scenarios/3` | Run Scenario 3: NVDA Portfolio Anomaly | Yes | None |
