"""Pydantic schemas for workflow management, creation, updates, and frontend responses."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.utils.currency import to_decimal_amount, normalize_currency


class WorkflowStepSchema(BaseModel):
    """Schema representing an individual operational stage in the workflow."""
    id: str
    order: int
    type: str = Field(..., description="Step type: registration, payment, verification, email, analytics")
    title: str
    description: str
    iconName: str
    status: Optional[str] = "completed"
    config: Dict[str, Any] = Field(default_factory=dict)
    metrics: Optional[Dict[str, Any]] = None


class WorkflowStatsSchema(BaseModel):
    """Aggregated business telemetry and reliability metrics for a workflow."""
    totalRuns: int = 0
    successfulRuns: int = 0
    failedRuns: int = 0
    totalRevenue: float = 0.0
    totalRegistrations: int = 0
    capacityLimit: int = 50
    reliabilityScore: float = 100.0
    avgRunDurationMs: int = 1140


class GenerateWorkflowRequest(BaseModel):
    """Payload for AI-powered natural language workflow generation."""
    prompt: str = Field(..., min_length=3, description="Natural language business instruction")
    options: Optional[Dict[str, Any]] = None


class WorkflowCreateRequest(BaseModel):
    """Payload for manual or programmatic workflow creation."""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    prompt: Optional[str] = ""
    capacity: int = Field(default=50, ge=1, le=100_000)
    price: Decimal = Field(default=Decimal("20.00"), ge=Decimal("0.00"))
    currency: str = Field(default="USD")
    steps: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = "active"


class WorkflowUpdateRequest(BaseModel):
    """Payload for partial workflow configuration updates."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    capacity: Optional[int] = Field(default=None, ge=1)
    price: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))
    currency: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


class WorkflowStatusUpdateRequest(BaseModel):
    """Payload for activating, pausing, or completing a workflow."""
    status: str = Field(..., description="Target status: active, draft, paused, completed, failed")


class WorkflowResponse(BaseModel):
    """Frontend-compatible response envelope representing a complete workflow."""
    id: str
    title: str
    description: str
    prompt: str
    status: str
    createdAt: str
    updatedAt: str
    steps: List[Dict[str, Any]]
    stats: WorkflowStatsSchema
    tags: List[str]
    capacity: int
    price: float
    currency: str

