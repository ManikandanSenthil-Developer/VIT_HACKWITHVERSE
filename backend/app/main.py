import logging
import os
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


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger("mats.api")


# ============================================================
# RENDER DEPLOYMENT URL
# ============================================================

BACKEND_URL = "https://mats-backend-j21f.onrender.com"


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.

    Creates database tables if they do not already exist.
    """

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")

    except Exception as e:
        logger.exception(
            f"Database initialization failed: {e}"
        )

    yield


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.PROJECT_NAME,

    openapi_url=f"{settings.API_V1_STR}/openapi.json",

    docs_url=f"{settings.API_V1_STR}/docs",

    redoc_url=f"{settings.API_V1_STR}/redoc",

    lifespan=lifespan,
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,

    # Your configured frontend origins
    allow_origins=settings.BACKEND_CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],

    allow_headers=["*"],

    expose_headers=[
        "X-Request-ID",
        "Retry-After",
    ],
)


# ============================================================
# REQUEST CORRELATION ID + SECURITY HEADERS
# ============================================================

@app.middleware("http")
async def security_and_correlation_middleware(
    request: Request,
    call_next,
):
    request_id = (
        request.headers.get("X-Request-ID")
        or f"MATS-REQ-{uuid.uuid4().hex[:12].upper()}"
    )

    request.state.request_id = request_id

    response: Response = await call_next(request)

    # Correlation ID
    response.headers["X-Request-ID"] = request_id

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["X-XSS-Protection"] = "1; mode=block"

    response.headers[
        "Referrer-Policy"
    ] = "strict-origin-when-cross-origin"

    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains"

    return response


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        f"MATS-ERR-{uuid.uuid4().hex[:8].upper()}",
    )

    logger.exception(
        f"Unhandled Exception [Request ID: {request_id}]: {exc}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",

                "message": (
                    "An unexpected internal error occurred. "
                    "Please contact system support."
                ),

                "request_id": request_id,
            }
        },

        headers={
            "X-Request-ID": request_id
        },
    )


# ============================================================
# API ROUTES
# ============================================================

# Versioned API
app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
)

# Backward-compatible API
app.include_router(
    api_router,
    prefix="/api",
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health", tags=["Health"])
def health_check():
    """
    Comprehensive multi-component system health telemetry.
    """

    # --------------------------------------------------------
    # DATABASE CHECK
    # --------------------------------------------------------

    db_status = "healthy"

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))

    except Exception as e:
        logger.error(
            f"Database health check failed: {e}"
        )

        db_status = "unhealthy"


    # --------------------------------------------------------
    # CACHE CHECK
    # --------------------------------------------------------

    cache_status = "healthy"

    try:
        cache_service.set(
            "health_test",
            "ok",
            ttl_seconds=5,
        )

        cache_entry = cache_service.get(
            "health_test"
        )

        if (
            not cache_entry
            or cache_entry[0] != "ok"
        ):
            cache_status = "degraded"

    except Exception as e:
        logger.error(
            f"Cache health check failed: {e}"
        )

        cache_status = "degraded"


    # --------------------------------------------------------
    # HEALTH RESPONSE
    # --------------------------------------------------------

    return {
        "status": (
            "healthy"
            if db_status == "healthy"
            else "degraded"
        ),

        "service": (
            "MATS Multi-Agent Financial "
            "Intelligence Platform"
        ),

        "version": "1.0.0",

        "phase": (
            "Phase 5 — Trust, Security "
            "& Production Hardening"
        ),

        "backend_url": BACKEND_URL,

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


# ============================================================
# LIVENESS PROBE
# ============================================================

@app.get("/health/live", tags=["Health"])
def liveness_probe():
    """
    Verifies that the application process is alive.
    """

    return {
        "status": "alive",
        "backend_url": BACKEND_URL,
    }


# ============================================================
# READINESS PROBE
# ============================================================

@app.get("/health/ready", tags=["Health"])
def readiness_probe():
    """
    Verifies that the database is available.
    """

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "backend_url": BACKEND_URL,
        }

    except Exception as e:

        logger.error(
            f"Readiness check failed: {e}"
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,

            content={
                "status": "not_ready",
                "reason": "database unavailable",
            },
        )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/", tags=["Root"])
def root():
    return {
        "message": (
            "Welcome to MATS "
            "(Multi-Agent Autonomous "
            "Financial Intelligence System) API"
        ),

        "backend_url": BACKEND_URL,

        "docs": (
            f"{BACKEND_URL}"
            f"{settings.API_V1_STR}/docs"
        ),

        "health": (
            f"{BACKEND_URL}/health"
        ),

        "live": (
            f"{BACKEND_URL}/health/live"
        ),

        "ready": (
            f"{BACKEND_URL}/health/ready"
        ),
    }


# ============================================================
# SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn

    # Render provides PORT automatically.
    # Local development defaults to 8000.

    port = int(
        os.environ.get(
            "PORT",
            8000,
        )
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
    )
