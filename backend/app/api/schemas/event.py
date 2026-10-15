"""Event API Schemas"""

from datetime import datetime
from pydantic import BaseModel, Field
from app.domain.value_objects.enums import EventType, EventStatus


class EventCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    event_type: EventType
    event_date: datetime
    branch_id: str
    description: str | None = None
    venue: str | None = Field(None, max_length=255)
    end_date: datetime | None = None


class EventUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    event_date: datetime | None = None
    venue: str | None = None
    status: EventStatus | None = None


class EventResponse(BaseModel):
    id: str
    title: str
    event_type: str
    event_date: datetime
    branch_id: str
    created_by_id: str
    description: str | None
    venue: str | None
    status: str
    is_recurring: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RSVPRequest(BaseModel):
    status: str = Field(..., pattern="^(GOING|MAYBE|NOT_GOING)$")


class RecurringEventRequest(BaseModel):
    frequency: str = Field(..., pattern="^(daily|weekly|monthly)$")
    interval: int = Field(1, ge=1, le=365)
    end_date: datetime | None = None
    occurrences: int | None = Field(None, ge=1, le=100)


class EventReminderRequest(BaseModel):
    """Request schema for sending event reminders to registrants"""

    reminder_hours_before: int = Field(
        24, ge=1, le=168, description="Hours before event to remind (default 24)"
    )
    custom_message: str | None = Field(
        None, max_length=500, description="Additional custom message to include"
    )


class EventNotifyRequest(BaseModel):
    """Request schema for sending custom notifications to event registrants"""

    subject: str = Field(..., min_length=1, max_length=200, description="Email subject line")
    message: str = Field(..., min_length=1, max_length=1000, description="Email message content")
    notification_type: str = Field(
        "announcement",
        pattern="^(announcement|update|cancellation)$",
        description="Type of notification",
    )


class EventNotificationResponse(BaseModel):
    """Response schema for event notification operations"""

    task_ids: list[str] | None = Field(
        default=None, description="List of Celery task IDs for tracking"
    )
    status: str = Field(..., description="Overall status: queued/error")
    message: str = Field(..., description="Human-readable status message")
    event_id: str = Field(..., description="Event identifier")
    recipient_count: int = Field(..., description="Number of recipients")
    failed_count: int = Field(0, description="Number of failed dispatches")
    timestamp: str = Field(..., description="Timestamp of operation")
