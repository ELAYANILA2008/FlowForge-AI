"""Authentication routes, JWT token issuance, and current user profile dependencies."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.core.exceptions import AuthenticationException, DuplicateEntityException
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse

logger = logging.getLogger("flowforge.routes.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency to extract and validate the authenticated user from the Bearer token."""
    if not token:
        raise AuthenticationException("Authentication required: Missing Bearer token")

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Invalid token payload: missing subject identifier")

    user = db.scalar(select(User).where(User.id == str(user_id)))
    if not user:
        raise AuthenticationException("The user associated with this token no longer exists")

    return user


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Dependency that returns the current User if valid Bearer token provided, or None if anonymous."""
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        return db.scalar(select(User).where(User.id == str(user_id)))
    except Exception:
        return None


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User Account",
    description="Registers a new user account, hashes credentials using PBKDF2, and issues an initial JWT token.",
)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user account."""
    existing_user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing_user:
        raise DuplicateEntityException("User", "email", payload.email)

    user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        hashed_password=get_password_hash(payload.password),
        role=payload.role or "owner",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        subject=user.id,
        claims={"email": user.email, "role": user.role, "name": user.name},
    )

    logger.info("Registered new user [%s] with email '%s'", user.id, user.email)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticates email and password and returns a signed JWT access token.",
)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate with JSON payload."""
    user = db.scalar(select(User).where(User.email == payload.email.lower().strip()))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationException("Invalid email or password.")

    token = create_access_token(
        subject=user.id,
        claims={"email": user.email, "role": user.role, "name": user.name},
    )

    logger.info("User [%s] '%s' logged in successfully", user.id, user.email)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
    description="Returns profile information for the authenticated user based on the Bearer token.",
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """Return authenticated user profile."""
    return UserResponse.model_validate(current_user)

