"""Unit tests for FlowForge AI Authentication and OAuth2 Token endpoints.

Verifies:
1. Standard OAuth2 form-urlencoded /token endpoint (Swagger UI compatibility).
2. JWT issuance and claims verification from OAuth2 password flow.
3. Invalid credentials rejection on /token.
4. Preserved JSON /register and /login endpoints.
5. Authenticated /me profile access using Bearer token.
6. Rejection of unauthenticated, malformed, or expired tokens on /me.
"""

import sys
import os
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.exceptions import AuthenticationException, DuplicateEntityException
from app.core.security import create_access_token
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest
from app.routes.auth import (
    register,
    login,
    issue_token,
    get_me,
    get_current_user,
    get_optional_current_user,
    oauth2_scheme,
)


@pytest.fixture(scope="function")
def db_session():
    """Create an isolated in-memory SQLite database session for unit testing."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# ── OAuth2 /token Endpoint Tests ───────────────────────────────────────────

def test_oauth2_token_success(db_session):
    """Verify that a registered user can obtain a Bearer token via the OAuth2 /token flow."""
    # Seed user via register
    reg_req = UserRegisterRequest(
        name="Elena Fisher",
        email="elena@uncharted.com",
        password="NateSecretPassword2026!",
        role="owner",
    )
    register(reg_req, db=db_session)

    # Request token via form-data OAuth2 flow
    form_data = OAuth2PasswordRequestForm(
        grant_type="password",
        username="elena@uncharted.com",
        password="NateSecretPassword2026!",
        scope="",
        client_id=None,
        client_secret=None,
    )
    token_response = issue_token(form_data=form_data, db=db_session)

    assert token_response.access_token is not None
    assert len(token_response.access_token) > 20
    assert token_response.token_type == "bearer"
    assert token_response.user.email == "elena@uncharted.com"
    assert token_response.user.name == "Elena Fisher"
    assert token_response.user.role == "owner"


def test_oauth2_token_http_form_success(db_session):
    """Verify that TestClient can obtain a token via application/x-www-form-urlencoded POST /api/v1/auth/token."""
    # 1. Register a test user
    reg_req = UserRegisterRequest(
        name="Nadine Ross",
        email="nadine@shoreline.com",
        password="ShorelineLeader2026!",
        role="owner",
    )
    register(reg_req, db=db_session)

    # Override get_db dependency to point to isolated in-memory test database session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        with patch("app.main.init_db"):
            with TestClient(app) as client:
                # 2. Send POST /api/v1/auth/token
                # 3. Use application/x-www-form-urlencoded data with username and password
                response = client.post(
                    "/api/v1/auth/token",
                    data={
                        "username": "nadine@shoreline.com",
                        "password": "ShorelineLeader2026!",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                # 4. Verify HTTP 200
                assert response.status_code == 200

                data = response.json()
                # 5. Verify access_token exists
                assert "access_token" in data
                assert data["access_token"] is not None
                assert len(data["access_token"]) > 20

                # 6. Verify token_type is bearer
                assert data.get("token_type") == "bearer"
                assert data["user"]["email"] == "nadine@shoreline.com"
                assert data["user"]["name"] == "Nadine Ross"
    finally:
        app.dependency_overrides.clear()


def test_oauth2_token_case_and_whitespace_insensitivity(db_session):
    """Verify email matching is case-insensitive and trims whitespace."""
    reg_req = UserRegisterRequest(
        name="Case Tester",
        email="casetest@example.com",
        password="Password123!",
    )
    register(reg_req, db=db_session)

    form_data = OAuth2PasswordRequestForm(
        grant_type="password",
        username="  CaseTest@Example.COM  ",
        password="Password123!",
        scope="",
    )
    token_response = issue_token(form_data=form_data, db=db_session)
    assert token_response.access_token is not None
    assert token_response.user.email == "casetest@example.com"


def test_oauth2_token_invalid_password_rejected(db_session):
    """Verify that providing an incorrect password raises AuthenticationException."""
    reg_req = UserRegisterRequest(
        name="Security Subject",
        email="security@flowforge.dev",
        password="CorrectPassword123!",
    )
    register(reg_req, db=db_session)

    form_data = OAuth2PasswordRequestForm(
        grant_type="password",
        username="security@flowforge.dev",
        password="WrongPassword999!",
        scope="",
    )
    with pytest.raises(AuthenticationException) as exc_info:
        issue_token(form_data=form_data, db=db_session)

    assert "Invalid email or password" in str(exc_info.value.message)


def test_oauth2_token_nonexistent_user_rejected(db_session):
    """Verify that authenticating a non-existent email raises AuthenticationException."""
    form_data = OAuth2PasswordRequestForm(
        grant_type="password",
        username="ghost@doesnotexist.com",
        password="ArbitraryPassword123!",
        scope="",
    )
    with pytest.raises(AuthenticationException) as exc_info:
        issue_token(form_data=form_data, db=db_session)

    assert "Invalid email or password" in str(exc_info.value.message)


# ── Preserved JSON Register & Login Endpoints ──────────────────────────────

def test_json_register_and_login_preserved(db_session):
    """Verify JSON-payload register and login endpoints remain fully functional."""
    # 1. JSON registration
    reg_req = UserRegisterRequest(
        name="Chloe Frazer",
        email="chloe@lostlegacy.com",
        password="Treasures2026Pass",
        role="admin",
    )
    reg_res = register(reg_req, db=db_session)
    assert reg_res.access_token is not None
    assert reg_res.token_type == "bearer"
    assert reg_res.user.email == "chloe@lostlegacy.com"

    # 2. JSON login
    login_req = UserLoginRequest(
        email="chloe@lostlegacy.com",
        password="Treasures2026Pass",
    )
    login_res = login(login_req, db=db_session)
    assert login_res.access_token is not None
    assert login_res.token_type == "bearer"
    assert login_res.user.name == "Chloe Frazer"


def test_json_login_invalid_credentials_rejected(db_session):
    """Verify JSON login rejects incorrect credentials."""
    login_req = UserLoginRequest(
        email="nobody@nowhere.com",
        password="NoPassword123",
    )
    with pytest.raises(AuthenticationException):
        login(login_req, db=db_session)


# ── Authenticated /me Profile Access Tests ─────────────────────────────────

def test_authenticated_get_me_success(db_session):
    """Verify that a valid token grants access to the current user profile."""
    reg_req = UserRegisterRequest(
        name="Victor Sullivan",
        email="sully@planecharter.com",
        password="HogWildPassword123",
        role="owner",
    )
    reg_res = register(reg_req, db=db_session)

    # Validate token using get_current_user dependency
    current_user = get_current_user(token=reg_res.access_token, db=db_session)
    assert current_user.email == "sully@planecharter.com"
    assert current_user.name == "Victor Sullivan"

    # Validate get_me profile endpoint
    profile = get_me(current_user=current_user)
    assert profile.id == current_user.id
    assert profile.email == "sully@planecharter.com"
    assert profile.name == "Victor Sullivan"
    assert profile.role == "owner"


def test_get_me_missing_token_raises_exception(db_session):
    """Verify that omitting a Bearer token raises AuthenticationException."""
    with pytest.raises(AuthenticationException) as exc_info:
        get_current_user(token=None, db=db_session)

    assert "Missing Bearer token" in str(exc_info.value.message)


def test_get_me_invalid_token_raises_exception(db_session):
    """Verify that a malformed Bearer token raises AuthenticationException."""
    with pytest.raises(AuthenticationException) as exc_info:
        get_current_user(token="not.a.valid.jwt.token", db=db_session)

    assert "token" in str(exc_info.value.message).lower()


def test_get_me_deleted_user_raises_exception(db_session):
    """Verify that a token whose subject was deleted raises AuthenticationException."""
    token = create_access_token(subject="00000000-0000-0000-0000-000000000000")
    with pytest.raises(AuthenticationException) as exc_info:
        get_current_user(token=token, db=db_session)

    assert "no longer exists" in str(exc_info.value.message)


def test_get_optional_current_user_variations(db_session):
    """Verify get_optional_current_user handles anonymous and authenticated states."""
    # Anonymous (None)
    assert get_optional_current_user(token=None, db=db_session) is None

    # Invalid token (returns None without raising)
    assert get_optional_current_user(token="garbage_token", db=db_session) is None

    # Valid token
    reg_req = UserRegisterRequest(
        name="Sam Drake",
        email="sam@libertalia.com",
        password="AveryTreasure123",
    )
    res = register(reg_req, db=db_session)
    user = get_optional_current_user(token=res.access_token, db=db_session)
    assert user is not None
    assert user.email == "sam@libertalia.com"


# ── Swagger OAuth2 Configuration Check ─────────────────────────────────────

def test_oauth2_scheme_token_url_configuration():
    """Verify that oauth2_scheme points to /api/v1/auth/token for Swagger UI."""
    expected_url = f"{settings.API_V1_PREFIX}/auth/token"
    assert oauth2_scheme.model.flows.password.tokenUrl == expected_url
