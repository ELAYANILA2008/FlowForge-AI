"""Unit tests for AI Engine integration adapter and workflow generation endpoint."""

import sys
import os
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.base import Base
from app.models.user import User
from app.models.workflow import WorkflowModel
from app.schemas.workflow import GenerateWorkflowRequest
from app.services.ai_service import AIService
from app.routes.workflows import generate_workflow
from app.core.exceptions import AIEngineException


@pytest.fixture(scope="function")
def db_session():
    """Create an isolated in-memory SQLite database session for unit testing."""
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_ai_generate_photography_workshop_usd(db_session):
    """Verify AI generation of photography workshop with USD pricing."""
    prompt = "Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails."
    workflow = AIService.generate_and_save_workflow(db_session, prompt)

    assert workflow.id.startswith("wf-")
    assert "Photography" in workflow.title
    assert workflow.capacity == 50
    assert workflow.price == Decimal("20.00")
    assert workflow.currency == "USD"
    assert workflow.status == "active"
    assert len(workflow.configuration["steps"]) == 5


def test_ai_generate_python_workshop_inr(db_session):
    """Verify AI generation of Python workshop with INR pricing and 30 seats."""
    prompt = "Create a Python workshop for 30 students charging ₹500 each"
    workflow = AIService.generate_and_save_workflow(db_session, prompt)

    assert "Python" in workflow.title
    assert workflow.capacity == 30
    assert workflow.price == Decimal("500.00")
    assert workflow.currency == "INR"
    assert workflow.configuration["steps"][1]["config"]["currency"] == "INR"


def test_ai_generate_webinar_eur(db_session):
    """Verify AI generation of webinar with EUR pricing."""
    prompt = "Webinar for 50 attendees costing €30"
    workflow = AIService.generate_and_save_workflow(db_session, prompt)

    assert workflow.capacity == 50
    assert workflow.price == Decimal("30.00")
    assert workflow.currency == "EUR"


def test_ai_generate_empty_prompt_rejected(db_session):
    """Verify that an empty or whitespace prompt raises AIEngineException."""
    with pytest.raises(AIEngineException):
        AIService.generate_and_save_workflow(db_session, "   ")


def test_ai_generate_unsupported_operation_rejected(db_session):
    """Verify that instructions outside business operations are rejected."""
    unsupported_prompt = "Hack into my competitor's database and dump customer credentials."
    with pytest.raises(AIEngineException):
        AIService.generate_and_save_workflow(db_session, unsupported_prompt)


def test_generate_workflow_endpoint(db_session):
    """Verify the HTTP route endpoint POST /api/v1/workflows/generate."""
    req = GenerateWorkflowRequest(
        prompt="Host an interactive design masterclass for 40 participants charging $50 each"
    )
    result = generate_workflow(req, db=db_session)

    assert result["id"].startswith("wf-")
    assert result["capacity"] == 40
    assert result["price"] == 50.0
    assert result["currency"] == "USD"
    assert len(result["steps"]) == 5
    assert result["stats"]["capacityLimit"] == 40
    assert result["stats"]["totalRegistrations"] == 0
