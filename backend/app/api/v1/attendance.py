"""Attendance API Router"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, status
from app.api.deps import CurrentUserDep, DbSessionDep, require_role
from app.api.schemas.attendance import *
from app.api.schemas.responses import ApiResponse
from app.application.services.attendance_service import (
    AttendanceService,
    get_attendance_service,
)
from app.tasks.reports import generate_daily_attendance_report
from app.domain.value_objects.enums import Role

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("", response_model=ApiResponse[AttendanceResponse])
async def record_attendance(
    data: AttendanceRecordRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: AttendanceService = Depends(get_attendance_service),
):
    """
    Record single attendance entry.

    **Protected Endpoint** (Authentication required)

    **Business Rules:**
    - Creates attendance record for youth at event
    - Auto-sets check-in time to current timestamp
    - Status defaults to PRESENT

    **Request Body:**
    - event_id: UUID of the event
    - youth_id: UUID of the youth member

    **Returns:**
    - 200: Attendance recorded successfully
    - 404: Event or youth not found
    """
    attendance = await service.record_single(data.event_id, data.youth_id, db)
    return ApiResponse(data=AttendanceResponse.from_orm(attendance))


@router.post("/bulk", response_model=ApiResponse[dict])
async def record_bulk_attendance(
    data: BulkAttendanceRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    generate_report: bool = False,
    service: AttendanceService = Depends(get_attendance_service),
):
    """
    Record attendance for multiple youths at once.

    **Protected Endpoint** (Authentication required)

    **Business Rules:**
    - Batch creates attendance records for list of youths
    - More efficient than multiple single calls
    - All attendances recorded with same timestamp
    - Optional automatic report generation after recording

    **Request Body:**
    - event_id: UUID of the event
    - youth_ids: List of youth UUIDs (1-100 max)

    **Query Parameters:**
    - generate_report: If true, auto-generates daily report after bulk recording

    **Returns:**
    - 200: Bulk attendance recorded successfully
    - 400: Validation error (empty list, invalid IDs)

    **Use Case:**
    Event coordinator checks in multiple youths at event start using tablet/app.
    """
    attendances = await service.record_bulk(data.event_id, data.youth_ids, db)

    # Optional: Auto-generate report after bulk recording
    report_task_id = None
    if generate_report:
        try:
            today = datetime.utcnow().date().isoformat()
            task = generate_daily_attendance_report.delay(date=today, send_email=False)
            report_task_id = task.id
            logger.info(
                f"Auto-generated attendance report task {report_task_id} after bulk recording"
            )
        except Exception as e:
            logger.warning(f"Failed to auto-generate report after bulk recording: {e}")

    return ApiResponse(
        data={
            "recorded_count": len(attendances),
            "attendances": [AttendanceResponse.from_orm(a) for a in attendances],
            "report_task_id": report_task_id,
            "message": f"Successfully recorded {len(attendances)} attendance entries",
        }
    )


@router.get("/summary", response_model=ApiResponse[AttendanceSummaryResponse])
async def get_summary(
    branch_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    service: AttendanceService = Depends(get_attendance_service),
):
    """
    Get attendance summary statistics for a branch.

    **Protected Endpoint** (Authentication required)

    **Query Parameters:**
    - branch_id: UUID of the branch (required)
    - start_date: Optional start date for summary period
    - end_date: Optional end date for summary period

    **Returns:**
    - total_events: Number of events in period
    - total_attendances: Total attendance records
    - unique_youths: Number of unique youths who attended
    - attendance_rate: Percentage attendance rate

    **Use Case:**
    Branch coordinators view attendance metrics for reporting and analysis.
    """
    summary = await service.generate_summary(branch_id, start_date, end_date, db)
    return ApiResponse(data=AttendanceSummaryResponse(**summary))


@router.post(
    "/reports/generate",
    response_model=ApiResponse[AttendanceReportResponse],
    dependencies=[Depends(require_role([Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN]))],
)
async def generate_attendance_report(
    data: AttendanceReportRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
):
    """
    Generate daily attendance report (CSV export).

    **Protected Endpoint** (BRANCH_COORDINATOR, SUPER_ADMIN only)

    **Business Rules:**
    - Generates comprehensive CSV report of attendance records
    - Includes: user names, emails, events, check-in/out times, durations
    - Can be auto-emailed to coordinators
    - Report generation runs asynchronously via Celery

    **Request Body:**
    - date: ISO format date (optional, defaults to today)
    - send_email: Boolean flag to email report (default: false)

    **Returns:**
    - task_id: Celery task ID for tracking report generation
    - status: "queued" or "error"
    - message: Status message
    - date: Date of report
    - timestamp: When task was queued

    **Report Contents:**
    - User Name
    - Email
    - Event
    - Check In Time
    - Check Out Time
    - Status
    - Duration (minutes)

    **Use Case:**
    - Daily report generation for record-keeping
    - Weekly/monthly attendance analysis
    - Audit trail for attendance records
    - Export for external reporting systems

    **Performance:**
    - Report generation typically takes 1-3 minutes for 1000 records
    - Use task_id to check status via /api/v1/tasks/{task_id} endpoint
    - Download CSV via /api/v1/analytics/reports/{task_id}/download

    **Example:**
    ```
    POST /api/v1/attendance/reports/generate
    {
        "date": "2024-01-15",
        "send_email": true
    }
    ```
    """
    report_date = data.date or datetime.utcnow().date().isoformat()

    task_id = None
    try:
        task = generate_daily_attendance_report.delay(
            date=report_date, send_email=data.send_email
        )
        task_id = task.id
        logger.info(
            f"Dispatched attendance report generation task {task_id} for date {report_date}"
        )
        status_str = "queued"
        message = f"Attendance report generation started for {report_date}"
    except Exception as e:
        logger.error(f"Failed to dispatch attendance report task: {e}")
        status_str = "error"
        message = "Failed to queue report generation"

    return ApiResponse(
        data=AttendanceReportResponse(
            task_id=task_id,
            status=status_str,
            message=message,
            date=report_date,
            timestamp=datetime.utcnow().isoformat(),
        )
    )


@router.get("/stats", response_model=ApiResponse[AttendanceSummaryResponse])
async def get_stats(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    service: AttendanceService = Depends(get_attendance_service),
):
    """
    Get attendance statistics (alias for summary without branch filter).
    Returns overall attendance stats across all branches.
    """
    # Get overall stats (no branch filter)
    summary = await service.generate_summary(None, start_date, end_date, db)
    return ApiResponse(data=AttendanceSummaryResponse(**summary))
    present_result = await db.execute(
        select(func.count(AttendanceModel.id)).where(
            AttendanceModel.status == AttendanceStatus.PRESENT
        )
    )
    present = present_result.scalar_one()
    
    # Calculate rate
    rate = (present / total * 100) if total > 0 else 0.0
    
    return ApiResponse(
        data={
            "total": total,
            "present": present,
            "rate": round(rate, 2),
            "absent": total - present
        }
    )
