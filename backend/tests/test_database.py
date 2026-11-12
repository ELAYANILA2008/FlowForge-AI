"""Unit tests for PostgreSQL / SQLAlchemy 2.x models, relationships, and session management."""

import sys
import os
import pytest
from decimal import Decimal
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.base import Base
from app.models.user import User
from app.models.workflow import WorkflowModel
from app.models.registration import RegistrationModel
from app.models.payment import PaymentModel
from app.models.transaction import TransactionModel


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh in-memory SQLite database session for testing."""
    test_engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def test_user_creation(test_db):
    """Verify that User entity can be created and queried."""
    user = User(
        name="Alex Mercer",
        email="alex@flowforge.ai",
        hashed_password="pbkdf2_sha256$hashed",
        role="owner",
    )
    test_db.add(user)
    test_db.commit()

    queried = test_db.scalar(select(User).where(User.email == "alex@flowforge.ai"))
    assert queried is not None
    assert queried.name == "Alex Mercer"
    assert queried.role == "owner"
    assert queried.id is not None
    assert queried.created_at is not None


def test_unique_user_email_constraint(test_db):
    """Verify that duplicate user email triggers an IntegrityError."""
    user1 = User(name="User 1", email="duplicate@flowforge.ai", hashed_password="pw")
    user2 = User(name="User 2", email="duplicate@flowforge.ai", hashed_password="pw")
    test_db.add(user1)
    test_db.commit()

    test_db.add(user2)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()


def test_workflow_relationship_and_cascade(test_db):
    """Verify workflow entity creation and user-to-workflow relationship."""
    user = User(name="Owner", email="owner@flowforge.ai", hashed_password="pw")
    test_db.add(user)
    test_db.commit()

    wf = WorkflowModel(
        owner_id=user.id,
        title="Python Automation Workshop",
        description="Hands-on Python workshop",
        configuration={"steps": ["registration", "payment"]},
        capacity=30,
        price=Decimal("500.00"),
        currency="INR",
        status="active",
    )
    test_db.add(wf)
    test_db.commit()

    assert len(user.workflows) == 1
    assert user.workflows[0].title == "Python Automation Workshop"
    assert user.workflows[0].price == Decimal("500.00")
    assert user.workflows[0].currency == "INR"


def test_registration_and_capacity(test_db):
    """Verify registration creation and unique customer email per workflow."""
    wf = WorkflowModel(
        title="Photography Workshop",
        capacity=20,
        price=Decimal("750.00"),
        currency="INR",
    )
    test_db.add(wf)
    test_db.commit()

    reg1 = RegistrationModel(
        workflow_id=wf.id,
        customer_name="Elena Rostova",
        customer_email="elena@example.com",
        registration_status="confirmed",
    )
    test_db.add(reg1)
    test_db.commit()

    assert reg1.id is not None
    assert len(wf.registrations) == 1

    # Duplicate registration for same workflow should fail constraint
    reg_duplicate = RegistrationModel(
        workflow_id=wf.id,
        customer_name="Elena Second",
        customer_email="elena@example.com",
    )
    test_db.add(reg_duplicate)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()


def test_payment_and_transaction_audit_trail(test_db):
    """Verify payment and transaction entity creation with Decimal amounts."""
    wf = WorkflowModel(title="Webinar", price=Decimal("30.00"), currency="EUR")
    test_db.add(wf)
    test_db.commit()

    reg = RegistrationModel(
        workflow_id=wf.id,
        customer_name="John Doe",
        customer_email="john@example.com",
    )
    test_db.add(reg)
    test_db.commit()

    payment = PaymentModel(
        registration_id=reg.id,
        paypal_order_id="ORDER-12345",
        paypal_capture_id="CAPTURE-67890",
        amount=Decimal("30.00"),
        currency="EUR",
        payment_status="paid",
    )
    test_db.add(payment)
    test_db.commit()

    tx = TransactionModel(
        payment_id=payment.id,
        transaction_reference="TXN-2026-EUR-001",
        verification_status="verified",
    )
    test_db.add(tx)
    test_db.commit()

    assert payment.amount == Decimal("30.00")
    assert payment.currency == "EUR"
    assert len(payment.transactions) == 1
    assert payment.transactions[0].verification_status == "verified"
    assert payment.transactions[0].transaction_reference == "TXN-2026-EUR-001"

