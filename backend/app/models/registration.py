"""SQLAlchemy model for customer event and workshop registrations."""

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.workflow import WorkflowModel
    from app.models.payment import PaymentModel


class RegistrationModel(Base):
    """Customer registration record associating an attendee with a workflow."""

    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint("workflow_id", "customer_email", name="uq_workflow_customer_email"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    workflow_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    customer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    customer_email: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    registration_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    workflow: Mapped["WorkflowModel"] = relationship(
        "WorkflowModel",
        back_populates="registrations",
    )
    payments: Mapped[List["PaymentModel"]] = relationship(
        "PaymentModel",
        back_populates="registration",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Registration id={self.id} workflow_id={self.workflow_id} email={self.customer_email} status={self.registration_status}>"

