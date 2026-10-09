"""Notification API Schemas"""
from datetime import datetime
from pydantic import BaseModel, Field
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
