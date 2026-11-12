"""Pydantic schemas for Dashboard Metrics, Agent Telemetry, and Activity Feeds.

Matches frontend types defined in frontend/src/types/metrics.ts:
- DashboardMetrics
- AgentPerformanceMetric
- ActivityFeedItem
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class RevenueTrendItem(BaseModel):
    """Daily revenue and registration trend data point."""
    date: str
    amount: float
    registrations: int


class ExecutionTrendItem(BaseModel):
    """Daily execution success/failure trend data point."""
    date: str
    successful: int
    failed: int


class DashboardMetrics(BaseModel):
    """Aggregated operational telemetry and financial performance."""
    totalWorkflows: int
    activeWorkflows: int
    successfulExecutions: int
    failedExecutions: int
    totalRegistrations: int
    totalRevenueUsd: float
    totalRevenueInr: float
    totalRevenueEur: float
    overallTaskCompletionRate: float
    avgExecutionTimeSeconds: float
    systemReliabilityScore: float
    revenueTrend: List[RevenueTrendItem] = Field(default_factory=list)
    executionTrend: List[ExecutionTrendItem] = Field(default_factory=list)


class AgentPerformanceMetric(BaseModel):
    """Real-time performance benchmark for specialized AI operation agents."""
    id: str
    name: str
    role: str
    model: str
    taskCompletionRate: float
    workflowSuccessRate: float
    avgExecutionTimeMs: int
    reliabilityScore: float
    totalTasksProcessed: int
    failedTaskCount: int
    recoveryRate: float
    status: Literal["optimal", "monitoring", "degraded"]
    lastBenchmarkedAt: str


class ActivityFeedItem(BaseModel):
    """Event entry in the live operational activity stream."""
    id: str
    workflowId: str
    workflowTitle: str
    type: Literal["registration", "payment", "email", "error", "created"]
    title: str
    description: str
    timestamp: str
    amount: Optional[float] = None
    status: Literal["success", "pending", "failed"]

