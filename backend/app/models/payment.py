"""SQLAlchemy model for customer payment records and PayPal order tracking.

SECURITY GUARANTEE:
Never stores raw credit card numbers, CVVs, or cardholder banking credentials.
Tracks only sanitized PayPal order tokens and server-verified capture IDs.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.registration import RegistrationModel
    from app.models.transaction import TransactionModel


class PaymentModel(Base):
    """Payment record linked to a registration and PayPal checkout order."""

    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    registration_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("registrations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    paypal_order_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True,
    )
    paypal_capture_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )
    payment_status: Mapped[str] = mapped_column(
        String(50),
        default="unpaid",
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    registration: Mapped["RegistrationModel"] = relationship(
        "RegistrationModel",
        back_populates="payments",
    )
    transactions: Mapped[List["TransactionModel"]] = relationship(
        "TransactionModel",
        back_populates="payment",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Payment id={self.id} amount={self.amount} {self.currency} status={self.payment_status} order_id={self.paypal_order_id}>"

