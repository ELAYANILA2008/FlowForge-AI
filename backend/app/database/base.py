"""SQLAlchemy 2.x Declarative Base and Model Mixins.

Defines the centralized base class for all database models and provides
standardized timestamp mixins with UTC timezone support.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Central declarative base class for all FlowForge AI database models."""
    pass


class TimestampMixin:
    """Provides created_at and updated_at datetime columns stored in UTC."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


def generate_uuid() -> str:
    """Generate a clean UUID4 string identifier."""
    return str(uuid.uuid4())

