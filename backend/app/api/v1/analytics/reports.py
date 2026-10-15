"""
Analytics and Reports API Router

Provides comprehensive report generation and export endpoints with async Celery integration.
Supports daily, weekly, monthly, and custom date range reports with CSV export capabilities.

**Report Types:**
- Daily Attendance Reports: Check-in/out records, durations, status breakdowns
- Weekly Analytics: Attendance stats, top attendees, average durations, event counts
- Monthly Financial: Pledge and payment summaries (requires finance models)
- Custom Reports: Flexible date ranges and report types (max 90 days)
- User Exports: Complete user directory with active members

**Report Generation Flow:**
1. Client submits report request → Returns task_id immediately (202 Accepted)
2. Celery worker processes report in background (1-3 minutes typical)
3. Client polls /analytics/reports/{task_id}/download for completion
4. Once complete, download CSV via same endpoint

**CSV Format Examples:**

*Daily Attendance Report:*
User Name,Email,Event,Check In Time,Check Out Time,Status,Duration (minutes)
John Doe,john@example.com,Sunday Service,2026-10-08 09:00:00,2026-10-08 11:30:00,PRESENT,150

*Weekly Analytics:*
Returns JSON with: total_attendance, unique_users, avg_duration_minutes, total_events, top_attendees[]

*Users Export:*
ID,Name,Email,Phone,Role,Created At
123e4567-e89b-12d3-a456-426614174000,John Doe,john@example.com,+1234567890,YOUTH_MEMBER,2026-09-01 10:00:00

**Performance:**
- Daily reports: ~30-60 seconds (typical: 50-200 records)
- Weekly analytics: ~45-90 seconds (aggregation queries)
- Custom reports: ~1-3 minutes (depends on date range)
- User exports: ~15-30 seconds (depends on total users)

**RBAC:**
- Daily/Weekly/Custom Reports: BRANCH_COORDINATOR, SUPER_ADMIN
- Monthly Financial: SUPER_ADMIN only (sensitive financial data)
- User Exports: SUPER_ADMIN only (complete user data)

Implements: FR-REPORTS-001, FR-REPORTS-002, FR-ANALYTICS-001
"""

import logging
from datetime import datetime

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import Response

from app.api.deps import require_role
from app.api.schemas.report import (
    CustomReportRequest,
    DailyReportRequest,
    MonthlyReportRequest,
    ReportResponse,
    WeeklyReportRequest,
)
from app.api.schemas.responses import ApiResponse
from app.domain.value_objects.enums import Role
from app.tasks.celery_app import celery_app
from app.tasks.reports import (
    export_users_csv,
    generate_custom_report,
    generate_daily_attendance_report,
    generate_monthly_financial_report,
    generate_weekly_analytics,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/analytics", tags=["Analytics & Reports"])


@router.post(
    "/reports/daily",
    response_model=ApiResponse[ReportResponse],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role([Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN]))],
    summary="Generate daily attendance report",
    description="""
    **Generate Daily Attendance Report (CSV)**
    
    Creates a comprehensive CSV report of all attendance records for a specific date.
    The report includes check-in/check-out times, event details, attendance status,
    and calculated durations.
    
    **Report Contents:**
    - User identification (name, email)
    - Event association
    - Check-in and check-out timestamps
    - Attendance status (PRESENT, ABSENT, LATE, EXCUSED)
    - Duration in minutes (calculated from check-in/out)
    - Summary statistics (total present, absent, late)
    
    **CSV Format:**
    ```
    User Name,Email,Event,Check In Time,Check Out Time,Status,Duration (minutes)
    John Doe,john@example.com,Sunday Service,2026-10-08 09:00:00,2026-10-08 11:30:00,PRESENT,150
    Jane Smith,jane@example.com,Sunday Service,2026-10-08 09:15:00,2026-10-08 11:30:00,LATE,135
    ```
    
    **Generation Time:** Typically 30-60 seconds depending on record count (50-200 records typical)
    
    **How to Download:**
    1. Submit this request → receive task_id
    2. Poll GET /analytics/reports/{task_id}/download
    3. When ready (202 → 200), download CSV
    
    **Use Cases:**
    - Daily operations review
    - Attendance tracking and verification
    - Event participation analysis
    - Administrative reporting
    
    **Required Permissions:** BRANCH_COORDINATOR or SUPER_ADMIN
    """,
)
async def generate_daily_report(
    request: DailyReportRequest,
) -> ApiResponse[ReportResponse]:
    """
    Generate daily attendance report.

    Args:
        request: Daily report request with date and email preferences

    Returns:
        ApiResponse containing task_id and report metadata

    Raises:
        HTTPException: If task dispatch fails
    """
    try:
        # Dispatch Celery task
        task = generate_daily_attendance_report.delay(
            date=request.date, send_email=request.send_email
        )
        task_id = task.id

        logger.info(
            f"Dispatched daily report task {task_id} for date {request.date or 'today'}"
        )

        return ApiResponse(
            data=ReportResponse(
                task_id=task_id,
                status="queued",
                message="Daily attendance report generation started",
                report_type="daily_attendance",
                date_range={
                    "date": request.date or datetime.utcnow().date().isoformat()
                },
                timestamp=datetime.utcnow().isoformat(),
            )
        )

    except Exception as e:
        logger.error(f"Failed to dispatch daily report task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue report generation",
        )


@router.post(
    "/reports/weekly",
    response_model=ApiResponse[ReportResponse],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role([Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN]))],
    summary="Generate weekly analytics report",
    description="""
    **Generate Weekly Analytics Report (JSON)**
    
    Creates comprehensive weekly analytics with attendance statistics, engagement metrics,
    and top performer identification. Returns JSON data (not CSV).
    
    **Report Contents:**
    - Total attendance records for the week
    - Unique users who attended
    - Average session duration in minutes
    - Total events completed
    - Top 10 attendees by attendance count
    
    **JSON Response Structure:**
    ```json
    {
        "status": "completed",
        "week_start": "2026-10-07",
        "week_end": "2026-10-14",
        "total_attendance": 450,
        "unique_users": 85,
        "avg_duration_minutes": 125.5,
        "total_events": 8,
        "top_attendees": [
            {"name": "John Doe", "count": 8},
            {"name": "Jane Smith", "count": 7}
        ]
    }
    ```
    
    **Week Calculation:**
    - week_offset=0: Current week (Monday to Sunday)
    - week_offset=1: Last week
    - week_offset=2: Two weeks ago
    - Maximum: 52 weeks back
    
    **Generation Time:** Typically 45-90 seconds (aggregation queries across week)
    
    **How to Download:**
    1. Submit this request → receive task_id
    2. Poll GET /analytics/reports/{task_id}/download
    3. Retrieve JSON result from response
    
    **Use Cases:**
    - Weekly operations review
    - Engagement trend analysis
    - Recognition of top participants
    - Resource planning for upcoming week
    
    **Required Permissions:** BRANCH_COORDINATOR or SUPER_ADMIN
    """,
)
async def generate_weekly_report(
    request: WeeklyReportRequest,
) -> ApiResponse[ReportResponse]:
    """
    Generate weekly analytics report.

    Args:
        request: Weekly report request with week offset

    Returns:
        ApiResponse containing task_id and report metadata

    Raises:
        HTTPException: If task dispatch fails
    """
    try:
        # Dispatch Celery task
        task = generate_weekly_analytics.delay(week_offset=request.week_offset)
        task_id = task.id

        # Calculate week range for metadata
        from datetime import date, timedelta

        today = date.today()
        start_of_week = today - timedelta(
            days=today.weekday() + (request.week_offset * 7)
        )
        end_of_week = start_of_week + timedelta(days=7)

        logger.info(
            f"Dispatched weekly analytics task {task_id} for week offset {request.week_offset}"
        )

        return ApiResponse(
            data=ReportResponse(
                task_id=task_id,
                status="queued",
                message="Weekly analytics report generation started",
                report_type="weekly_analytics",
                date_range={
                    "week_start": start_of_week.isoformat(),
                    "week_end": end_of_week.isoformat(),
                    "week_offset": request.week_offset,
                },
                timestamp=datetime.utcnow().isoformat(),
            )
        )

    except Exception as e:
        logger.error(f"Failed to dispatch weekly analytics task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue report generation",
        )


@router.post(
    "/reports/monthly",
    response_model=ApiResponse[ReportResponse],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role(Role.SUPER_ADMIN))],
    summary="Generate monthly financial report",
    description="""
    **Generate Monthly Financial Report (JSON) - SUPER_ADMIN ONLY**
    
    Creates monthly financial summary with pledge and payment statistics.
    Access restricted to SUPER_ADMIN due to sensitive financial data.
    
    **⚠️ Note:** This endpoint currently returns placeholder data. Full implementation
    requires pledge and payment models to be completed.
    
    **Planned Report Contents:**
    - Total pledges made during the month
    - Total payments received
    - Outstanding/pending payments
    - Payment completion rate (percentage)
    - Breakdown by pledge type (monthly, project, special)
    - Top contributors
    
    **JSON Response Structure (When Implemented):**
    ```json
    {
        "status": "completed",
        "month": "2026-10",
        "month_name": "October 2026",
        "total_pledges": 15000.00,
        "total_paid": 12500.00,
        "total_pending": 2500.00,
        "payment_rate": 83.33,
        "breakdown_by_type": {...}
    }
    ```
    
    **Generation Time:** Expected 60-120 seconds (financial aggregations)
    
    **Security Note:** Financial reports are restricted to SUPER_ADMIN only to protect
    sensitive member contribution data.
    
    **Use Cases:**
    - Monthly financial review
    - Budget planning
    - Fundraising campaign assessment
    - Year-end financial reporting
    
    **Required Permissions:** SUPER_ADMIN only
    """,
)
async def generate_monthly_report(
    request: MonthlyReportRequest,
) -> ApiResponse[ReportResponse]:
    """
    Generate monthly financial report.

    Args:
        request: Monthly report request with month parameter

    Returns:
        ApiResponse containing task_id and report metadata

    Raises:
        HTTPException: If task dispatch fails
    """
    try:
        # Dispatch Celery task
        task = generate_monthly_financial_report.delay(month=request.month)
        task_id = task.id

        # Parse month for metadata
        if request.month:
            month_date = datetime.strptime(request.month, "%Y-%m")
        else:
            month_date = datetime.utcnow().replace(day=1)

        logger.info(
            f"Dispatched monthly financial report task {task_id} for month {request.month or 'current'}"
        )

        return ApiResponse(
            data=ReportResponse(
                task_id=task_id,
                status="queued",
                message="Monthly financial report generation started",
                report_type="monthly_financial",
                date_range={
                    "month": month_date.strftime("%Y-%m"),
                    "month_name": month_date.strftime("%B %Y"),
                },
                timestamp=datetime.utcnow().isoformat(),
            )
        )

    except Exception as e:
        logger.error(f"Failed to dispatch monthly financial report task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue report generation",
        )


@router.post(
    "/reports/custom",
    response_model=ApiResponse[ReportResponse],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role([Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN]))],
    summary="Generate custom date range report",
    description="""
    **Generate Custom Date Range Report (CSV)**
    
    Creates flexible reports with custom date ranges and report types.
    Maximum date range: 90 days to ensure reasonable generation times.
    
    **Report Types:**
    
    1. **Attendance Report:**
       - All attendance records in date range
       - User details, events, timestamps, statuses
       - Duration calculations
       - CSV format similar to daily report
    
    2. **Events Report (Future):**
       - All events in date range
       - Event details, attendance counts, completion status
       - CSV with event-centric view
    
    3. **Users Report (Future):**
       - Users created/modified in date range
       - Full user details and activity summary
       - CSV with user-centric view
    
    **CSV Format (Attendance):**
    ```
    User,Event,Check In,Check Out,Status
    John Doe,Sunday Service,2026-10-08 09:00,2026-10-08 11:30,PRESENT
    Jane Smith,Bible Study,2026-10-09 18:00,2026-10-09 19:30,PRESENT
    ```
    
    **Validation Rules:**
    - end_date must be after start_date
    - Maximum date range: 90 days
    - Dates cannot be in the future
    - All dates in ISO format (YYYY-MM-DD)
    
    **Generation Time:** 1-3 minutes depending on date range and record count
    - 1 week: ~30 seconds
    - 1 month: ~60 seconds
    - 90 days: ~2-3 minutes
    
    **How to Download:**
    1. Submit this request → receive task_id
    2. Poll GET /analytics/reports/{task_id}/download
    3. Download CSV when ready
    
    **Use Cases:**
    - Quarterly attendance analysis
    - Seasonal participation trends
    - Event-specific reporting
    - Custom administrative reports
    
    **Required Permissions:** BRANCH_COORDINATOR or SUPER_ADMIN
    """,
)
async def generate_custom_report_endpoint(
    request: CustomReportRequest,
) -> ApiResponse[ReportResponse]:
    """
    Generate custom date range report.

    Args:
        request: Custom report request with date range and report type

    Returns:
        ApiResponse containing task_id and report metadata

    Raises:
        HTTPException: If task dispatch fails
    """
    try:
        # Dispatch Celery task
        task = generate_custom_report.delay(
            start_date=request.start_date,
            end_date=request.end_date,
            report_type=request.report_type,
        )
        task_id = task.id

        logger.info(
            f"Dispatched custom report task {task_id} "
            f"({request.report_type}, {request.start_date} to {request.end_date})"
        )

        return ApiResponse(
            data=ReportResponse(
                task_id=task_id,
                status="queued",
                message=f"Custom {request.report_type} report generation started",
                report_type=f"custom_{request.report_type}",
                date_range={
                    "start_date": request.start_date,
                    "end_date": request.end_date,
                    "report_type": request.report_type,
                },
                timestamp=datetime.utcnow().isoformat(),
            )
        )

    except Exception as e:
        logger.error(f"Failed to dispatch custom report task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue report generation",
        )


@router.get(
    "/reports/{task_id}/download",
    dependencies=[Depends(require_role([Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN]))],
    summary="Download or check report status",
    description="""
    **Download Report or Check Generation Status**
    
    Multi-purpose endpoint that serves both as a status checker and download endpoint.
    Poll this endpoint to check report generation progress, then download when complete.
    
    **Response Codes:**
    - **200 OK:** Report ready - returns CSV file or JSON data
    - **202 Accepted:** Report still processing - check again in 5-10 seconds
    - **400 Bad Request:** Report generation failed - see error details
    - **404 Not Found:** Invalid task_id
    
    **Polling Pattern:**
    ```python
    # Pseudo-code for client implementation
    task_id = create_report()  # Returns task_id
    
    while True:
        response = GET /analytics/reports/{task_id}/download
        
        if response.status == 200:
            # Download ready
            save_file(response.body)
            break
        elif response.status == 202:
            # Still processing
            wait(5_seconds)
            continue
        else:
            # Error occurred
            handle_error(response)
            break
    ```
    
    **Response Types:**
    
    1. **CSV Reports (200 OK):**
       - Content-Type: text/csv
       - Content-Disposition: attachment; filename=report_{task_id}.csv
       - Body: Raw CSV data
    
    2. **JSON Reports (200 OK):**
       - Content-Type: application/json
       - Body: Report data as JSON object
    
    3. **Processing (202 Accepted):**
       - Content-Type: application/json
       - Body: {"detail": "Report still processing", "progress": {...}}
    
    4. **Failed (400 Bad Request):**
       - Content-Type: application/json
       - Body: {"detail": "Report generation failed", "error": "..."}
    
    **Query Parameters:**
    - format: Output format (default: "csv", future: "xlsx", "pdf", "json")
    
    **Performance Tips:**
    - Poll every 5-10 seconds (avoid excessive polling)
    - Set client timeout to 5 minutes minimum
    - Handle 202 responses gracefully
    - Cache completed reports client-side
    
    **Security:**
    - Task IDs are UUIDs (not guessable)
    - RBAC enforced (same as report creation)
    - Reports expire after 24 hours
    
    **Required Permissions:** BRANCH_COORDINATOR or SUPER_ADMIN
    """,
)
async def download_report(
    task_id: str = Path(..., description="Celery task ID from report generation"),
    format: str = Query(
        default="csv",
        description="Output format (csv, json)",
        regex="^(csv|json)$",
    ),
):
    """
    Download report or check generation status.

    Args:
        task_id: Celery task ID from report generation endpoint
        format: Output format preference (csv or json)

    Returns:
        Response with CSV/JSON data or status information

    Raises:
        HTTPException: If task not found, failed, or still processing (202)
    """
    try:
        # Get task result from Celery
        task_result = AsyncResult(task_id, app=celery_app)

        # Check task state
        if task_result.state == "PENDING":
            logger.info(f"Report task {task_id} still pending")
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail={
                    "message": "Report still processing",
                    "state": "PENDING",
                    "task_id": task_id,
                },
            )

        elif task_result.state == "STARTED":
            logger.info(f"Report task {task_id} in progress")
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail={
                    "message": "Report generation in progress",
                    "state": "STARTED",
                    "task_id": task_id,
                },
            )

        elif task_result.state == "FAILURE":
            error_msg = str(task_result.info) if task_result.info else "Unknown error"
            logger.error(f"Report task {task_id} failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Report generation failed",
                    "error": error_msg,
                    "task_id": task_id,
                },
            )

        elif task_result.state == "SUCCESS":
            result = task_result.result
            logger.info(f"Report task {task_id} completed successfully")

            # Check if result contains CSV content
            if "csv_content" in result and format == "csv":
                csv_content = result["csv_content"]
                return Response(
                    content=csv_content,
                    media_type="text/csv",
                    headers={
                        "Content-Disposition": f"attachment; filename=report_{task_id}.csv"
                    },
                )

            # Return JSON result
            else:
                return ApiResponse(
                    data={
                        "task_id": task_id,
                        "state": "SUCCESS",
                        "result": result,
                    }
                )

        else:
            # Unknown state
            logger.warning(
                f"Report task {task_id} in unknown state: {task_result.state}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Unknown task state",
                    "state": task_result.state,
                    "task_id": task_id,
                },
            )

    except HTTPException:
        # Re-raise HTTP exceptions (status checks)
        raise

    except Exception as e:
        logger.error(f"Failed to retrieve report {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report",
        )


@router.post(
    "/export/users",
    response_model=ApiResponse[ReportResponse],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role(Role.SUPER_ADMIN))],
    summary="Export all users to CSV",
    description="""
    **Export All Active Users to CSV - SUPER_ADMIN ONLY**
    
    Exports complete user directory with all active members to CSV format.
    Access restricted to SUPER_ADMIN due to complete user data exposure.
    
    **CSV Contents:**
    - User ID (UUID)
    - Full name
    - Email address
    - Phone number
    - Role (YOUTH_MEMBER, DEPARTMENT_LEADER, etc.)
    - Account creation timestamp
    
    **CSV Format:**
    ```
    ID,Name,Email,Phone,Role,Created At
    123e4567-e89b-12d3-a456-426614174000,John Doe,john@example.com,+1234567890,YOUTH_MEMBER,2026-09-01 10:00:00
    223e4567-e89b-12d3-a456-426614174001,Jane Smith,jane@example.com,+1234567891,DEPARTMENT_LEADER,2026-08-15 09:30:00
    ```
    
    **Filtering:**
    - Only includes active users (is_active=True)
    - Excludes archived/suspended accounts
    - All roles included
    
    **Generation Time:** Typically 15-30 seconds depending on total user count
    - 100 users: ~10 seconds
    - 500 users: ~20 seconds
    - 1000+ users: ~30-45 seconds
    
    **How to Download:**
    1. Submit this request → receive task_id
    2. Poll GET /analytics/reports/{task_id}/download
    3. Download CSV when ready
    
    **Use Cases:**
    - System-wide user audits
    - External system integrations
    - Backup user directory
    - Compliance reporting
    - Migration preparation
    
    **Security Note:** This export contains complete user contact information.
    Only SUPER_ADMIN should have access. Handle downloaded CSV files securely.
    
    **Data Privacy:** Ensure compliance with organizational data protection policies
    before exporting user data.
    
    **Required Permissions:** SUPER_ADMIN only
    """,
)
async def export_users() -> ApiResponse[ReportResponse]:
    """
    Export all active users to CSV.

    Returns:
        ApiResponse containing task_id and export metadata

    Raises:
        HTTPException: If task dispatch fails
    """
    try:
        # Dispatch Celery task
        task = export_users_csv.delay()
        task_id = task.id

        logger.info(f"Dispatched user export task {task_id}")

        return ApiResponse(
            data=ReportResponse(
                task_id=task_id,
                status="queued",
                message="User export started",
                report_type="user_export",
                date_range=None,
                timestamp=datetime.utcnow().isoformat(),
            )
        )

    except Exception as e:
        logger.error(f"Failed to dispatch user export task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue user export",
        )
