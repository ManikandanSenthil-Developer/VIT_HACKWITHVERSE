# MATS Platform — Security Architecture & Policy

---

## 1. Authentication & Session Management
- **Password Security**: Passwords are cryptographically salted and hashed using `passlib[bcrypt]` with work factor 12. Plaintext passwords are never stored in the database, logged to telemetry, or transmitted in response payloads.
- **Session Tokens**: Implements JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`).
  - Short-lived Access Tokens: 30 minutes lifetime.
  - Refresh Tokens: 7 days lifetime with database revokability checks.
- **Brute Force Defense**: Login endpoints are governed by a sliding-window rate limiter (15 requests / minute) and failed authentication attempts are logged to `audit_logs`.

---

## 2. Authorization & IDOR Defense
- **Ownership Verification**: Every user-specific resource (portfolios, holdings, watchlists, proactive alerts, scenarios, analysis history) requires authenticated identity verification (`current_user.id`).
- **Zero Cross-Tenant Leakage**: Attempting to query `GET /api/v1/portfolio/{id}` or `GET /api/v1/alerts/{id}` belonging to another user automatically triggers a `404 Not Found` or `403 Forbidden` response.

---

## 3. Rate Limiting Policy
The platform implements an in-memory, thread-safe sliding window rate limiter in `backend/app/core/rate_limiter.py`:
- `POST /api/v1/auth/login`: 15 requests / minute
- `POST /api/v1/auth/register`: 10 requests / minute
- `POST /api/v1/intelligence/analyze`: 25 requests / minute (per user)
- `POST /api/v1/rag/ingest`: 15 requests / minute (per user)
- `POST /api/v1/monitoring/run`: 10 requests / minute
- Exceeded thresholds return `429 Too Many Requests` with a standard `Retry-After` header.

---

## 4. AI Safety & Prompt Injection Neutralization
- **Strict Data vs Instruction Boundary**: All external inputs (user prompts, news articles, SEC Edgar filings, retrieved chunks) are treated as untrusted passive DATA.
- **Forbidden Delimiters Sanitized**: Delimiters such as `SYSTEM:`, `ASSISTANT:`, `Ignore previous instructions`, `reveal system prompt`, `execute code` are sanitized and escaped before agent ingestion.
- **Zero Tool Execution by LLM**: AI agents produce structured financial research assessments; agents have zero access to shell commands, code execution sandboxes, or database mutation tools.

---

## 5. RAG Provenance & SSRF Guardrails
- **SSRF Validation**: URL document ingestion is validated against private network blocks (`127.0.0.1`, `localhost`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`).
- **Source Trust Classification**: Ingested filings are tagged with `trust_level` (`PRIMARY`, `OFFICIAL`, `SECONDARY`, `TERTIARY`, `UNKNOWN`). Official SEC Form 10-K and 10-Q filings are classified as `OFFICIAL`.
- **Payload Quotas**: Enforces a strict 10MB document ceiling and deduplicates content via SHA-256 hashing.

---

## 6. HTTP Defense & Security Headers
All responses emitted by the MATS API include defensive headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `X-Request-ID`: Unique correlation identifier for distributed tracing and error triage.
