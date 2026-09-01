# MATS Platform — Trust, Safety & Financial Governance

---

## 1. Core Mission & Ethical Boundary
MATS (Multi-Agent Autonomous Financial Intelligence System) is strictly a **decision-support and research platform** designed to empower retail investors with institutional-grade financial intelligence.

### Absolute Boundaries:
1. **NO Trade Execution**: MATS never executes trades, places orders, or requests brokerage API execution keys.
2. **NO Guaranteed Returns**: Financial markets involve risk of loss. MATS never promises profit, guarantees yields, or claims risk-free returns.
3. **Human-in-the-Loop**: The investor retains 100% discretion and ownership of all financial decisions.

---

## 2. Zero-Fabrication Policy
To eliminate generative AI hallucinations in financial intelligence:
- **Market Data**: Quotes, historical OHLCV bars, and financial ratios are queried directly from verified market providers (Finnhub, Yahoo Finance, or local verified datasets).
- **Documents & Citations**: Official filings are ingested from SEC Edgar or verified company investor relations releases.
- **Fail-Safe Fallbacks**:
  - If market data is unavailable: *"Market data unavailable."*
  - If cached: *"Data may be stale (cached X minutes ago)."*
  - If document evidence is insufficient: *"Insufficient reliable evidence to substantiate this claim."*
  - Citations are never fabricated or guessed.

---

## 3. RAG Source Trust Hierarchy
Ingested research sources are classified into explicit trust tiers:
- **PRIMARY / OFFICIAL**: SEC Form 10-K, 10-Q, 8-K filings and regulatory press releases.
- **SECONDARY**: Audited institutional equity research and recognized financial press.
- **TERTIARY**: Industry sentiment surveys and analyst commentary.
- **UNKNOWN**: Unverified web mentions or unaccredited blog posts.

Research agents prioritize PRIMARY and OFFICIAL documentation during RAG vector retrieval.

---

## 4. Explainable AI Confidence
Every major AI assessment exposes an auditable confidence score (e.g. 82%).

> **Governance Principle**: Confidence reflects the mathematical consensus between specialized autonomous agents (Technical, Fundamental, Sentiment, RAG Research) and the empirical coverage of retrieved citations. It is **not a statistical probability** that a stock will increase or decrease in price.

---

## 5. Conflict Preservation & Agent Disagreement
When specialized autonomous agents reach opposing conclusions (e.g. Technical Momentum is POSITIVE while Fundamental Valuation is NEGATIVE):
- MATS **never** masks or averages out the disagreement.
- MATS highlights the conflict explicitly: *"Signal Conflict Detected: Technical indicators signal short-term bullish momentum, while fundamental balance sheet leverage signals elevated debt risk."*
- Uncovering divergence is a primary value proposition for retail investor risk mitigation.

---

## 6. Official Financial Disclaimers

### Short Form (Interface Banner):
> *"MATS provides AI-generated financial research and decision-support insights. It does not constitute investment advice or order execution. Verify all data independently."*

### Full Form (Reports & Disclosures):
> *"MATS (Multi-Agent Autonomous Financial Intelligence System) provides artificial intelligence research summaries, market surveillance telemetry, and scenario stress testing for informational and educational decision-support purposes only. MATS is not a registered investment advisor, broker-dealer, or financial analyst. Content generated does not constitute personalized financial, investment, legal, or tax advice, nor does it constitute an endorsement or solicitation to buy, sell, or hold any security. Past performance is no guarantee of future results. All investments carry risk, including the possible loss of principal. Users must conduct independent due diligence before making investment decisions."*
