"""
Analytics and Reports Request/Response Schemas

Provides Pydantic models for report generation requests and responses.
Supports daily, weekly, monthly, and custom date range reports with validation.

Implements: FR-REPORTS-001, FR-REPORTS-002
"""

from datetime import datetime, timedelta
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


class DailyReportRequest(BaseModel):
    """
    Request schema for daily attendance report generation.

    Attributes:
        date: ISO format date (YYYY-MM-DD), defaults to today if not provided
        send_email: Whether to email the report to administrators (future feature)

    Examples:
        >>> request = DailyReportRequest(date="2026-10-08", send_email=False)
        >>> request = DailyReportRequest()  # Uses today's date
    """

    date: Optional[str] = Field(
        default=None,
        description="ISO format date (YYYY-MM-DD), defaults to today",
        examples=["2026-10-08", "2026-09-15"],
    )
    send_email: bool = Field(
        default=False,
        description="Whether to email the report to administrators",
    )

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date is in ISO format and not in the future."""
        if v is None:
            return v

        try:
            date_obj = datetime.fromisoformat(v).date()
        except ValueError:
            raise ValueError("Date must be in ISO format (YYYY-MM-DD)")

        if date_obj > datetime.utcnow().date():
            raise ValueError("Date cannot be in the future")

        return v


class WeeklyReportRequest(BaseModel):
    """
    Request schema for weekly analytics report generation.

    Attributes:
        week_offset: Weeks before current week (0=current, 1=last week, 2=two weeks ago)

    Examples:
        >>> request = WeeklyReportRequest(week_offset=0)  # Current week
        >>> request = WeeklyReportRequest(week_offset=1)  # Last week
    """

    week_offset: int = Field(
        default=0,
        ge=0,
        le=52,
        description="Weeks before current week (0=current, 1=last week)",
        examples=[0, 1, 2],
    )


class MonthlyReportRequest(BaseModel):
    """
    Request schema for monthly financial report generation.

    Attributes:
        month: Month in YYYY-MM format, defaults to current month if not provided

    Examples:
        >>> request = MonthlyReportRequest(month="2026-10")
        >>> request = MonthlyReportRequest()  # Uses current month
    """

    month: Optional[str] = Field(
        default=None,
        description="Month in YYYY-MM format, defaults to current month",
        examples=["2026-10", "2026-09"],
    )

    @field_validator("month")
    @classmethod
    def validate_month_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate month is in YYYY-MM format and not in the future."""
        if v is None:
            return v

        try:
            month_obj = datetime.strptime(v, "%Y-%m").date()
        except ValueError:
            raise ValueError("Month must be in YYYY-MM format")

        current_month = datetime.utcnow().date().replace(day=1)
        if month_obj > current_month:
            raise ValueError("Month cannot be in the future")

        return v


class CustomReportRequest(BaseModel):
    """
    Request schema for custom date range report generation.

    Attributes:
        start_date: Report start date in ISO format (YYYY-MM-DD)
        end_date: Report end date in ISO format (YYYY-MM-DD)
        report_type: Type of report to generate (attendance, events, users)

    Validation:
        - end_date must be after start_date
        - Date range cannot exceed 90 days
        - Dates cannot be in the future

    Examples:
        >>> request = CustomReportRequest(
        ...     start_date="2026-09-01",
        ...     end_date="2026-09-30",
        ...     report_type="attendance"
        ... )
    """

    start_date: str = Field(
        ...,
        description="Report start date in ISO format (YYYY-MM-DD)",
        examples=["2026-09-01", "2026-10-01"],
    )
    end_date: str = Field(
        ...,
        description="Report end date in ISO format (YYYY-MM-DD)",
        examples=["2026-09-30", "2026-10-31"],
    )
    report_type: Literal["attendance", "events", "users"] = Field(
        default="attendance",
        description="Type of report to generate",
        examples=["attendance", "events", "users"],
    )

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v: str) -> str:
        """Validate start_date is in ISO format and not in the future."""
        try:
            start = datetime.fromisoformat(v).date()
        except ValueError:
            raise ValueError("start_date must be in ISO format (YYYY-MM-DD)")

        if start > datetime.utcnow().date():
            raise ValueError("start_date cannot be in the future")

        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: str, info) -> str:
        """Validate end_date and check date range constraints."""
        try:
            end = datetime.fromisoformat(v).date()
        except ValueError:
            raise ValueError("end_date must be in ISO format (YYYY-MM-DD)")

        if end > datetime.utcnow().date():
            raise ValueError("end_date cannot be in the future")

        # Validate against start_date if available
        start_date_str = info.data.get("start_date")
        if start_date_str:
            try:
                start = datetime.fromisoformat(start_date_str).date()

                if end <= start:
                    raise ValueError("end_date must be after start_date")

                # Check 90-day limit
                date_range = (end - start).days
                if date_range > 90:
                    raise ValueError(
                        f"Date range cannot exceed 90 days (current range: {date_range} days)"
                    )
            except ValueError as e:
                # Re-raise validation errors
                if "must be after" in str(e) or "cannot exceed" in str(e):
                    raise
                # Ignore other parsing errors (already validated in start_date)

        return v


class ReportResponse(BaseModel):
    """
    Response schema for report generation requests.

    Attributes:
        task_id: Celery task ID for tracking report generation (None if synchronous)
        status: Report generation status (queued, processing, completed, error)
        message: Human-readable status message
        report_type: Type of report being generated
        date_range: Date range or parameters for the report
        timestamp: UTC timestamp when the request was received

    Examples:
        >>> response = ReportResponse(
        ...     task_id="abc123-def456",
        ...     status="queued",
        ...     message="Daily attendance report generation started",
        ...     report_type="daily_attendance",
        ...     date_range={"date": "2026-10-08"},
        ...     timestamp="2026-10-08T10:30:00Z"
        ... )
    """

    task_id: Optional[str] = Field(
        default=None,
        description="Celery task ID for tracking report generation",
        examples=["abc123-def456-ghi789"],
    )
    status: str = Field(
        ...,
        description="Report generation status",
        examples=["queued", "processing", "completed", "error"],
    )
    message: str = Field(
        ...,
        description="Human-readable status message",
        examples=[
            "Daily attendance report generation started",
            "Report ready for download",
        ],
    )
    report_type: str = Field(
        ...,
        description="Type of report being generated",
        examples=["daily_attendance", "weekly_analytics", "monthly_financial"],
    )
    date_range: Optional[dict] = Field(
        default=None,
        description="Date range or parameters for the report",
        examples=[
            {"date": "2026-10-08"},
            {"week_start": "2026-10-07", "week_end": "2026-10-14"},
        ],
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="UTC timestamp when the request was received",
        examples=["2026-10-08T10:30:00Z"],
    )


class ReportStatusResponse(BaseModel):
    """
    Response schema for report generation status queries.

    Attributes:
        task_id: Celery task ID
        state: Celery task state (PENDING, STARTED, SUCCESS, FAILURE, RETRY)
        result: Task result data if completed successfully
        error: Error message if task failed
        progress: Task progress information (percentage, current step)

    Examples:
        >>> response = ReportStatusResponse(
        ...     task_id="abc123",
        ...     state="SUCCESS",
        ...     result={"total_records": 150, "csv_size": 5120},
        ...     error=None
        ... )
    """

    task_id: str = Field(
        ...,
        description="Celery task ID",
        examples=["abc123-def456-ghi789"],
    )
    state: str = Field(
        ...,
        description="Celery task state",
        examples=["PENDING", "STARTED", "SUCCESS", "FAILURE"],
    )
    result: Optional[dict] = Field(
        default=None,
        description="Task result data if completed successfully",
        examples=[{"total_records": 150, "csv_size": 5120}],
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if task failed",
        examples=["Database connection timeout", "Invalid date range"],
    )
    progress: Optional[dict] = Field(
        default=None,
        description="Task progress information",
        examples=[{"percent": 75, "step": "Generating CSV"}],
    )
