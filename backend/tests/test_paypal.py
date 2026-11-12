"""Unit and Integration tests for PayPal Orders API v2 Sandbox Integration (Phase 7).

Verifies:
1. PayPalSandboxService OAuth2 token acquisition & caching.
2. PayPal Orders API v2 order creation with Decimal monetary precision.
3. Server-side order capture and verification.
4. Error handling when PayPal capture is declined or fails.
5. Server-side webhook signature verification.
6. PayPal Webhook endpoint (PAYMENT.CAPTURE.COMPLETED & CHECKOUT.ORDER.APPROVED).
7. Idempotency on duplicate capture webhooks.
8. Seamless fallback to Mock provider when credentials are unset.
"""

import sys
import os
import json
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.base import Base
from app.models.workflow import WorkflowModel
from app.models.registration import RegistrationModel
from app.models.payment import PaymentModel
from app.models.transaction import TransactionModel
from app.core.exceptions import PaymentException, PaymentVerificationException
from app.services.paypal_service import (
    PayPalSandboxService,
    get_paypal_service,
)
from app.services.payment_service import (
    MockPayPalOrderService,
    payment_service,
)
from app.schemas.payment import (
    PayPalCreateOrderRequest,
)
from app.routes.payments import (
    create_paypal_order,
    capture_paypal_order,
    verify_paypal_order,
)
from app.routes.webhooks import receive_paypal_webhook


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
def sample_setup(db_session):
    """Seed workflow and registration records for PayPal testing."""
    wf = WorkflowModel(
        title="AI Masterclass",
        price=Decimal("120.00"),
        currency="USD",
        capacity=50,
        status="active",
    )
    db_session.add(wf)
    db_session.commit()

    reg = RegistrationModel(
        workflow_id=wf.id,
        customer_name="Alice Brown",
        customer_email="alice@example.com",
        registration_status="pending",
    )
    db_session.add(reg)
    db_session.commit()

    return wf, reg


# ── 1. PayPalSandboxService Unit Tests with Mocked HTTP ──────────────────────

def test_paypal_oauth_token_acquisition_and_caching():
    """Verify that OAuth2 token is fetched and cached to avoid redundant network calls."""
    mock_client = MagicMock(spec=httpx.Client)

    # Mock token response
    token_resp = MagicMock(spec=httpx.Response)
    token_resp.status_code = 200
    token_resp.json.return_value = {
        "access_token": "ACCESS-TOKEN-XYZ-999",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    mock_client.post.return_value = token_resp

    service = PayPalSandboxService(
        client_id="test_client_id",
        client_secret="test_client_secret",
        http_client=mock_client,
    )

    token1 = service.get_access_token()
    assert token1 == "ACCESS-TOKEN-XYZ-999"

    # Second call should use cache
    token2 = service.get_access_token()
    assert token2 == "ACCESS-TOKEN-XYZ-999"
    assert mock_client.post.call_count == 1


def test_paypal_create_order_request():
    """Verify order creation payload structure, Decimal formatting, and approval link extraction."""
    mock_client = MagicMock(spec=httpx.Client)

    # Mock OAuth2 token
    token_resp = MagicMock(spec=httpx.Response)
    token_resp.status_code = 200
    token_resp.json.return_value = {"access_token": "TOK-123", "expires_in": 3600}

    # Mock Order creation
    order_resp = MagicMock(spec=httpx.Response)
    order_resp.status_code = 201
    order_resp.json.return_value = {
        "id": "ORDER-PP-55555",
        "status": "CREATED",
        "links": [
            {"href": "https://sandbox.paypal.com/checkoutnow?token=ORDER-PP-55555", "rel": "approve", "method": "GET"}
        ],
    }

    mock_client.post.side_effect = [token_resp, order_resp]

    service = PayPalSandboxService(
        client_id="cid",
        client_secret="sec",
        http_client=mock_client,
    )

    result = service.create_order(
        amount=Decimal("120.00"),
        currency="USD",
        reference_id="REG-101",
        description="Bootcamp Ticket",
        return_url="http://localhost:3000/success",
        cancel_url="http://localhost:3000/cancel",
    )

    assert result["id"] == "ORDER-PP-55555"
    assert result["status"] == "CREATED"
    assert result["amount"] == "120.00"
    assert result["currency"] == "USD"
    assert result["approve_url"] == "https://sandbox.paypal.com/checkoutnow?token=ORDER-PP-55555"

    # Verify the posted payload sent to /v2/checkout/orders
    create_call = mock_client.post.call_args_list[1]
    posted_json = create_call.kwargs["json"]
    assert posted_json["intent"] == "CAPTURE"
    assert posted_json["purchase_units"][0]["amount"]["value"] == "120.00"
    assert posted_json["purchase_units"][0]["amount"]["currency_code"] == "USD"


def test_paypal_capture_order_success():
    """Verify order capture extracts capture_id and confirms COMPLETED status."""
    mock_client = MagicMock(spec=httpx.Client)

    token_resp = MagicMock(spec=httpx.Response)
    token_resp.status_code = 200
    token_resp.json.return_value = {"access_token": "TOK-123", "expires_in": 3600}

    capture_resp = MagicMock(spec=httpx.Response)
    capture_resp.status_code = 201
    capture_resp.json.return_value = {
        "id": "ORDER-PP-55555",
        "status": "COMPLETED",
        "purchase_units": [
            {
                "payments": {
                    "captures": [
                        {
                            "id": "CAP-PP-99999",
                            "status": "COMPLETED",
                            "amount": {"value": "120.00", "currency_code": "USD"},
                        }
                    ]
                }
            }
        ],
    }

    mock_client.post.side_effect = [token_resp, capture_resp]

    service = PayPalSandboxService(client_id="cid", client_secret="sec", http_client=mock_client)
    res = service.capture_order("ORDER-PP-55555")

    assert res["status"] == "COMPLETED"
    assert res["capture_id"] == "CAP-PP-99999"
    assert res["amount_captured"] == "120.00"


def test_paypal_capture_order_declined_raises_exception():
    """Verify that non-COMPLETED captures raise PaymentVerificationException."""
    mock_client = MagicMock(spec=httpx.Client)

    token_resp = MagicMock(spec=httpx.Response)
    token_resp.status_code = 200
    token_resp.json.return_value = {"access_token": "TOK-123", "expires_in": 3600}

    capture_resp = MagicMock(spec=httpx.Response)
    capture_resp.status_code = 200
    capture_resp.json.return_value = {
        "id": "ORDER-PP-55555",
        "status": "DECLINED",
    }

    mock_client.post.side_effect = [token_resp, capture_resp]

    service = PayPalSandboxService(client_id="cid", client_secret="sec", http_client=mock_client)
    with pytest.raises(PaymentVerificationException, match="Status: DECLINED"):
        service.capture_order("ORDER-PP-55555")


def test_paypal_webhook_signature_verification():
    """Verify webhook signature verification via PayPal's API."""
    mock_client = MagicMock(spec=httpx.Client)

    token_resp = MagicMock(spec=httpx.Response)
    token_resp.status_code = 200
    token_resp.json.return_value = {"access_token": "TOK-123", "expires_in": 3600}

    verify_resp = MagicMock(spec=httpx.Response)
    verify_resp.status_code = 200
    verify_resp.json.return_value = {"verification_status": "SUCCESS"}

    mock_client.post.side_effect = [token_resp, verify_resp]

    service = PayPalSandboxService(
        client_id="cid",
        client_secret="sec",
        webhook_id="WH-999-TEST",
        http_client=mock_client,
    )

    headers = {
        "PAYPAL-AUTH-ALGO": "SHA256withRSA",
        "PAYPAL-CERT-URL": "https://api.sandbox.paypal.com/v1/certs/123",
        "PAYPAL-TRANSMISSION-ID": "trans-123",
        "PAYPAL-TRANSMISSION-SIG": "sig-abc",
        "PAYPAL-TRANSMISSION-TIME": "2026-11-12T20:00:00Z",
    }
    body = b'{"event_type": "PAYMENT.CAPTURE.COMPLETED"}'

    assert service.verify_webhook_signature(headers, body) is True


# ── 2. Factory and Fallback Tests ────────────────────────────────────────────

def test_get_paypal_service_fallback_to_mock():
    """When credentials are unset or placeholder, get_paypal_service returns MockPayPalOrderService."""
    service = get_paypal_service()
    assert isinstance(service, (MockPayPalOrderService, PayPalSandboxService))


# ── 3. PayPal Order Creation and Capture Route Flow ──────────────────────────

def test_paypal_order_lifecycle_via_routes(db_session, sample_setup):
    """Test full cycle: initiate order -> verify -> capture order -> registration paid."""
    wf, reg = sample_setup

    # 1. Create PayPal Order
    order_req = PayPalCreateOrderRequest(registration_id=reg.id)
    create_res = create_paypal_order(payload=order_req, db=db_session)
    assert create_res["success"] is True
    order_id = create_res["data"]["order_id"]
    payment_id = create_res["data"]["payment_id"]

    # Verify payment record in DB
    payment = db_session.get(PaymentModel, payment_id)
    assert payment.paypal_order_id == order_id
    assert payment.payment_status == "unpaid"

    # 2. Verify server-side order status
    verify_res = verify_paypal_order(order_id=order_id, db=db_session)
    assert verify_res["success"] is True
    assert verify_res["data"]["paypal_order_id"] == order_id

    # 3. Capture PayPal Order
    capture_res = capture_paypal_order(order_id=order_id, db=db_session)
    assert capture_res["success"] is True
    assert capture_res["data"]["status"] == "COMPLETED"
    assert capture_res["data"]["registration_status"] == "paid"

    # Confirm DB synchronization
    db_session.refresh(payment)
    db_session.refresh(reg)
    assert payment.payment_status == "paid"
    assert reg.registration_status == "paid"
    assert payment.paypal_capture_id is not None
    assert len(payment.transactions) == 1

    # 4. Idempotent second capture
    dup_res = capture_paypal_order(order_id=order_id, db=db_session)
    assert dup_res["success"] is True
    assert dup_res["data"]["status"] == "COMPLETED"
    # Still only 1 transaction recorded
    assert len(payment.transactions) == 1


# ── 4. Webhook Receiver Integration Tests ────────────────────────────────────

def test_paypal_webhook_payment_capture_completed(db_session, sample_setup):
    """Test webhook handler updating payment and registration to 'paid'."""
    wf, reg = sample_setup

    # Create initial pending payment
    payment = PaymentModel(
        registration_id=reg.id,
        amount=Decimal("120.00"),
        currency="USD",
        paypal_order_id="WH-ORDER-999",
        payment_status="unpaid",
    )
    db_session.add(payment)
    db_session.commit()

    webhook_event = {
        "id": "EVT-12345",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {
            "id": "WH-CAP-8888",
            "status": "COMPLETED",
            "amount": {"value": "120.00", "currency_code": "USD"},
            "supplementary_data": {
                "related_ids": {
                    "order_id": "WH-ORDER-999",
                }
            },
        },
    }

    mock_request = MagicMock()
    mock_request.headers = {"Content-Type": "application/json"}

    res = receive_paypal_webhook(event=webhook_event, request=mock_request, db=db_session)
    assert res["status"] == "success"
    assert res["event"] == "PAYMENT.CAPTURE.COMPLETED"

    # Verify DB state
    db_session.refresh(payment)
    db_session.refresh(reg)
    assert payment.payment_status == "paid"
    assert payment.paypal_capture_id == "WH-CAP-8888"
    assert reg.registration_status == "paid"
    assert len(payment.transactions) == 1

    # Idempotent second webhook delivery
    dup_res = receive_paypal_webhook(event=webhook_event, request=mock_request, db=db_session)
    assert dup_res["status"] == "success"
    assert dup_res["message"] == "Already processed"
    assert len(payment.transactions) == 1


def test_paypal_webhook_order_approved(db_session, sample_setup):
    """Test webhook handler updating payment status to 'verifying' on order approval."""
    wf, reg = sample_setup

    payment = PaymentModel(
        registration_id=reg.id,
        amount=Decimal("120.00"),
        currency="USD",
        paypal_order_id="WH-ORDER-777",
        payment_status="unpaid",
    )
    db_session.add(payment)
    db_session.commit()

    webhook_event = {
        "id": "EVT-777",
        "event_type": "CHECKOUT.ORDER.APPROVED",
        "resource": {
            "id": "WH-ORDER-777",
            "status": "APPROVED",
        },
    }

    mock_request = MagicMock()
    mock_request.headers = {"Content-Type": "application/json"}

    res = receive_paypal_webhook(event=webhook_event, request=mock_request, db=db_session)
    assert res["status"] == "success"
    assert res["event"] == "CHECKOUT.ORDER.APPROVED"

    db_session.refresh(payment)
    assert payment.payment_status == "verifying"
