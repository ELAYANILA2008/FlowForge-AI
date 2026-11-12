"""Unit tests for Payment and Transaction backend foundation (Phase 6).

Verifies:
1. Payment creation linked to valid workflow & registration.
2. Decimal-safe monetary arithmetic across supported currencies (USD, EUR, INR).
3. Rejection of invalid amounts (zero or negative).
4. Strict currency validation and rejection of unsupported currencies.
5. Transaction persistence and audit trail generation.
6. Payment lifecycle status transitions and registration state synchronization.
7. Route endpoints for payments and transactions.
"""

import sys
import os
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.base import Base
from app.models.workflow import WorkflowModel
from app.models.registration import RegistrationModel
from app.models.payment import PaymentModel
from app.models.transaction import TransactionModel
from app.schemas.payment import (
    PaymentCreateRequest,
    PaymentStatusUpdateRequest,
    TransactionCreateRequest,
)
from app.services.payment_service import (
    payment_service,
    MockPayPalOrderService,
)
from app.routes.payments import (
    create_payment,
    get_payment,
    update_payment_status,
    create_transaction,
    list_registration_payments,
)
from app.core.exceptions import (
    EntityNotFoundException,
    PaymentException,
)


@pytest.fixture(scope="function")
def db_session():
    """Create an isolated in-memory SQLite database session for testing."""
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_workflow_and_registration(db_session):
    """Seed a sample workflow and registration for payment tests."""
    wf = WorkflowModel(
        title="Python Fullstack Bootcamp",
        price=Decimal("49.00"),
        currency="USD",
        capacity=30,
        status="active",
    )
    db_session.add(wf)
    db_session.commit()

    reg = RegistrationModel(
        workflow_id=wf.id,
        customer_name="Jane Doe",
        customer_email="jane@example.com",
        registration_status="pending",
    )
    db_session.add(reg)
    db_session.commit()

    return wf, reg


# ── Payment Creation Tests ───────────────────────────────────────────────────

def test_payment_creation_defaults_to_workflow_price(db_session, sample_workflow_and_registration):
    """Payment without explicit amount/currency inherits from workflow."""
    wf, reg = sample_workflow_and_registration

    payload = PaymentCreateRequest(registration_id=reg.id)
    result = payment_service.create_payment(db=db_session, payload=payload)

    assert result["registration_id"] == reg.id
    assert result["amount"] == 49.0
    assert result["currency"] == "USD"
    assert result["payment_status"] == "unpaid"
    assert result["id"] is not None


def test_payment_creation_with_inr_currency(db_session, sample_workflow_and_registration):
    """Payment can be created with INR currency and explicit Decimal amount."""
    wf, reg = sample_workflow_and_registration

    payload = PaymentCreateRequest(
        registration_id=reg.id,
        amount=Decimal("3999.00"),
        currency="inr",
        paypal_order_id="ORD-INR-12345",
    )
    result = payment_service.create_payment(db=db_session, payload=payload)

    assert result["amount"] == 3999.0
    assert result["currency"] == "INR"
    assert result["paypal_order_id"] == "ORD-INR-12345"


def test_payment_creation_with_eur_currency(db_session, sample_workflow_and_registration):
    """Payment can be created with EUR currency."""
    wf, reg = sample_workflow_and_registration

    payload = PaymentCreateRequest(
        registration_id=reg.id,
        amount=Decimal("75.50"),
        currency="EUR",
    )
    result = payment_service.create_payment(db=db_session, payload=payload)

    assert result["amount"] == 75.5
    assert result["currency"] == "EUR"


def test_payment_creation_invalid_registration_rejected(db_session):
    """Creating payment for non-existent registration raises EntityNotFoundException."""
    payload = PaymentCreateRequest(registration_id="non-existent-reg-id")
    with pytest.raises(EntityNotFoundException):
        payment_service.create_payment(db=db_session, payload=payload)


def test_payment_creation_zero_or_negative_amount_rejected():
    """Schema rejects zero or negative payment amounts."""
    with pytest.raises(ValueError, match="greater than zero"):
        PaymentCreateRequest(
            registration_id="reg-123",
            amount=Decimal("0.00"),
        )

    with pytest.raises(ValueError, match="greater than zero"):
        PaymentCreateRequest(
            registration_id="reg-123",
            amount=Decimal("-15.00"),
        )


def test_payment_unsupported_currency_rejected():
    """Schema rejects unsupported currencies outside USD, EUR, INR."""
    with pytest.raises(ValueError, match="Unsupported currency"):
        PaymentCreateRequest(
            registration_id="reg-123",
            amount=Decimal("20.00"),
            currency="GBP",
        )

    with pytest.raises(ValueError, match="Unsupported currency"):
        PaymentCreateRequest(
            registration_id="reg-123",
            amount=Decimal("20.00"),
            currency="XYZ",
        )


# ── Transaction Persistence Tests ────────────────────────────────────────────

def test_transaction_persistence(db_session, sample_workflow_and_registration):
    """Transactions can be created and linked to payment for audit trails."""
    wf, reg = sample_workflow_and_registration

    pay_res = payment_service.create_payment(
        db=db_session,
        payload=PaymentCreateRequest(registration_id=reg.id),
    )
    payment_id = pay_res["id"]

    tx_payload = TransactionCreateRequest(
        verification_status="verified",
        transaction_reference="TXN-MANUAL-REF-99",
    )
    tx_res = payment_service.create_transaction(
        db=db_session,
        payment_id=payment_id,
        payload=tx_payload,
    )

    assert tx_res["payment_id"] == payment_id
    assert tx_res["transaction_reference"] == "TXN-MANUAL-REF-99"
    assert tx_res["verification_status"] == "verified"

    # Verify payment now includes this transaction in response
    fetched_pay = payment_service.get_payment(db=db_session, payment_id=payment_id)
    assert len(fetched_pay["transactions"]) == 1
    assert fetched_pay["transactions"][0]["transaction_reference"] == "TXN-MANUAL-REF-99"


# ── Payment Status Lifecycle Tests ───────────────────────────────────────────

def test_payment_status_update_to_paid_syncs_registration(db_session, sample_workflow_and_registration):
    """Updating status to 'paid' automatically updates registration status and records transaction."""
    wf, reg = sample_workflow_and_registration

    pay_res = payment_service.create_payment(
        db=db_session,
        payload=PaymentCreateRequest(registration_id=reg.id),
    )
    payment_id = pay_res["id"]

    update_payload = PaymentStatusUpdateRequest(
        payment_status="paid",
        paypal_order_id="ORD-CAPTURED-111",
        paypal_capture_id="CAP-111-SUCCESS",
    )
    updated = payment_service.update_payment_status(
        db=db_session,
        payment_id=payment_id,
        payload=update_payload,
    )

    assert updated["payment_status"] == "paid"
    assert updated["paypal_capture_id"] == "CAP-111-SUCCESS"

    # Verify registration is now 'paid'
    db_session.refresh(reg)
    assert reg.registration_status == "paid"

    # Verify audit transaction was recorded
    assert len(updated["transactions"]) >= 1
    assert updated["transactions"][0]["verification_status"] == "verified"


def test_payment_status_update_to_failed_syncs_registration(db_session, sample_workflow_and_registration):
    """Updating status to 'failed' marks registration as 'failed'."""
    wf, reg = sample_workflow_and_registration

    pay_res = payment_service.create_payment(
        db=db_session,
        payload=PaymentCreateRequest(registration_id=reg.id),
    )
    payment_id = pay_res["id"]

    update_payload = PaymentStatusUpdateRequest(payment_status="failed")
    updated = payment_service.update_payment_status(
        db=db_session,
        payment_id=payment_id,
        payload=update_payload,
    )

    assert updated["payment_status"] == "failed"
    db_session.refresh(reg)
    assert reg.registration_status == "failed"


# ── Route Integration Tests ──────────────────────────────────────────────────

def test_payment_api_routes(db_session, sample_workflow_and_registration):
    """Test payment endpoints via route handler invocation."""
    wf, reg = sample_workflow_and_registration

    # 1. Create payment
    create_req = PaymentCreateRequest(registration_id=reg.id)
    create_resp = create_payment(payload=create_req, db=db_session)
    assert create_resp["success"] is True
    payment_id = create_resp["data"]["id"]

    # 2. Get payment
    get_resp = get_payment(payment_id=payment_id, db=db_session)
    assert get_resp["success"] is True
    assert get_resp["data"]["id"] == payment_id

    # 3. Create transaction
    tx_req = TransactionCreateRequest(verification_status="verified")
    tx_resp = create_transaction(payment_id=payment_id, payload=tx_req, db=db_session)
    assert tx_resp["success"] is True
    assert tx_resp["data"]["verification_status"] == "verified"

    # 4. Update status
    patch_req = PaymentStatusUpdateRequest(payment_status="verifying")
    patch_resp = update_payment_status(payment_id=payment_id, payload=patch_req, db=db_session)
    assert patch_resp["success"] is True
    assert patch_resp["data"]["payment_status"] == "verifying"

    # 5. List payments for registration
    list_resp = list_registration_payments(registration_id=reg.id, db=db_session)
    assert list_resp["success"] is True
    assert len(list_resp["data"]) == 1


# ── Mock PayPal Provider Test ────────────────────────────────────────────────

def test_mock_paypal_provider_interface():
    """Verify that MockPayPalOrderService implements the interface cleanly."""
    provider = MockPayPalOrderService()
    order = provider.create_order(amount=Decimal("50.00"), currency="USD", reference_id="REF-1")
    assert order["status"] == "CREATED"
    assert order["currency"] == "USD"
    assert order["mock"] is True

    cap = provider.capture_order(paypal_order_id="MOCK-ORDER-1")
    assert cap["status"] == "COMPLETED"
    assert cap["mock"] is True

    status_resp = provider.get_order_status(paypal_order_id="MOCK-ORDER-1")
    assert status_resp["status"] == "APPROVED"

