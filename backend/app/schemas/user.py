"""Pydantic schemas for user authentication, registration, and profile responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Payload for user account creation."""
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    email: EmailStr = Field(..., description="Unique email address for login")
    password: str = Field(..., min_length=8, max_length=128, description="Plaintext password")
    role: Optional[str] = Field(default="owner", description="User role (e.g. owner, admin, user)")


class UserLoginRequest(BaseModel):
    """Payload for user authentication."""
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Sanitized public user profile response (never exposes hashed password)."""
    id: str
    name: str
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT authorization response returned upon successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

