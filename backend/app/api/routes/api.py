from fastapi import APIRouter
from app.api.routes import (
    auth,
    user,
    profile,
    watchlist,
    portfolio,
    market,
    rag,
    intelligence,
    risk,
    scenarios,
    alerts,
    monitoring,
    demo,
    metrics,
    copilot,
    research,
    ecosystem,
    adaptive,
)

api_router = APIRouter()

# Phase 1 routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(profile.router, prefix="/profile", tags=["Investor Profile"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])

# Phase 2 routers
api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG Knowledge Engine"])

# Phase 3 router
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Multi-Agent Intelligence"])

# Phase 4 routers
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Engine"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenario Engine"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts & Notifications"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Autonomous Monitoring"])

# Phase 6 routers
api_router.include_router(demo.router, prefix="/demo", tags=["Demo Resilience & Scenarios"])
api_router.include_router(metrics.router, prefix="/monitoring", tags=["Observability & Metrics"])

# Phase 7 routers
api_router.include_router(copilot.router, prefix="/copilot", tags=["Investor Copilot"])
api_router.include_router(research.router, prefix="/research", tags=["Comparative & Research Intelligence"])

# Phase 8 routers
api_router.include_router(ecosystem.router, prefix="/ecosystem", tags=["Ecosystem, Accessibility & Portability"])

# Phase 9 routers
api_router.include_router(adaptive.router, prefix="/adaptive", tags=["Adaptive Intelligence & Knowledge Graph"])

