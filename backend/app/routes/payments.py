"""Payment and Transaction API routes.

Provides endpoints for:
- Creating payment records linked to registrations
- Initiating PayPal Orders API v2 checkout orders
- Authoritatively capturing PayPal orders server-side
- Verifying server-side PayPal order status
- Updating payment state and synchronizing registration status
- Recording transaction verification audit entries
"""

import logging
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.routes.auth import get_optional_current_user
from app.schemas.payment import (
    PaymentCreateRequest,
    PaymentResponse,
    PaymentStatusUpdateRequest,
    PayPalCreateOrderRequest,
    PayPalCreateOrderResponse,
    PayPalCaptureResponse,
    TransactionCreateRequest,
    TransactionResponse,
)
from app.services.payment_service import payment_service

logger = logging.getLogger("flowforge.routes.payments")

router = APIRouter(prefix="/payments", tags=["Payments"])


def _envelope(data, message: str = ""):
    """Standard API success envelope matching frontend ApiResponse<T>."""
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post(
    "",
    summary="Create or Initiate Payment Record",
    response_description="Created payment record",
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payload: PaymentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """Create a payment record for a registration, validating monetary limits and currency."""
    result = payment_service.create_payment(db=db, payload=payload)
    return _envelope(result, "Payment record created successfully")


# ── PayPal Orders API v2 Endpoints ──────────────────────────────────────────

@router.post(
    "/create-order",
    summary="Create PayPal Checkout Order",
    response_description="PayPal order details and approval redirect URL",
    status_code=status.HTTP_201_CREATED,
)
def create_paypal_order(
    payload: PayPalCreateOrderRequest,
    db: Session = Depends(get_db),
):
    """Initiate an official PayPal Orders v2 transaction for an event registration."""
    result = payment_service.initiate_paypal_order(
        db=db,
        registration_id=payload.registration_id,
        return_url=payload.return_url,
        cancel_url=payload.cancel_url,
    )
    return _envelope(result, "PayPal order created successfully")


@router.post(
    "/capture/{order_id}",
    summary="Capture PayPal Order Server-Side",
    response_description="Verified capture result and synchronized payment status",
)
def capture_paypal_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    """Capture an approved PayPal order server-side and update registration status."""
    result = payment_service.capture_paypal_order(db=db, paypal_order_id=order_id)
    return _envelope(result, "PayPal order captured and confirmed")


@router.get(
    "/verify/{order_id}",
    summary="Verify PayPal Order Status",
    response_description="Server-side PayPal order verification details",
)
def verify_paypal_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    """Authoritatively check server-side status of a PayPal order."""
    result = payment_service.verify_paypal_order(db=db, paypal_order_id=order_id)
    return _envelope(result)


# ── Standard Payment & Transaction Lookups ───────────────────────────────────

@router.get(
    "/{payment_id}",
    summary="Get Payment Details",
    response_description="Payment details with linked transaction audit trail",
)
def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve payment details and associated transactions by payment ID."""
    result = payment_service.get_payment(db=db, payment_id=payment_id)
    return _envelope(result)


@router.patch(
    "/{payment_id}/status",
    summary="Update Payment Status",
    response_description="Updated payment record",
)
def update_payment_status(
    payment_id: str,
    payload: PaymentStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update payment lifecycle state (e.g. paid, verifying, failed) and synchronize registration."""
    result = payment_service.update_payment_status(db=db, payment_id=payment_id, payload=payload)
    return _envelope(result, f"Payment status updated to '{payload.payment_status}'")


@router.post(
    "/{payment_id}/transactions",
    summary="Record Audit Transaction",
    response_description="Created transaction audit record",
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    payment_id: str,
    payload: TransactionCreateRequest,
    db: Session = Depends(get_db),
):
    """Record an audit transaction log entry for a payment."""
    result = payment_service.create_transaction(db=db, payment_id=payment_id, payload=payload)
    return _envelope(result, "Transaction recorded successfully")


@router.get(
    "/registration/{registration_id}",
    summary="List Payments for Registration",
    response_description="List of payments for given registration",
)
def list_registration_payments(
    registration_id: str,
    db: Session = Depends(get_db),
):
    """List all payment records created for a specific registration."""
    results = payment_service.list_payments_for_registration(db=db, registration_id=registration_id)
    return _envelope(results, f"Found {len(results)} payment record(s)")
