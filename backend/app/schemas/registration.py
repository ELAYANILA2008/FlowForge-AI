"""Registration Pydantic schemas.

Matches the frontend RegistrationFormData and RegistrationSubmission types
defined in frontend/src/types/registration.ts exactly.
"""

from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, field_validator


class RegistrationCreateRequest(BaseModel):
    """Customer registration form submission — mirrors RegistrationFormData."""

    studentName: str
    studentEmail: EmailStr
    experienceLevel: Literal["beginner", "intermediate", "advanced"]
    specialRequests: Optional[str] = None

    @field_validator("studentName")
    @classmethod
    def validate_student_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("studentName must not be blank")
        if len(v) > 200:
            raise ValueError("studentName must be 200 characters or fewer")
        return v

    @field_validator("specialRequests")
    @classmethod
    def validate_special_requests(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError("specialRequests must be 1000 characters or fewer")
            return v or None
        return None


class RegistrationResponse(BaseModel):
    """Registration confirmation response — mirrors RegistrationSubmission."""

    id: str
    workflowId: str
    studentName: str
    studentEmail: str
    feeAmount: float
    currency: str
    paymentStatus: str           # "unpaid" | "verifying" | "paid" | "failed"
    paypalTransactionId: Optional[str] = None
    emailConfirmed: bool
    registeredAt: str            # ISO-8601 UTC string

    model_config = {"from_attributes": True}

