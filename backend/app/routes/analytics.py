"""Dashboard Metrics, Agent Telemetry, and Activity Feed API Routes.

Frontend Contract Endpoints:
- GET /api/v1/metrics/dashboard -> Dashboard overview and multi-currency revenues
- GET /api/v1/metrics/agents    -> AI agent reliability and performance benchmarks
- GET /api/v1/activity          -> Real-time operational activity feed
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analytics import (
    ActivityFeedItem,
    AgentPerformanceMetric,
    DashboardMetrics,
)
from app.services.analytics_service import analytics_service

logger = logging.getLogger("flowforge.routes.analytics")

router = APIRouter(tags=["Metrics & Analytics"])


def _envelope(data, message: str = ""):
    """Standard API success envelope matching frontend ApiResponse<T>."""
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/metrics/dashboard",
    summary="Get Dashboard Metrics",
    response_description="System performance, workflow counters, and multi-currency revenues",
)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
):
    """Retrieve operational KPIs and segregated revenue totals for USD, INR, and EUR."""
    metrics = analytics_service.get_dashboard_metrics(db=db)
    return _envelope(metrics, "Dashboard metrics retrieved successfully")


@router.get(
    "/metrics/agents",
    summary="Get Agent Performance Metrics",
    response_description="Telemetry and reliability scores for FlowForge AI agents",
)
def get_agent_performance(
    db: Session = Depends(get_db),
):
    """Retrieve benchmark and performance scores for AI and operations agents."""
    agents = analytics_service.get_agent_performance(db=db)
    return _envelope(agents, "Agent performance metrics retrieved successfully")


@router.get(
    "/activity",
    summary="Get Real-Time Activity Feed",
    response_description="Unified chronological log of workflows, registrations, and payments",
)
def get_activity_feed(
    limit: Optional[int] = Query(default=25, ge=1, le=100, description="Number of activity items to retrieve"),
    db: Session = Depends(get_db),
):
    """Retrieve the real-time operational activity feed."""
    feed = analytics_service.get_activity_feed(db=db, limit=limit)
    return _envelope(feed, f"Found {len(feed)} activity event(s)")

