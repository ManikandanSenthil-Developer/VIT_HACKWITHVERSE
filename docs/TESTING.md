# MATS Platform — Testing & Verification Strategy

---

## 1. Automated Test Architecture
The test suite is built on `pytest` and `FastAPI TestClient`, executing full-stack unit and integration flows across all 5 project phases:

- `test_auth.py`: User registration, password hashing, JWT token refresh, invalid credential rejection.
- `test_portfolio.py`: Portfolio CRUD, holding valuation math, watchlist symbol management.
- `test_market.py`: Normalized market quotes, handling corrupt nulls, historical OHLCV ordering, company profiles, cache validation.
- `test_rag.py`: Text chunking, SHA-256 deduplication, vector similarity search, citation trace extraction.
- `test_security.py`: SSRF prevention, symbol sanitization, payload size enforcement, unauthenticated rejection.
- `test_intelligence.py`: Agent query routing, conflict detection, synthesis without hallucination, profile personalization framing, prompt injection neutralization.
- `test_portfolio_risk.py`: Deterministic risk engine scoring, factor explainability math, What-If scenario stress testing, user portfolio ownership isolation.
- `test_monitoring_alerts.py`: Anomaly detection triggers, severity personalization, alert clustering, user alert isolation, daily brief generation.
- `test_security_audit.py`: IDOR attacks, rate limiting, security headers, structured error handling without traceback leakage, user data deletion ("Right to be Forgotten"), and health check probes.

---

## 2. Running Automated Tests

```powershell
cd d:\WorkSpace\VIT\mats-platform\backend
& ".\pyenv\python.exe" -m pytest -v
```

---

## 3. Frontend Verification
```powershell
cd d:\WorkSpace\VIT\mats-platform\frontend
npm run build
```
Confirms clean compilation with TypeScript strict type checking.
