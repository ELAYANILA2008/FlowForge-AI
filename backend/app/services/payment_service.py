"""Payment Service — Financial operations, payment tracking, and transaction persistence.

SECURITY & INTEGRITY:
- Uses Decimal for all monetary arithmetic.
- Supports USD, EUR, and INR.
- Verifies registration and workflow integrity before initiating payments.
- Records immutable financial audit transactions for payment events.
- Prepares abstract interface for future PayPal Orders API v2 Sandbox integration.
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EntityNotFoundException,
    PaymentException,
)
from app.core.security import generate_reference_id
from app.models.payment import PaymentModel
from app.models.registration import RegistrationModel
from app.models.transaction import TransactionModel
from app.models.workflow import WorkflowModel
from app.schemas.payment import PaymentCreateRequest, PaymentStatusUpdateRequest, TransactionCreateRequest
from app.utils.currency import normalize_currency, to_decimal_amount

logger = logging.getLogger("flowforge.services.payment")

VALID_PAYMENT_STATUSES = {"unpaid", "pending", "verifying", "paid", "failed", "refunded"}


def transaction_to_response_dict(tx: TransactionModel) -> Dict[str, Any]:
    """Convert a TransactionModel to a clean JSON-serializable dictionary."""
    return {
        "id": tx.id,
        "payment_id": tx.payment_id,
        "transaction_reference": tx.transaction_reference,
        "verification_status": tx.verification_status,
        "created_at": tx.created_at.isoformat() if tx.created_at else "",
    }


def payment_to_response_dict(payment: PaymentModel) -> Dict[str, Any]:
    """Convert a PaymentModel to a clean JSON-serializable dictionary."""
    fee_float = float(payment.amount) if isinstance(payment.amount, Decimal) else float(payment.amount or 0)
    tx_list = [transaction_to_response_dict(tx) for tx in (payment.transactions or [])]
    return {
        "id": payment.id,
        "registration_id": payment.registration_id,
        "paypal_order_id": payment.paypal_order_id,
        "paypal_capture_id": payment.paypal_capture_id,
        "amount": fee_float,
        "currency": payment.currency,
        "payment_status": payment.payment_status,
        "created_at": payment.created_at.isoformat() if payment.created_at else "",
        "transactions": tx_list,
    }


# ── PayPal Sandbox Service Interface ─────────────────────────────────────────

class IPayPalOrderService(ABC):
    """Clean interface abstraction for future PayPal Orders API v2 Sandbox integration."""

    @abstractmethod
    def create_order(
        self,
        amount: Decimal,
        currency: str,
        reference_id: str,
        description: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an order on PayPal Sandbox."""
        pass

    @abstractmethod
    def capture_order(self, paypal_order_id: str) -> Dict[str, Any]:
        """Capture an authorized order on PayPal Sandbox."""
        pass

    @abstractmethod
    def get_order_status(self, paypal_order_id: str) -> Dict[str, Any]:
        """Check status of an order on PayPal Sandbox."""
        pass


class MockPayPalOrderService(IPayPalOrderService):
    """Stub / Mock PayPal provider for development and testing prior to Sandbox credentials."""

    def create_order(
        self,
        amount: Decimal,
        currency: str,
        reference_id: str,
        description: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_curr = normalize_currency(currency)
        dec_amount = to_decimal_amount(amount)
        mock_id = f"MOCK-PAYPAL-{generate_reference_id('ORD')}"
        mock_approve = f"https://www.sandbox.paypal.com/checkoutnow?token={mock_id}"
        logger.info("Mock PayPal create_order called for %s %s (ref: %s)", dec_amount, normalized_curr, reference_id)
        return {
            "id": mock_id,
            "status": "CREATED",
            "amount": str(dec_amount),
            "currency": normalized_curr,
            "approve_url": mock_approve,
            "mock": True,
        }

    def capture_order(self, paypal_order_id: str) -> Dict[str, Any]:
        mock_cap_id = f"MOCK-CAP-{generate_reference_id('CAP')}"
        logger.info("Mock PayPal capture_order called for order %s", paypal_order_id)
        return {
            "id": mock_cap_id,
            "status": "COMPLETED",
            "order_id": paypal_order_id,
            "mock": True,
        }

    def get_order_status(self, paypal_order_id: str) -> Dict[str, Any]:
        return {
            "id": paypal_order_id,
            "status": "APPROVED",
            "mock": True,
        }


# ── Core Payment Service ─────────────────────────────────────────────────────

class PaymentService:
    """Handles payment tracking, monetary validation, and transaction persistence."""

    def __init__(self, paypal_provider: Optional[IPayPalOrderService] = None):
        if paypal_provider is not None:
            self.paypal_provider = paypal_provider
        else:
            try:
                from app.services.paypal_service import get_paypal_service
                self.paypal_provider = get_paypal_service()
            except Exception:
                self.paypal_provider = MockPayPalOrderService()

    def create_payment(
        self,
        db: Session,
        payload: PaymentCreateRequest,
    ) -> Dict[str, Any]:
        """Create a payment record linked to a valid registration and workflow."""
        # 1. Verify registration exists
        reg: Optional[RegistrationModel] = db.execute(
            select(RegistrationModel).where(RegistrationModel.id == payload.registration_id)
        ).scalar_one_or_none()

        if reg is None:
            raise EntityNotFoundException("Registration", payload.registration_id)

        # 2. Verify associated workflow exists
        workflow: Optional[WorkflowModel] = db.execute(
            select(WorkflowModel).where(WorkflowModel.id == reg.workflow_id)
        ).scalar_one_or_none()

        if workflow is None:
            raise EntityNotFoundException("Workflow", reg.workflow_id)

        # 3. Determine and validate amount using Decimal
        if payload.amount is not None:
            payment_amount = to_decimal_amount(payload.amount)
        else:
            payment_amount = to_decimal_amount(workflow.price)

        if payment_amount <= Decimal("0.00"):
            raise PaymentException("Payment amount must be greater than zero.")

        # 4. Determine and validate currency
        if payload.currency is not None:
            payment_currency = normalize_currency(payload.currency)
        else:
            payment_currency = normalize_currency(workflow.currency)

        # 5. Persist payment record
        try:
            payment = PaymentModel(
                registration_id=reg.id,
                amount=payment_amount,
                currency=payment_currency,
                paypal_order_id=payload.paypal_order_id,
                payment_status="unpaid",
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to persist payment for registration %s: %s", reg.id, exc)
            raise

        logger.info(
            "Created payment [%s] for registration [%s] — %s %s (status=%s)",
            payment.id, reg.id, payment.amount, payment.currency, payment.payment_status,
        )

        return payment_to_response_dict(payment)

    def get_payment(self, db: Session, payment_id: str) -> Dict[str, Any]:
        """Retrieve a payment record by ID with associated transactions."""
        payment: Optional[PaymentModel] = db.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        ).scalar_one_or_none()

        if payment is None:
            raise EntityNotFoundException("Payment", payment_id)

        return payment_to_response_dict(payment)

    def list_payments_for_registration(self, db: Session, registration_id: str) -> List[Dict[str, Any]]:
        """List all payments associated with a specific registration."""
        reg: Optional[RegistrationModel] = db.execute(
            select(RegistrationModel).where(RegistrationModel.id == registration_id)
        ).scalar_one_or_none()

        if reg is None:
            raise EntityNotFoundException("Registration", registration_id)

        payments: List[PaymentModel] = (
            db.execute(
                select(PaymentModel)
                .where(PaymentModel.registration_id == registration_id)
                .order_by(PaymentModel.created_at.desc())
            )
            .scalars()
            .all()
        )

        return [payment_to_response_dict(p) for p in payments]

    def update_payment_status(
        self,
        db: Session,
        payment_id: str,
        payload: PaymentStatusUpdateRequest,
    ) -> Dict[str, Any]:
        """Update payment lifecycle status and synchronize registration state."""
        payment: Optional[PaymentModel] = db.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        ).scalar_one_or_none()

        if payment is None:
            raise EntityNotFoundException("Payment", payment_id)

        new_status = payload.payment_status.strip().lower()
        if new_status not in VALID_PAYMENT_STATUSES:
            raise PaymentException(
                f"Invalid payment status '{new_status}'. Valid statuses: {sorted(list(VALID_PAYMENT_STATUSES))}"
            )

        try:
            payment.payment_status = new_status
            if payload.paypal_order_id:
                payment.paypal_order_id = payload.paypal_order_id
            if payload.paypal_capture_id:
                payment.paypal_capture_id = payload.paypal_capture_id

            # Sync linked registration state
            reg: Optional[RegistrationModel] = db.execute(
                select(RegistrationModel).where(RegistrationModel.id == payment.registration_id)
            ).scalar_one_or_none()

            if reg:
                if new_status == "paid":
                    reg.registration_status = "paid"
                    # Auto-record audit transaction upon confirmed payment
                    tx = TransactionModel(
                        payment_id=payment.id,
                        transaction_reference=payload.paypal_capture_id or generate_reference_id("TXN"),
                        verification_status="verified",
                    )
                    db.add(tx)
                elif new_status == "failed":
                    reg.registration_status = "failed"
                elif new_status == "verifying":
                    reg.registration_status = "verifying"

            db.commit()
            db.refresh(payment)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to update payment status [%s]: %s", payment_id, exc)
            raise

        logger.info("Payment [%s] status updated to '%s'", payment_id, new_status)
        return payment_to_response_dict(payment)

    def create_transaction(
        self,
        db: Session,
        payment_id: str,
        payload: TransactionCreateRequest,
    ) -> Dict[str, Any]:
        """Record an immutable transaction audit log entry for a payment."""
        payment: Optional[PaymentModel] = db.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        ).scalar_one_or_none()

        if payment is None:
            raise EntityNotFoundException("Payment", payment_id)

        ref = payload.transaction_reference or generate_reference_id("TXN")

        try:
            tx = TransactionModel(
                payment_id=payment.id,
                transaction_reference=ref,
                verification_status=payload.verification_status,
            )
            db.add(tx)
            db.commit()
            db.refresh(tx)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to create transaction for payment [%s]: %s", payment_id, exc)
            raise

        logger.info("Recorded transaction [%s] for payment [%s] (ref=%s)", tx.id, payment.id, tx.transaction_reference)
        return transaction_to_response_dict(tx)

    def initiate_paypal_order(
        self,
        db: Session,
        registration_id: str,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a PayPal checkout order and persist the pending payment record."""
        reg: Optional[RegistrationModel] = db.execute(
            select(RegistrationModel).where(RegistrationModel.id == registration_id)
        ).scalar_one_or_none()
        if reg is None:
            raise EntityNotFoundException("Registration", registration_id)

        workflow: Optional[WorkflowModel] = db.execute(
            select(WorkflowModel).where(WorkflowModel.id == reg.workflow_id)
        ).scalar_one_or_none()
        if workflow is None:
            raise EntityNotFoundException("Workflow", reg.workflow_id)

        amount = to_decimal_amount(workflow.price)
        currency = normalize_currency(workflow.currency)

        # Call PayPal provider (real sandbox or mock)
        order_res = self.paypal_provider.create_order(
            amount=amount,
            currency=currency,
            reference_id=reg.id,
            description=f"FlowForge AI - {workflow.title}",
            return_url=return_url,
            cancel_url=cancel_url,
        )

        paypal_order_id = order_res.get("id")
        approve_url = order_res.get("approve_url")

        # Create or update payment record
        payment = PaymentModel(
            registration_id=reg.id,
            amount=amount,
            currency=currency,
            paypal_order_id=paypal_order_id,
            payment_status="unpaid",
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {
            "order_id": paypal_order_id,
            "payment_id": payment.id,
            "status": order_res.get("status", "CREATED"),
            "approve_url": approve_url,
            "amount": float(amount),
            "currency": currency,
        }

    def capture_paypal_order(
        self,
        db: Session,
        paypal_order_id: str,
    ) -> Dict[str, Any]:
        """Capture an approved PayPal order server-side and verify completion."""
        payment: Optional[PaymentModel] = db.execute(
            select(PaymentModel).where(PaymentModel.paypal_order_id == paypal_order_id)
        ).scalar_one_or_none()
        if payment is None:
            raise EntityNotFoundException("Payment with PayPal Order", paypal_order_id)

        if payment.payment_status == "paid":
            logger.info("Payment [%s] already marked paid (idempotent capture request)", payment.id)
            return {
                "order_id": paypal_order_id,
                "capture_id": payment.paypal_capture_id or "",
                "payment_id": payment.id,
                "status": "COMPLETED",
                "amount": float(payment.amount),
                "currency": payment.currency,
                "registration_status": "paid",
            }

        # Authoritative capture via provider
        capture_res = self.paypal_provider.capture_order(paypal_order_id)
        status = capture_res.get("status")
        if status != "COMPLETED":
            raise PaymentException(
                f"PayPal capture failed: status is {status}",
                details={"paypal_order_id": paypal_order_id, "capture_response": capture_res},
            )

        capture_id = capture_res.get("capture_id") or capture_res.get("id") or generate_reference_id("CAP")
        payment.paypal_capture_id = capture_id
        payment.payment_status = "paid"

        # Sync registration
        reg: Optional[RegistrationModel] = db.execute(
            select(RegistrationModel).where(RegistrationModel.id == payment.registration_id)
        ).scalar_one_or_none()
        if reg:
            reg.registration_status = "paid"

        # Record audit transaction
        tx = TransactionModel(
            payment_id=payment.id,
            transaction_reference=capture_id,
            verification_status="verified",
        )
        db.add(tx)
        db.commit()
        db.refresh(payment)

        logger.info("PayPal order [%s] successfully captured as [%s] for payment [%s]", paypal_order_id, capture_id, payment.id)
        return {
            "order_id": paypal_order_id,
            "capture_id": capture_id,
            "payment_id": payment.id,
            "status": "COMPLETED",
            "amount": float(payment.amount),
            "currency": payment.currency,
            "registration_status": "paid",
        }

    def verify_paypal_order(
        self,
        db: Session,
        paypal_order_id: str,
    ) -> Dict[str, Any]:
        """Authoritatively query PayPal API for server-side order status."""
        payment: Optional[PaymentModel] = db.execute(
            select(PaymentModel).where(PaymentModel.paypal_order_id == paypal_order_id)
        ).scalar_one_or_none()
        if payment is None:
            raise EntityNotFoundException("Payment with PayPal Order", paypal_order_id)

        status_res = self.paypal_provider.get_order_status(paypal_order_id)
        return {
            "payment_id": payment.id,
            "paypal_order_id": paypal_order_id,
            "internal_payment_status": payment.payment_status,
            "paypal_order_status": status_res.get("status"),
            "details": status_res,
        }


payment_service = PaymentService()

