"""Notification Model"""

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
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base, TimestampMixin
from app.domain.value_objects.enums import (
    NotificationType,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
)


class NotificationModel(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    type: Mapped[str] = mapped_column(
        SQLEnum(NotificationType, name="notification_type"), nullable=False
    )
    channel: Mapped[str] = mapped_column(
        SQLEnum(NotificationChannel, name="notification_channel"), nullable=False
    )
    priority: Mapped[str] = mapped_column(
        SQLEnum(NotificationPriority, name="notification_priority"),
        default=NotificationPriority.NORMAL,
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(NotificationStatus, name="notification_status"),
        default=NotificationStatus.QUEUED,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    notification_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="Additional metadata for the notification"
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("UserModel", back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_user", "user_id"),
        Index("ix_notifications_type", "type"),
        {"comment": "User notifications"},
    )
