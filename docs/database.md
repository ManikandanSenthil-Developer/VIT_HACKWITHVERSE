# MATS Database Schema, Integrity & Migrations

**ORM**: SQLAlchemy 2.0  
**Migration Tool**: Alembic  
**Dialect Parity**: SQLite 3 (single-laptop local execution) & PostgreSQL 16+ (institutional container)  

---

## 1. Schema Relationships

```
Users (1) ────< (N) Portfolios (1) ────< (N) Holdings
  │                  │
  ├──── (1) InvestorProfile
  ├──── (1) Watchlist
  ├────< (N) AnalysisHistory
  ├────< (N) Alerts
  └────< (N) AuditLogs

Companies (1) ────< (N) Securities (1) ────< (N) PriceHistory
     │                        │
     ├────< (N) FundamentalData  └──── (1) MarketSnapshot
     └────< (N) Documents (1) ────< (N) DocumentChunks (with 384-dim embeddings)

MarketEvents (1) ────< (N) Alerts
```

---

## 2. Migration History

| Revision ID | Description |
| :--- | :--- |
| `f28ccbff4598` | Phase 1: Base User, InvestorProfile, Portfolio, Holding, Watchlist |
| `74c45f131c8a` | Phase 2: Company, Security, PriceHistory, MarketSnapshot, FundamentalData, Document, DocumentChunk |
| `8bd80ef2a060` | Phase 2: Add raw_content column to Document |
| `7e0c63526b4c` | Phase 3: AnalysisHistory multi-agent table |
| `4e23adfc2d64` | Phase 4: MarketEvent, Alert, ScenarioRun, MonitoringRun |
| `7c8de411741c` | Phase 5: AuditLog model and trust_level column on Document |

---

## 3. Integrity & Cascading Rules
- All user foreign keys enforce `ON DELETE CASCADE`: deleting a user via `DELETE /api/v1/user/me` immediately cascades to their portfolios, holdings, alerts, profile, watchlist, and analysis history without leaving orphan records.
- Portfolio holdings enforce foreign key integrity against `portfolios.id`.
- SEC Form 10-K document chunks enforce cascading deletion against `documents.id`.
