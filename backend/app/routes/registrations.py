"""Registration API routes — customer event and workshop sign-ups.

Frontend URL contract (from frontend/src/services/httpAdapter.ts):
  POST   /api/v1/registration/{workflowId}            → submit registration
  GET    /api/v1/registration/status/{submissionId}   → get registration status
  GET    /api/v1/registrations/workflow/{workflowId}  → list (owner only)

All successful responses are wrapped in the standard envelope:
  { "success": true, "data": <RegistrationResponse|RegistrationResponse[]>, ... }
"""

import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.routes.auth import get_current_user, get_optional_current_user
from app.schemas.registration import RegistrationCreateRequest, RegistrationResponse
from app.services.registration_service import registration_service

logger = logging.getLogger("flowforge.routes.registrations")

router = APIRouter(tags=["Registrations"])


def _envelope(data, message: str = ""):
    """Standard API success envelope matching frontend ApiResponse<T>."""
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── POST /registration/{workflowId} ─────────────────────────────────────────

@router.post(
    "/registration/{workflow_id}",
    summary="Submit Customer Registration",
    response_description="Registration confirmation with payment status",
    status_code=201,
)
def submit_registration(
    workflow_id: str,
    payload: RegistrationCreateRequest,
    db: Session = Depends(get_db),
    # Public endpoint — no auth required for customers to register
    current_user: User = Depends(get_optional_current_user),
):
    """Create a new customer registration for a workflow/event.

    Validates:
    - Workflow exists and is active
    - Seat capacity not exceeded (overbooking-safe)
    - No duplicate registration for the same email+workflow

    Returns the RegistrationSubmission matching the frontend contract.
    """
    result = registration_service.create_registration(
        db=db,
        workflow_id=workflow_id,
        student_name=payload.studentName,
        student_email=str(payload.studentEmail),
    )
    return _envelope(result, "Registration submitted successfully")


# ── GET /registration/status/{submissionId} ──────────────────────────────────

@router.get(
    "/registration/status/{submission_id}",
    summary="Get Registration Status",
    response_description="Current registration and payment status",
)
def get_registration_status(
    submission_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve the current status of a registration by its ID.

    Used by the frontend to poll payment completion after PayPal checkout.
    Public endpoint (customers can check their own status without auth).
    """
    result = registration_service.get_registration(db=db, registration_id=submission_id)
    return _envelope(result)


# ── GET /registrations/workflow/{workflowId} ─────────────────────────────────

@router.get(
    "/registrations/workflow/{workflow_id}",
    summary="List Registrations for Workflow",
    response_description="All registrations for a workflow (owner only)",
)
def list_workflow_registrations(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all customer registrations for a specific workflow.

    Restricted to the workflow owner (authenticated endpoint).
    Returns the list in reverse chronological order.
    """
    results = registration_service.list_registrations_for_workflow(
        db=db,
        workflow_id=workflow_id,
        owner_id=current_user.id,
    )
    return _envelope(results, f"Found {len(results)} registration(s)")

