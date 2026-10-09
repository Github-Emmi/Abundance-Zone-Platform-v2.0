"""Attendance API Schemas"""
from datetime import datetime
from pydantic import BaseModel, Field


class AttendanceRecordRequest(BaseModel):
    event_id: str
    youth_id: str


class BulkAttendanceRequest(BaseModel):
    event_id: str
    youth_ids: list[str] = Field(..., min_items=1)


class AttendanceResponse(BaseModel):
    id: str
    event_id: str
    youth_id: str
    status: str
    check_in_time: datetime | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceSummaryResponse(BaseModel):
    total_events: int
    total_attendances: int
    unique_youths: int
    attendance_rate: float


class AttendanceHeatmapResponse(BaseModel):
    date: str
    count: int
