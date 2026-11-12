"""SQLAlchemy model for financial transaction records and verification audit trails."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, generate_uuid
from app.core.security import generate_reference_id

if TYPE_CHECKING:
    from app.models.payment import PaymentModel


class TransactionModel(Base):
    """Audit record for a verified financial transaction and webhook confirmation."""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    payment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("payments.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    transaction_reference: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        default=lambda: generate_reference_id("TXN"),
        nullable=False,
    )
    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    payment: Mapped["PaymentModel"] = relationship(
        "PaymentModel",
        back_populates="transactions",
    )

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} ref={self.transaction_reference} status={self.verification_status}>"

