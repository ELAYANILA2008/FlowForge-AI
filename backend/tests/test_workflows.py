"""Unit tests for user authentication and workflow management APIs."""

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
from app.schemas.user import UserRegisterRequest, UserLoginRequest
from app.schemas.workflow import WorkflowCreateRequest, WorkflowUpdateRequest, WorkflowStatusUpdateRequest
from app.routes.auth import register, login, get_me, get_current_user
from app.routes.workflows import (
    list_workflows,
    create_workflow,
    get_workflow,
    update_workflow,
    delete_workflow,
    set_workflow_status,
)
from app.core.exceptions import (
    AuthenticationException,
    DuplicateEntityException,
    EntityNotFoundException,
    AuthorizationException,
)


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


# ── Authentication Tests ───────────────────────────────────────────────────

def test_user_registration_success(db_session):
    """Verify that a new user can register and receive a valid JWT token."""
    req = UserRegisterRequest(
        name="Sarah Connor",
        email="sarah@skynet.com",
        password="CyberdyneSecret123",
        role="owner",
    )
    result = register(req, db=db_session)
    assert result.access_token is not None
    assert result.token_type == "bearer"
    assert result.user.email == "sarah@skynet.com"
    assert result.user.name == "Sarah Connor"
    assert result.user.role == "owner"


def test_user_duplicate_registration_rejected(db_session):
    """Verify that registering with an existing email raises DuplicateEntityException."""
    req = UserRegisterRequest(
        name="Sarah Duplicate",
        email="duplicate@example.com",
        password="Password12345",
    )
    register(req, db=db_session)

    with pytest.raises(DuplicateEntityException):
        register(req, db=db_session)


def test_user_login_success(db_session):
    """Verify that an existing user can log in with correct credentials."""
    reg_req = UserRegisterRequest(
        name="John Doe",
        email="john@flowforge.ai",
        password="CorrectPassword123",
    )
    register(reg_req, db=db_session)

    login_req = UserLoginRequest(email="john@flowforge.ai", password="CorrectPassword123")
    result = login(login_req, db=db_session)
    assert result.access_token is not None
    assert result.user.email == "john@flowforge.ai"


def test_user_login_invalid_password(db_session):
    """Verify that logging in with an incorrect password raises AuthenticationException."""
    reg_req = UserRegisterRequest(
        name="Jane Doe",
        email="jane@flowforge.ai",
        password="ValidPassword123",
    )
    register(reg_req, db=db_session)

    login_req = UserLoginRequest(email="jane@flowforge.ai", password="WrongPassword999")
    with pytest.raises(AuthenticationException):
        login(login_req, db=db_session)


def test_get_current_user_profile(db_session):
    """Verify that a valid token resolves to the authenticated User entity."""
    reg_req = UserRegisterRequest(
        name="Alice Walker",
        email="alice@flowforge.ai",
        password="SecureAlicePassword123",
    )
    res = register(reg_req, db=db_session)

    user = get_current_user(token=res.access_token, db=db_session)
    assert user.email == "alice@flowforge.ai"
    assert user.name == "Alice Walker"

    # Profile endpoint output
    profile = get_me(current_user=user)
    assert profile.email == "alice@flowforge.ai"


# ── Workflow Management Tests ──────────────────────────────────────────────

def test_workflow_creation_and_frontend_contract(db_session):
    """Verify that creating a workflow produces the exact frontend JSON schema."""
    req = WorkflowCreateRequest(
        title="Python AI Automation Workshop",
        description="Learn to orchestrate AI with FlowForge",
        prompt="Create a Python workshop for 30 students charging ₹500 each",
        capacity=30,
        price=Decimal("500.00"),
        currency="INR",
        tags=["Python", "AI", "PayPal"],
    )
    result = create_workflow(req, db=db_session)

    assert result["id"].startswith("wf-")
    assert result["title"] == "Python AI Automation Workshop"
    assert result["capacity"] == 30
    assert result["price"] == 500.0
    assert result["currency"] == "INR"
    assert result["status"] == "active"
    assert len(result["steps"]) == 5
    assert result["stats"]["capacityLimit"] == 30
    assert result["stats"]["totalRegistrations"] == 0
    assert "createdAt" in result


def test_workflow_list_and_filter(db_session):
    """Verify that list_workflows retrieves multiple entries and filters by status."""
    req1 = WorkflowCreateRequest(title="Active Workshop", status="active")
    req2 = WorkflowCreateRequest(title="Draft Workshop", status="draft")
    create_workflow(req1, db=db_session)
    create_workflow(req2, db=db_session)

    all_wfs = list_workflows(db=db_session)
    assert len(all_wfs) == 2

    active_only = list_workflows(status="active", db=db_session)
    assert len(active_only) == 1
    assert active_only[0]["title"] == "Active Workshop"


def test_workflow_retrieve_by_id(db_session):
    """Verify retrieving a single workflow by ID."""
    req = WorkflowCreateRequest(title="Unique Workshop", capacity=25, price=Decimal("20.00"))
    created = create_workflow(req, db=db_session)

    retrieved = get_workflow(workflow_id=created["id"], db=db_session)
    assert retrieved["id"] == created["id"]
    assert retrieved["title"] == "Unique Workshop"
    assert retrieved["capacity"] == 25


def test_workflow_not_found(db_session):
    """Verify that querying a nonexistent workflow raises EntityNotFoundException (404)."""
    with pytest.raises(EntityNotFoundException):
        get_workflow(workflow_id="wf-nonexistent-999", db=db_session)


def test_workflow_update(db_session):
    """Verify updating workflow parameters."""
    req = WorkflowCreateRequest(title="Original Title", capacity=50)
    created = create_workflow(req, db=db_session)

    update_req = WorkflowUpdateRequest(
        title="Updated Title",
        capacity=40,
        price=Decimal("35.00"),
        currency="EUR",
    )
    updated = update_workflow(workflow_id=created["id"], payload=update_req, db=db_session)

    assert updated["title"] == "Updated Title"
    assert updated["capacity"] == 40
    assert updated["price"] == 35.0
    assert updated["currency"] == "EUR"


def test_workflow_status_transition(db_session):
    """Verify updating workflow status via PATCH endpoint."""
    created = create_workflow(WorkflowCreateRequest(title="Test Status Flow"), db=db_session)
    assert created["status"] == "active"

    status_req = WorkflowStatusUpdateRequest(status="paused")
    updated = set_workflow_status(workflow_id=created["id"], payload=status_req, db=db_session)
    assert updated["status"] == "paused"


def test_workflow_deletion(db_session):
    """Verify workflow deletion removes the record from database."""
    created = create_workflow(WorkflowCreateRequest(title="To Be Deleted"), db=db_session)
    wf_id = created["id"]

    del_res = delete_workflow(workflow_id=wf_id, db=db_session)
    assert del_res["success"] is True

    with pytest.raises(EntityNotFoundException):
        get_workflow(workflow_id=wf_id, db=db_session)

