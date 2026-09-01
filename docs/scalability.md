# MATS Scalability & Growth Architecture

## 1. Current State: Single-Laptop Modular Monolith
The present architecture runs entirely within a single laptop with:
- FastAPI ASGI application process.
- Embedded local SQLite database (or local PostgreSQL 16 container).
- In-process sliding-window rate limiter.
- In-process asyncio multi-agent orchestrator.
- Local dense semantic vector projection (384-dimensional embeddings).

This enables sub-second responses, zero cloud spend, and zero network fragility.

---

## 2. Horizontal Scaling Roadmap (10,000+ Active Users)

```
                       [ Cloudflare Edge / WAF ]
                                  │
                       [ HTTPS Load Balancer ]
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
  [ API Node 1 ]           [ API Node 2 ]           [ API Node 3 ]
  (FastAPI Workers)        (FastAPI Workers)        (FastAPI Workers)
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
       [ Redis / Valkey Cluster ]        [ Primary PostgreSQL ]
       - Distributed Rate Limiter        - Connection Pooling (PgBouncer)
       - Market Quote TTL Cache          - Read Replicas for Analytics
       - Pub/Sub for Market Events       - Strict Foreign Keys
                 │
       [ Vector DB Cluster ]
       (pgvector / Qdrant)
       - SEC Edgar 10-K Chunks
```

---

## 3. Bottleneck Analysis & Mitigations

### 1. Multi-Agent LLM Invocations
- **Bottleneck**: Calling external LLM models concurrently for hundreds of simultaneous users would incur high API cost and rate limiting.
- **Mitigation**: Query classifier routes only necessary agents (e.g. Technical only for RSI inquiries). Aggressive deduplication and caching of company research summaries for 12 hours.

### 2. High-Frequency Market Quotes
- **Bottleneck**: Polling thousands of ticker symbols in real-time.
- **Mitigation**: Distributed in-memory cache with 60-second TTL prevents repeated API calls across users researching the same popular tickers (NVDA, AAPL, MSFT).

### 3. Regulatory Filings Ingestion
- **Bottleneck**: Chunking and embedding 100-page SEC 10-K filings.
- **Mitigation**: Offload heavy document ingestion to background asynchronous task workers, pre-indexing regulatory disclosures once upon publication.
