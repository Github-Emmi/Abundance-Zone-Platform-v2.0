"""Attendance Model"""

from typing import Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base, TimestampMixin
from app.domain.value_objects.enums import AttendanceStatus


class AttendanceModel(Base, TimestampMixin):
    __tablename__ = "attendance"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(AttendanceStatus, name="attendance_status"),
        default=AttendanceStatus.PENDING_CHECK_IN,
    )
    check_in_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    check_out_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    youth_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("youths.id", ondelete="CASCADE"), nullable=False
    )
    event_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    recorded_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True
    )

    youth = relationship("YouthModel", back_populates="attendance_records")
    event = relationship("EventModel", back_populates="attendance_records")

    __table_args__ = (
        UniqueConstraint("youth_id", "event_id", name="uq_attendance_youth_event"),
        Index("ix_attendance_youth", "youth_id"),
        Index("ix_attendance_event", "event_id"),
        {"comment": "Attendance records"},
    )
