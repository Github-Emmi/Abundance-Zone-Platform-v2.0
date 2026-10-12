"""Event Model"""

from typing import Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base, TimestampMixin
from app.domain.value_objects.enums import EventType, EventStatus


class EventModel(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(
        SQLEnum(EventType, name="event_type"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(EventStatus, name="event_status"), default=EventStatus.DRAFT
    )
    event_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    is_regional: Mapped[bool] = mapped_column(Boolean, default=False)

    branch_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("branches.id", name="fk_events_branch"),
        nullable=True,
    )
    created_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", name="fk_events_created_by"),
        nullable=False,
    )

    branch = relationship("BranchModel", back_populates="events")
    creator = relationship(
        "UserModel", foreign_keys=[created_by_id], back_populates="created_events"
    )
    attendance_records = relationship(
        "AttendanceModel", back_populates="event", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_events_date", "event_date"),
        Index("ix_events_type", "event_type"),
        {"comment": "Events and services"},
    )
