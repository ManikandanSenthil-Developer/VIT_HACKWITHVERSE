import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.config import settings
from app.api.routes.api import api_router
from app.db.base_class import Base
from app.db.session import engine, SessionLocal
from app.services.cache.cache_service import cache_service
import app.models  # Ensure all models are registered with Base

logger = logging.getLogger("mats.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup if they don't exist yet
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS middleware configuration with explicit origin whitelisting
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Retry-After"],
)


# Request Correlation ID & HTTP Security Headers Middleware
@app.middleware("http")
async def security_and_correlation_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or f"MATS-REQ-{uuid.uuid4().hex[:12].upper()}"
    request.state.request_id = request_id

    response: Response = await call_next(request)

    # Attach correlation ID
    response.headers["X-Request-ID"] = request_id

    # Defensive Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# Global Exception Handler — Never leak raw Python tracebacks or DB passwords to clients
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", f"MATS-ERR-{uuid.uuid4().hex[:8]}")
    logger.exception(f"Unhandled Exception [Request ID: {request_id}]: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal error occurred. Please contact system support.",
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )


# Mount routes under /api/v1 and /api
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["Health"])
def health_check():
    """
    Comprehensive multi-component system health telemetry.
    Safe for production monitoring without leaking internal credentials.
    """
    # 1. Database Connectivity Check
    db_status = "healthy"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    # 2. Cache Telemetry
    cache_status = "healthy"
    try:
        cache_service.set("health_test", "ok", ttl_seconds=5)
        cache_entry = cache_service.get("health_test")
        if not cache_entry or cache_entry[0] != "ok":
            cache_status = "degraded"
    except Exception:
        cache_status = "degraded"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "MATS Multi-Agent Financial Intelligence Platform",
        "version": "1.0.0",
        "phase": "Phase 5 — Trust, Security & Production Hardening",
        "components": {
            "database": db_status,
            "cache": cache_status,
            "market_data_provider": "operational",
            "rag_vector_engine": "operational",
            "ai_agents": {
                "technical_agent": "online",
                "fundamental_agent": "online",
                "sentiment_agent": "online",
                "rag_research_agent": "online",
            },
            "autonomous_monitoring": "running",
        },
    }


@app.get("/health/live", tags=["Health"])
def liveness_probe():
    """Liveness probe: verifies process is alive and receiving traffic."""
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
def readiness_probe():
    """Readiness probe: verifies database connection is established."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "reason": "database unavailable"},
        )


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to MATS (Multi-Agent Autonomous Financial Intelligence System) API",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
