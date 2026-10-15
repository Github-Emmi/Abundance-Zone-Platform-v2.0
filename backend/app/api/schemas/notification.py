"""Notification API Schemas"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.domain.value_objects.enums import NotificationType


class NotificationResponse(BaseModel):
    id: str
    title: str
    content: str
    type: str
    read_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class BroadcastRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    notification_type: NotificationType


# ═══════════════════════════════════════════════════════════════════════════
# PUSH NOTIFICATION SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════


class PushNotificationRequest(BaseModel):
    """Request schema for sending a single push notification."""

    device_token: str = Field(
        ...,
        description="FCM device token",
        min_length=1,
        max_length=500,
    )
    title: str = Field(
        ...,
        description="Notification title",
        min_length=1,
        max_length=200,
    )
    body: str = Field(
        ...,
        description="Notification body/message",
        min_length=1,
        max_length=500,
    )
    data: Optional[Dict[str, str]] = Field(
        None,
        description="Custom data payload for the notification",
    )
    image_url: Optional[str] = Field(
        None,
        description="Image URL for rich notification (optional)",
        max_length=2048,
    )


class BulkNotificationRequest(BaseModel):
    """Request schema for sending bulk push notifications."""

    device_tokens: List[str] = Field(
        ...,
        description="List of FCM device tokens",
        min_length=1,
        max_length=500,
    )
    title: str = Field(
        ...,
        description="Notification title",
        min_length=1,
        max_length=200,
    )
    body: str = Field(
        ...,
        description="Notification body/message",
        min_length=1,
        max_length=500,
    )
    data: Optional[Dict[str, str]] = Field(
        None,
        description="Custom data payload for the notification",
    )
    image_url: Optional[str] = Field(
        None,
        description="Image URL for rich notification (optional)",
        max_length=2048,
    )

    @field_validator("device_tokens")
    @classmethod
    def validate_token_count(cls, v: List[str]) -> List[str]:
        """Validate maximum token count per request."""
        if len(v) > 500:
            raise ValueError("Maximum 500 device tokens allowed per request")
        if len(v) == 0:
            raise ValueError("At least one device token is required")
        return v


class TopicNotificationRequest(BaseModel):
    """Request schema for sending topic-based push notification."""

    topic: str = Field(
        ...,
        description="FCM topic name",
        min_length=1,
        max_length=200,
    )
    title: str = Field(
        ...,
        description="Notification title",
        min_length=1,
        max_length=200,
    )
    body: str = Field(
        ...,
        description="Notification body/message",
        min_length=1,
        max_length=500,
    )
    data: Optional[Dict[str, str]] = Field(
        None,
        description="Custom data payload for the notification",
    )


class TopicSubscriptionRequest(BaseModel):
    """Request schema for subscribing/unsubscribing devices to/from a topic."""

    device_tokens: List[str] = Field(
        ...,
        description="List of FCM device tokens to subscribe/unsubscribe",
        min_length=1,
        max_length=1000,
    )

    @field_validator("device_tokens")
    @classmethod
    def validate_token_count(cls, v: List[str]) -> List[str]:
        """Validate maximum token count per request."""
        if len(v) > 1000:
            raise ValueError("Maximum 1000 device tokens allowed per request")
        if len(v) == 0:
            raise ValueError("At least one device token is required")
        return v


class ScheduledNotificationRequest(BaseModel):
    """Request schema for scheduling a push notification."""

    device_token: str = Field(
        ...,
        description="FCM device token",
        min_length=1,
        max_length=500,
    )
    title: str = Field(
        ...,
        description="Notification title",
        min_length=1,
        max_length=200,
    )
    body: str = Field(
        ...,
        description="Notification body/message",
        min_length=1,
        max_length=500,
    )
    schedule_time: datetime = Field(
        ...,
        description="Scheduled delivery time (must be in the future)",
    )
    data: Optional[Dict[str, str]] = Field(
        None,
        description="Custom data payload for the notification",
    )

    @field_validator("schedule_time")
    @classmethod
    def validate_schedule_time(cls, v: datetime) -> datetime:
        """Validate that schedule time is in the future."""
        now = datetime.now(v.tzinfo) if v.tzinfo else datetime.utcnow()
        if v <= now:
            raise ValueError("Schedule time must be in the future")
        return v
