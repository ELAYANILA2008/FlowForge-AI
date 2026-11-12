"""FlowForge AI Backend Application.

Main FastAPI application entry point configuring:
- CORS middleware for Next.js frontend (localhost:3000)
- Global exception handlers and structured logging
- API versioning under /api/v1
- Health check and system diagnostic endpoints
- Routers for Authentication and Workflow operations
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.database.session import init_db
from app.routes.auth import router as auth_router
from app.routes.workflows import router as workflows_router
from app.routes.registrations import router as registrations_router
from app.routes.payments import router as payments_router
from app.routes.webhooks import router as webhooks_router
from app.routes.analytics import router as analytics_router

# Configure structured logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("flowforge.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle manager."""
    logger.info("Initializing FlowForge AI Backend v%s in [%s] mode", settings.APP_VERSION, settings.ENVIRONMENT)
    logger.info("Database URL: %s", settings.get_masked_secret(settings.DATABASE_URL))
    logger.info("CORS Origins: %s", settings.CORS_ORIGINS)
    logger.info("PayPal Mode: %s", "Mock/Simulated" if not settings.PAYPAL_CLIENT_ID else "PayPal Sandbox")
    logger.info("AI Engine Mode: %s", "Mock AI Client" if settings.AI_ENGINE_USE_MOCK else "OpenAI API")

    # For SQLite (local dev), ensure all tables exist before serving requests.
    # PostgreSQL uses Alembic migrations ('alembic upgrade head') — skip auto-create there.
    if settings.is_sqlite:
        logger.info("SQLite detected — running init_db() to ensure schema is up to date")
        init_db()
        logger.info("SQLite schema initialization complete")

    yield
    logger.info("FlowForge AI Backend shutting down")


# Initialize FastAPI Application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated business operation generation and payment execution backend for FlowForge AI.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register centralized domain and HTTP exception handlers
setup_exception_handlers(app)


# ── Root & Diagnostic Endpoints ─────────────────────────────────────────────

@app.get(
    "/",
    tags=["Diagnostics"],
    summary="Root Service Status",
    response_description="Service overview and links to API documentation",
)
def root():
    """Returns basic service identification and API documentation links."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get(
    "/health",
    tags=["Diagnostics"],
    summary="System Health Check",
    response_description="System uptime, database status, and health telemetry",
)
@app.get(f"{settings.API_V1_PREFIX}/health", tags=["Diagnostics"], include_in_schema=False)
def health_check():
    """Health check endpoint for container orchestrators, load balancers, and monitoring."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "type": "sqlite" if settings.is_sqlite else "postgresql",
            "configured": bool(settings.DATABASE_URL),
        },
        "integrations": {
            "ai_engine": "mock" if settings.AI_ENGINE_USE_MOCK else "openai",
            "paypal": "configured" if settings.PAYPAL_CLIENT_ID else "sandbox_demo",
            "email": "enabled" if settings.EMAIL_ENABLED else "mock_logged",
        },
    }


# ── Mount Versioned API Routers (/api/v1) ───────────────────────────────────

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(workflows_router, prefix=settings.API_V1_PREFIX)
app.include_router(registrations_router, prefix=settings.API_V1_PREFIX)
app.include_router(payments_router, prefix=settings.API_V1_PREFIX)
app.include_router(webhooks_router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)
