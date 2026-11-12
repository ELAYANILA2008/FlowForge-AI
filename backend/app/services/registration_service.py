"""Registration Service — transactional, capacity-safe customer registration.

Provides:
- create_registration(): overbooking-safe (SELECT ... FOR UPDATE), duplicate guard
- get_registration(): retrieve by registration ID
- list_registrations_for_workflow(): owner-facing list
- registration_to_response_dict(): serialises to RegistrationResponse-compatible dict
"""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    CapacityExceededException,
    DuplicateEntityException,
    EntityNotFoundException,
)
from app.models.registration import RegistrationModel
from app.models.workflow import WorkflowModel

logger = logging.getLogger("flowforge.services.registration")


# ── Serialiser ────────────────────────────────────────────────────────────────

def registration_to_response_dict(reg: RegistrationModel, workflow: WorkflowModel) -> Dict[str, Any]:
    """Convert a RegistrationModel to the RegistrationResponse-compatible dict.

    Matches frontend RegistrationSubmission shape exactly:
        id, workflowId, studentName, studentEmail, feeAmount, currency,
        paymentStatus, paypalTransactionId, emailConfirmed, registeredAt
    """
    # Determine paypal transaction id from latest PAID payment (if any)
    paypal_txn_id: Optional[str] = None
    email_confirmed: bool = False

    if reg.payments:
        for payment in reg.payments:
            if payment.payment_status == "paid" and payment.paypal_capture_id:
                paypal_txn_id = payment.paypal_capture_id
                email_confirmed = True
                break

    # Map internal registration_status → frontend paymentStatus
    _status_map = {
        "pending": "unpaid",
        "paid": "paid",
        "failed": "failed",
        "verifying": "verifying",
    }
    payment_status = _status_map.get(reg.registration_status, "unpaid")

    fee_amount = float(workflow.price) if isinstance(workflow.price, Decimal) else float(workflow.price or 0)

    return {
        "id": reg.id,
        "workflowId": reg.workflow_id,
        "studentName": reg.customer_name,
        "studentEmail": reg.customer_email,
        "feeAmount": fee_amount,
        "currency": workflow.currency,
        "paymentStatus": payment_status,
        "paypalTransactionId": paypal_txn_id,
        "emailConfirmed": email_confirmed,
        "registeredAt": reg.created_at.isoformat(),
    }


# ── Service operations ────────────────────────────────────────────────────────

class RegistrationService:
    """Handles all customer registration lifecycle operations."""

    def create_registration(
        self,
        db: Session,
        workflow_id: str,
        student_name: str,
        student_email: str,
    ) -> Dict[str, Any]:
        """Create a new registration with overbooking and duplicate protection.

        Uses SELECT ... FOR UPDATE on the workflow row to prevent concurrent
        overbooking in PostgreSQL. Falls back to a simple SELECT for SQLite
        (which does not support FOR UPDATE in the same way) since SQLite is
        used only for local dev/testing with low concurrency.

        Raises:
            EntityNotFoundException: Workflow does not exist or is not active.
            DuplicateEntityException: Email already registered for this workflow.
            CapacityExceededException: Workflow has no remaining seats.
        """
        student_email = student_email.strip().lower()

        # --- Lock the workflow row in PostgreSQL, plain SELECT in SQLite ------
        try:
            stmt = (
                select(WorkflowModel)
                .where(WorkflowModel.id == workflow_id)
                .with_for_update()
            )
            workflow: Optional[WorkflowModel] = db.execute(stmt).scalar_one_or_none()
        except Exception:
            # SQLite does not support FOR UPDATE; fall back
            workflow = db.execute(
                select(WorkflowModel).where(WorkflowModel.id == workflow_id)
            ).scalar_one_or_none()

        if workflow is None:
            raise EntityNotFoundException("Workflow", workflow_id)

        if workflow.status not in ("active", "draft"):
            raise EntityNotFoundException("Workflow", workflow_id)

        # --- Duplicate guard ---------------------------------------------------
        existing = db.execute(
            select(RegistrationModel).where(
                RegistrationModel.workflow_id == workflow_id,
                RegistrationModel.customer_email == student_email,
            )
        ).scalar_one_or_none()

        if existing is not None:
            raise DuplicateEntityException("Registration", "studentEmail", student_email)

        # --- Capacity check ---------------------------------------------------
        current_count: int = db.execute(
            select(func.count(RegistrationModel.id)).where(
                RegistrationModel.workflow_id == workflow_id
            )
        ).scalar_one()

        if current_count >= workflow.capacity:
            raise CapacityExceededException(
                current=current_count,
                limit=workflow.capacity,
                requested=1,
            )

        # --- Create registration -----------------------------------------------
        try:
            reg = RegistrationModel(
                workflow_id=workflow_id,
                customer_name=student_name.strip(),
                customer_email=student_email,
                registration_status="pending",
            )
            db.add(reg)
            db.commit()
            db.refresh(reg)
            db.refresh(workflow)   # refresh so payments relationship is accessible
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to persist registration for workflow %s: %s", workflow_id, exc)
            raise

        logger.info(
            "New registration [%s] for workflow '%s' by %s (seats: %d/%d)",
            reg.id, workflow.title, student_email, current_count + 1, workflow.capacity,
        )

        return registration_to_response_dict(reg, workflow)

    def get_registration(self, db: Session, registration_id: str) -> Dict[str, Any]:
        """Retrieve a registration by its ID.

        Raises:
            EntityNotFoundException: Registration not found.
        """
        reg: Optional[RegistrationModel] = db.execute(
            select(RegistrationModel).where(RegistrationModel.id == registration_id)
        ).scalar_one_or_none()

        if reg is None:
            raise EntityNotFoundException("Registration", registration_id)

        # Eagerly load workflow for serialisation
        workflow: Optional[WorkflowModel] = db.execute(
            select(WorkflowModel).where(WorkflowModel.id == reg.workflow_id)
        ).scalar_one_or_none()

        if workflow is None:
            raise EntityNotFoundException("Workflow", reg.workflow_id)

        return registration_to_response_dict(reg, workflow)

    def list_registrations_for_workflow(
        self,
        db: Session,
        workflow_id: str,
        owner_id: str,
    ) -> List[Dict[str, Any]]:
        """List all registrations for a workflow (owner-only).

        Raises:
            EntityNotFoundException: Workflow not found or not owned by caller.
        """
        workflow: Optional[WorkflowModel] = db.execute(
            select(WorkflowModel).where(
                WorkflowModel.id == workflow_id,
                WorkflowModel.owner_id == owner_id,
            )
        ).scalar_one_or_none()

        if workflow is None:
            raise EntityNotFoundException("Workflow", workflow_id)

        regs: List[RegistrationModel] = (
            db.execute(
                select(RegistrationModel)
                .where(RegistrationModel.workflow_id == workflow_id)
                .order_by(RegistrationModel.created_at.desc())
            )
            .scalars()
            .all()
        )

        return [registration_to_response_dict(r, workflow) for r in regs]


# Module-level singleton
registration_service = RegistrationService()

