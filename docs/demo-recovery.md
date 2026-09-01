# MATS 60-Second Demo Recovery Runbook

This runbook outlines immediate, deterministic recovery procedures if an unexpected failure occurs right before or during a live hackathon presentation.

---

## 1. Fast Diagnostic Matrix

| Failure Symptom | Cause | 60-Second Recovery Command |
| :--- | :--- | :--- |
| **Browser cannot connect to localhost:5173** | Frontend dev server terminated | `cd frontend && npm run dev` |
| **API calls return Network Error (port 8000)** | Backend ASGI server crashed | `cd backend && pyenv\python.exe -m uvicorn app.main:app --port 8000` |
| **"Demo User Not Found" on login** | Database unseeded | `cd backend && pyenv\python.exe scripts/seed_demo_data.py` |
| **External Market Data Provider Down** | Third-party rate limit / Wi-Fi drop | Pre-seeded quotes & hybrid provider seamlessly fallback to cached snapshots automatically. |
| **Simulated Alerts or Holdings Cluttered** | Dirty demo state | Click **"Reset Demo"** in UI or execute `scripts/reset-demo.ps1`. |
| **Database Corruption / Schema Glitch** | Bad migration or locked file | `cd backend && pyenv\python.exe scripts/restore_database.py` |

---

## 2. One-Command Full Environment Reset
If the presentation environment is in an unknown state, run this single command to restore 100% operational baseline:

```powershell
# From workspace root
& ".\scripts\demo-check.ps1"
```
If checks fail, run:
```powershell
& ".\scripts\reset-demo.ps1"
```

---

## 3. Emergency Presentation Fallback (Offline Mode)
Even with zero internet connectivity:
- The embedded semantic vector engine (`LocalSemanticEmbeddingProvider`) operates locally without cloud API calls.
- Multi-agent decomposition uses local heuristics, technical algorithms, and pre-indexed SEC Form 10-Ks.
- All 3 Hackathon Demo Scenarios (`POST /api/v1/demo/scenarios/{1,2,3}`) execute with 100% fidelity without hitting external networks.
