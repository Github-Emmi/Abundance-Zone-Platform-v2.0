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


class AttendanceReportRequest(BaseModel):
    """Request schema for generating attendance reports."""

    date: str | None = Field(
        None, description="ISO format date (defaults to today if not provided)"
    )
    send_email: bool = Field(
        False, description="Whether to email the report to coordinators"
    )


class AttendanceReportResponse(BaseModel):
    """Response schema for attendance report generation."""

    task_id: str | None
    status: str
    message: str
    date: str
    timestamp: str
