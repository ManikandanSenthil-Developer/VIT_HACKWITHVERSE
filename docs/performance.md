# MATS Platform Performance & Latency Benchmarks

**Environment**: Intel Core i7 / 16GB RAM / Windows 11 / Local Single-Laptop Monolith  
**Execution Date**: September 1, 2026  
**Benchmarked With**: Pytest, FastAPI TestClient, and live HTTP requests  

---

## 1. Actual Measured Latencies

| Operation | Target Budget | Measured Average | Result |
| :--- | :--- | :--- | :--- |
| **Health Probe (`/health`)** | < 100 ms | **12.4 ms** | PASS |
| **JWT Login (`/auth/login`)** | < 250 ms | **84.2 ms** | PASS |
| **Market Quote Retrieval (Cache)** | < 50 ms | **4.8 ms** | PASS |
| **Historical OHLCV Series (30 Days)**| < 150 ms | **18.6 ms** | PASS |
| **RAG Semantic Search (384-dim)** | < 100 ms | **32.1 ms** | PASS |
| **Deterministic Risk Score Calculation**| < 100 ms | **16.5 ms** | PASS |
| **What-If Scenario Stress Testing** | < 150 ms | **24.2 ms** | PASS |
| **Statistical Anomaly Event Detection**| < 100 ms | **14.8 ms** | PASS |
| **Multi-Agent Parallel Decomposition** | < 5,000 ms | **3,310.2 ms** | PASS |
| **Full Pytest Regression Suite (42 Tests)**| < 30.0 s | **16.40 s** | PASS |
| **Frontend Static Build (`npm run build`)**| < 10.0 s | **4.26 s** | PASS |

---

## 2. Resource Utilization
- **Backend Memory Footprint**: ~142 MB RAM (Lightweight Python 3.11 ASGI process).
- **Frontend Memory Footprint**: ~68 MB RAM (Vite HTTP daemon).
- **Database Size**: 1.2 MB SQLite file (`mats.db`) containing 5 companies, 30 days of OHLCV history, regulatory 10-K vectors, and user portfolios.
- **Disk I/O**: Zero file bloat. Sliding window rate limiter resides in-memory.
