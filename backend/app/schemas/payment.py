"""Payment and Transaction Pydantic Schemas.

Enforces financial integrity:
- Strict currency validation (USD, EUR, INR)
- Positive monetary validation using Decimal
- Secure transaction audit records without raw financial secrets
- Typed payloads for PayPal Orders API v2 create & capture flows
"""

from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

from app.utils.currency import normalize_currency, to_decimal_amount


PaymentStatusType = Literal["unpaid", "pending", "verifying", "paid", "failed", "refunded"]


class TransactionCreateRequest(BaseModel):
    """Payload to record an audit transaction for a payment."""
    verification_status: str = Field(default="verified", description="Status e.g. verified, pending, rejected")
    transaction_reference: Optional[str] = Field(default=None, description="Custom reference if already assigned")

    @field_validator("verification_status")
    @classmethod
    def validate_verification_status(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not cleaned:
            raise ValueError("verification_status cannot be empty")
        return cleaned


class TransactionResponse(BaseModel):
    """Sanitized financial transaction audit representation."""
    id: str
    payment_id: str
    transaction_reference: str
    verification_status: str
    created_at: str

    model_config = {"from_attributes": True}


class PaymentCreateRequest(BaseModel):
    """Payload to create or initiate a payment record for a registration."""
    registration_id: str = Field(..., description="ID of the registration being paid for")
    amount: Optional[Decimal] = Field(default=None, description="Payment amount (defaults to workflow price)")
    currency: Optional[str] = Field(default=None, description="Currency code (USD, EUR, INR)")
    paypal_order_id: Optional[str] = Field(default=None, description="External PayPal order ID if already initiated")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            dec = to_decimal_amount(v)
            if dec <= Decimal("0.00"):
                raise ValueError("Payment amount must be greater than zero.")
            return dec
        return None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return normalize_currency(v)
        return None


class PaymentStatusUpdateRequest(BaseModel):
    """Payload for updating payment lifecycle status."""
    payment_status: PaymentStatusType
    paypal_order_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment record response matching frontend & audit specifications."""
    id: str
    registration_id: str
    paypal_order_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None
    amount: float
    currency: str
    payment_status: str
    created_at: str
    transactions: List[TransactionResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ── PayPal Specific Request & Response Schemas ────────────────────────────────

class PayPalCreateOrderRequest(BaseModel):
    """Payload to initiate an official PayPal Orders v2 checkout order."""
    registration_id: str = Field(..., description="ID of registration to pay for")
    return_url: Optional[str] = Field(default=None, description="Return URL after PayPal approval")
    cancel_url: Optional[str] = Field(default=None, description="Cancel URL if user cancels checkout")


class PayPalCreateOrderResponse(BaseModel):
    """Response returned when a PayPal checkout order is generated."""
    order_id: str
    payment_id: str
    status: str
    approve_url: Optional[str] = None
    amount: float
    currency: str


class PayPalCaptureResponse(BaseModel):
    """Authoritative response after server-side capture verification."""
    order_id: str
    capture_id: str
    payment_id: str
    status: str
    amount: float
    currency: str
    registration_status: str
