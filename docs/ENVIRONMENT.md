# MATS Platform — Environment Configuration Guide

---

## 1. Environment Configurations

| Variable | Type | Default | Description | Environment |
| :--- | :--- | :--- | :--- | :--- |
| `PROJECT_NAME` | string | `MATS - Multi-Agent Autonomous Financial Intelligence Platform` | Platform Name | Dev / Prod |
| `API_V1_STR` | string | `/api/v1` | Root API prefix | Dev / Prod |
| `JWT_SECRET` | string | `[REPLACE_IN_PRODUCTION]` | Secret key used for signing JWT tokens | Prod (Required) |
| `JWT_REFRESH_SECRET` | string | `[REPLACE_IN_PRODUCTION]` | Secret key for refresh tokens | Prod (Required) |
| `ALGORITHM` | string | `HS256` | Token cryptographic signing algorithm | Dev / Prod |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | `30` | Access token lifespan in minutes | Dev / Prod |
| `REFRESH_TOKEN_EXPIRE_DAYS` | integer | `7` | Refresh token lifespan in days | Dev / Prod |
| `DATABASE_URL` | string | `sqlite:///./mats.db` | Database connection URI (SQLite or PostgreSQL) | Dev / Prod |
| `BACKEND_CORS_ORIGINS` | list | `["http://localhost:5173", "http://127.0.0.1:5173"]` | Whitelisted frontend web origins | Prod (Strict) |
| `MARKET_DATA_PROVIDER` | string | `hybrid` | Provider (`hybrid`, `yahoo`, `mock`) | Dev / Prod |
| `FINNHUB_API_KEY` | string | `None` | Optional Finnhub API Key for real-time quotes | Prod / Optional |
| `EMBEDDING_PROVIDER` | string | `local` | Embedding engine (`local` 384-dim or `openai`) | Dev / Prod |
| `OPENAI_API_KEY` | string | `None` | Optional OpenAI key | Dev / Optional |
| `MAX_DOCUMENT_SIZE_BYTES` | integer | `10485760` (10MB) | Max document upload / ingestion size | Dev / Prod |

---

## 2. Production Hardening Rules
1. **Secrets Rotation**: Always set unique cryptographically random strings for `JWT_SECRET` and `JWT_REFRESH_SECRET` in `.env`.
2. **CORS Restrictions**: Never set wildcard origins in production environments.
3. **Debug Flags**: Keep FastAPI debug modes disabled in production.
4. **SSL / TLS Termination**: Place a reverse proxy (e.g. Nginx or Caddy) terminating HTTPS in front of Uvicorn when deployed to public domains.
