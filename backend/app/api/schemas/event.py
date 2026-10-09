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
