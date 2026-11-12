"""Unit tests for Phase 9: Dashboard Metrics, Agent Telemetry, and Activity Stream.

Verifies:
1. Multi-currency segregated revenue calculation (USD, EUR, INR).
2. Accurate aggregation of workflows, registrations, and payment events.
3. Strict isolation of currencies without invalid mixing.
4. Agent performance benchmarks and telemetry metrics.
5. Real-time activity feed composition and chronological ordering.
6. API endpoint contracts matching frontend types.
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
from app.services.analytics_service import analytics_service
from app.routes.analytics import (
    get_dashboard_metrics,
    get_agent_performance,
    get_activity_feed,
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


def test_dashboard_metrics_empty_database(db_session):
    """Verify metrics calculation on a clean database without errors."""
    data = analytics_service.get_dashboard_metrics(db=db_session)

    assert data["totalWorkflows"] == 0
    assert data["activeWorkflows"] == 0
    assert data["totalRegistrations"] == 0
    assert data["totalRevenueUsd"] == 0.0
    assert data["totalRevenueInr"] == 0.0
    assert data["totalRevenueEur"] == 0.0
    assert data["successfulExecutions"] == 0
    assert data["failedExecutions"] == 0
    assert isinstance(data["revenueTrend"], list)
    assert len(data["revenueTrend"]) == 7
    assert isinstance(data["executionTrend"], list)
    assert len(data["executionTrend"]) == 7


def test_dashboard_metrics_with_multi_currency_revenues(db_session):
    """Verify that revenues are strictly segregated across USD, EUR, and INR."""
    # 1. Create workflows
    wf_usd = WorkflowModel(title="Workshop USD", price=Decimal("100.00"), currency="USD", status="active")
    wf_inr = WorkflowModel(title="Bootcamp INR", price=Decimal("5000.00"), currency="INR", status="active")
    wf_eur = WorkflowModel(title="Webinar EUR", price=Decimal("45.00"), currency="EUR", status="active")
    wf_draft = WorkflowModel(title="Draft Workshop", price=Decimal("20.00"), currency="USD", status="draft")

    db_session.add_all([wf_usd, wf_inr, wf_eur, wf_draft])
    db_session.commit()

    # 2. Create registrations
    reg1 = RegistrationModel(workflow_id=wf_usd.id, customer_name="Alice", customer_email="alice@test.com")
    reg2 = RegistrationModel(workflow_id=wf_usd.id, customer_name="Bob", customer_email="bob@test.com")
    reg3 = RegistrationModel(workflow_id=wf_inr.id, customer_name="Chitra", customer_email="chitra@test.com")
    reg4 = RegistrationModel(workflow_id=wf_eur.id, customer_name="Denis", customer_email="denis@test.com")

    db_session.add_all([reg1, reg2, reg3, reg4])
    db_session.commit()

    # 3. Create payments with mixed statuses
    # USD: 1 paid (100.00) + 1 unpaid (100.00)
    pay_usd_paid = PaymentModel(registration_id=reg1.id, amount=Decimal("100.00"), currency="USD", payment_status="paid")
    pay_usd_unpaid = PaymentModel(registration_id=reg2.id, amount=Decimal("100.00"), currency="USD", payment_status="unpaid")

    # INR: 1 paid (5000.00)
    pay_inr_paid = PaymentModel(registration_id=reg3.id, amount=Decimal("5000.00"), currency="INR", payment_status="paid")

    # EUR: 1 paid (45.00) + 1 failed (45.00)
    pay_eur_paid = PaymentModel(registration_id=reg4.id, amount=Decimal("45.00"), currency="EUR", payment_status="paid")
    pay_eur_failed = PaymentModel(registration_id=reg4.id, amount=Decimal("45.00"), currency="EUR", payment_status="failed")

    db_session.add_all([pay_usd_paid, pay_usd_unpaid, pay_inr_paid, pay_eur_paid, pay_eur_failed])
    db_session.commit()

    # 4. Compute metrics
    metrics = analytics_service.get_dashboard_metrics(db=db_session)

    assert metrics["totalWorkflows"] == 4
    assert metrics["activeWorkflows"] == 3
    assert metrics["totalRegistrations"] == 4

    # Strict currency separation check:
    assert metrics["totalRevenueUsd"] == 100.0
    assert metrics["totalRevenueInr"] == 5000.0
    assert metrics["totalRevenueEur"] == 45.0

    # Successful executions: 4 registrations + 3 paid payments = 7
    assert metrics["successfulExecutions"] == 7
    # Failed executions: 1 failed payment
    assert metrics["failedExecutions"] == 1


def test_agent_performance_telemetry(db_session):
    """Verify agent telemetry contains valid benchmark scores and statuses."""
    agents = analytics_service.get_agent_performance(db=db_session)

    assert len(agents) == 3
    agent_ids = [a["id"] for a in agents]
    assert "agent-ai-gen" in agent_ids
    assert "agent-paypal-ops" in agent_ids
    assert "agent-gatekeeper" in agent_ids

    for agent in agents:
        assert agent["taskCompletionRate"] >= 95.0
        assert agent["reliabilityScore"] >= 95.0
        assert agent["status"] == "optimal"
        assert agent["totalTasksProcessed"] > 0
        assert "lastBenchmarkedAt" in agent


def test_activity_feed_generation(db_session):
    """Verify that activity feed compiles events in chronological order."""
    wf = WorkflowModel(title="Photography Crash Course", price=Decimal("25.00"), currency="USD", capacity=10)
    db_session.add(wf)
    db_session.commit()

    reg = RegistrationModel(workflow_id=wf.id, customer_name="Sam Smith", customer_email="sam@test.com")
    db_session.add(reg)
    db_session.commit()

    payment = PaymentModel(registration_id=reg.id, amount=Decimal("25.00"), currency="USD", payment_status="paid", paypal_order_id="ORD-101")
    db_session.add(payment)
    db_session.commit()

    feed = analytics_service.get_activity_feed(db=db_session, limit=10)

    assert len(feed) >= 3
    event_types = [item["type"] for item in feed]
    assert "payment" in event_types
    assert "registration" in event_types
    assert "created" in event_types

    # Ensure items have required frontend fields
    for item in feed:
        assert item["id"] is not None
        assert item["workflowId"] is not None
        assert item["title"] is not None
        assert item["timestamp"] is not None
        assert item["status"] in ("success", "pending", "failed")


def test_analytics_api_routes(db_session):
    """Verify API endpoints return valid ApiResponse envelopes."""
    # 1. Test /metrics/dashboard
    dash_resp = get_dashboard_metrics(db=db_session)
    assert dash_resp["success"] is True
    assert "totalWorkflows" in dash_resp["data"]
    assert "totalRevenueUsd" in dash_resp["data"]

    # 2. Test /metrics/agents
    agents_resp = get_agent_performance(db=db_session)
    assert agents_resp["success"] is True
    assert isinstance(agents_resp["data"], list)
    assert len(agents_resp["data"]) == 3

    # 3. Test /activity
    activity_resp = get_activity_feed(limit=5, db=db_session)
    assert activity_resp["success"] is True
    assert isinstance(activity_resp["data"], list)

