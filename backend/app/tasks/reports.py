"""
Report Generation Background Tasks
Generates attendance, analytics, and financial reports with CSV export
"""

import csv
import io
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.models.attendance import AttendanceModel
from app.infrastructure.database.models.event import EventModel
from app.domain.value_objects.enums import AttendanceStatus, EventStatus

# Configure logging
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def generate_csv_from_data(headers: List[str], rows: List[List]) -> str:
    """Generate CSV content from headers and rows"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()


async def get_attendance_data(
    session: AsyncSession, start_date: datetime, end_date: datetime
) -> List[tuple]:
    """Fetch attendance records for date range"""
    query = (
        select(AttendanceModel, UserModel.name, UserModel.email, EventModel.title)
        .join(UserModel, AttendanceModel.user_id == UserModel.id)
        .outerjoin(EventModel, AttendanceModel.event_id == EventModel.id)
        .where(
            and_(
                AttendanceModel.check_in_time >= start_date,
                AttendanceModel.check_in_time < end_date,
            )
        )
        .order_by(AttendanceModel.check_in_time.desc())
    )

    result = await session.execute(query)
    return result.all()


# ═══════════════════════════════════════════════════════════════════════════
# REPORT GENERATION TASKS
# ═══════════════════════════════════════════════════════════════════════════


@celery_app.task(name="app.tasks.reports.generate_daily_attendance_report", bind=True)
def generate_daily_attendance_report(
    self, date: Optional[str] = None, send_email: bool = False
) -> Dict:
    """
    Generate daily attendance report

    Args:
        date: ISO format date (defaults to today)
        send_email: Whether to email the report

    Returns:
        Dict with report stats and CSV content
    """
    import asyncio

    async def _generate():
        try:
            # Parse date or use today
            if date:
                report_date = datetime.fromisoformat(date).date()
            else:
                report_date = datetime.utcnow().date()

            logger.info(f"Generating daily attendance report for {report_date}")

            start_time = datetime.combine(report_date, datetime.min.time())
            end_time = start_time + timedelta(days=1)

            async with AsyncSessionLocal() as session:
                # Get attendance data
                attendance_records = await get_attendance_data(
                    session, start_time, end_time
                )

                # Prepare CSV data
                headers = [
                    "User Name",
                    "Email",
                    "Event",
                    "Check In Time",
                    "Check Out Time",
                    "Status",
                    "Duration (minutes)",
                ]

                rows = []
                total_present = 0
                total_absent = 0
                total_late = 0

                for record, user_name, user_email, event_title in attendance_records:
                    duration = None
                    if record.check_out_time and record.check_in_time:
                        duration = int(
                            (
                                record.check_out_time - record.check_in_time
                            ).total_seconds()
                            / 60
                        )

                    rows.append(
                        [
                            user_name,
                            user_email,
                            event_title or "N/A",
                            (
                                record.check_in_time.strftime("%Y-%m-%d %H:%M:%S")
                                if record.check_in_time
                                else ""
                            ),
                            (
                                record.check_out_time.strftime("%Y-%m-%d %H:%M:%S")
                                if record.check_out_time
                                else ""
                            ),
                            (
                                record.status.value
                                if hasattr(record.status, "value")
                                else str(record.status)
                            ),
                            duration or "",
                        ]
                    )

                    # Count statuses
                    if record.status == AttendanceStatus.PRESENT:
                        total_present += 1
                    elif record.status == AttendanceStatus.ABSENT:
                        total_absent += 1
                    elif record.status == AttendanceStatus.LATE:
                        total_late += 1

                # Generate CSV
                csv_content = generate_csv_from_data(headers, rows)

                logger.info(
                    f"Daily report generated: {len(rows)} records, "
                    f"{total_present} present, {total_absent} absent, {total_late} late"
                )

                # TODO: Upload CSV to cloud storage (Cloudinary/S3)
                # TODO: Send email if requested

                return {
                    "status": "completed",
                    "date": report_date.isoformat(),
                    "total_records": len(rows),
                    "present": total_present,
                    "absent": total_absent,
                    "late": total_late,
                    "csv_size": len(csv_content),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as exc:
            logger.error(f"Failed to generate daily report: {str(exc)}")
            raise

    return asyncio.run(_generate())


@celery_app.task(name="app.tasks.reports.generate_weekly_analytics", bind=True)
def generate_weekly_analytics(self, week_offset: int = 0) -> Dict:
    """
    Generate weekly analytics report

    Args:
        week_offset: Weeks before current week (0 = current week, 1 = last week)

    Returns:
        Dict with weekly analytics
    """
    import asyncio

    async def _generate():
        try:
            # Calculate week date range
            today = datetime.utcnow().date()
            start_of_week = today - timedelta(days=today.weekday() + (week_offset * 7))
            end_of_week = start_of_week + timedelta(days=7)

            logger.info(
                f"Generating weekly analytics for {start_of_week} to {end_of_week}"
            )

            async with AsyncSessionLocal() as session:
                # Get attendance statistics
                attendance_query = select(
                    func.count(AttendanceModel.id).label("total_attendance"),
                    func.count(func.distinct(AttendanceModel.user_id)).label(
                        "unique_users"
                    ),
                    func.avg(
                        func.extract(
                            "epoch",
                            AttendanceModel.check_out_time
                            - AttendanceModel.check_in_time,
                        )
                        / 60
                    ).label("avg_duration"),
                ).where(
                    and_(
                        AttendanceModel.check_in_time
                        >= datetime.combine(start_of_week, datetime.min.time()),
                        AttendanceModel.check_in_time
                        < datetime.combine(end_of_week, datetime.min.time()),
                    )
                )

                result = await session.execute(attendance_query)
                stats = result.first()

                # Get top attendees
                top_attendees_query = (
                    select(
                        UserModel.name,
                        func.count(AttendanceModel.id).label("attendance_count"),
                    )
                    .join(AttendanceModel, UserModel.id == AttendanceModel.user_id)
                    .where(
                        and_(
                            AttendanceModel.check_in_time
                            >= datetime.combine(start_of_week, datetime.min.time()),
                            AttendanceModel.check_in_time
                            < datetime.combine(end_of_week, datetime.min.time()),
                        )
                    )
                    .group_by(UserModel.id, UserModel.name)
                    .order_by(func.count(AttendanceModel.id).desc())
                    .limit(10)
                )

                top_result = await session.execute(top_attendees_query)
                top_attendees = [
                    {"name": name, "count": count} for name, count in top_result.all()
                ]

                # Get events count
                events_query = select(func.count(EventModel.id)).where(
                    and_(
                        EventModel.start_time
                        >= datetime.combine(start_of_week, datetime.min.time()),
                        EventModel.start_time
                        < datetime.combine(end_of_week, datetime.min.time()),
                        EventModel.status == EventStatus.COMPLETED,
                    )
                )

                events_result = await session.execute(events_query)
                total_events = events_result.scalar() or 0

                logger.info(
                    f"Weekly analytics generated: {stats.total_attendance} attendance records"
                )

                return {
                    "status": "completed",
                    "week_start": start_of_week.isoformat(),
                    "week_end": end_of_week.isoformat(),
                    "total_attendance": stats.total_attendance or 0,
                    "unique_users": stats.unique_users or 0,
                    "avg_duration_minutes": (
                        round(stats.avg_duration, 2) if stats.avg_duration else 0
                    ),
                    "total_events": total_events,
                    "top_attendees": top_attendees,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as exc:
            logger.error(f"Failed to generate weekly analytics: {str(exc)}")
            raise

    return asyncio.run(_generate())


@celery_app.task(name="app.tasks.reports.generate_monthly_financial_report", bind=True)
def generate_monthly_financial_report(self, month: Optional[str] = None) -> Dict:
    """
    Generate monthly financial report (pledges, payments)

    Args:
        month: Month in YYYY-MM format (defaults to current month)

    Returns:
        Dict with financial statistics
    """
    import asyncio

    async def _generate():
        try:
            # Parse month or use current
            if month:
                report_month = datetime.strptime(month, "%Y-%m").date()
            else:
                today = datetime.utcnow().date()
                report_month = today.replace(day=1)

            # Calculate month date range
            datetime.combine(report_month, datetime.min.time())
            if report_month.month == 12:
                datetime.combine(
                    report_month.replace(year=report_month.year + 1, month=1),
                    datetime.min.time(),
                )
            else:
                datetime.combine(
                    report_month.replace(month=report_month.month + 1),
                    datetime.min.time(),
                )

            logger.info(
                f"Generating monthly financial report for {report_month.strftime('%B %Y')}"
            )

            async with AsyncSessionLocal():
                # TODO: Implement financial queries when pledge models are available
                # For now, return placeholder data

                logger.info(
                    f"Monthly financial report generated for {report_month.strftime('%B %Y')}"
                )

                return {
                    "status": "completed",
                    "month": report_month.strftime("%Y-%m"),
                    "month_name": report_month.strftime("%B %Y"),
                    "total_pledges": 0,  # TODO: Implement
                    "total_paid": 0,  # TODO: Implement
                    "total_pending": 0,  # TODO: Implement
                    "payment_rate": 0,  # TODO: Implement
                    "timestamp": datetime.utcnow().isoformat(),
                    "note": "Financial reporting requires pledge/payment models to be implemented",
                }

        except Exception as exc:
            logger.error(f"Failed to generate monthly financial report: {str(exc)}")
            raise

    return asyncio.run(_generate())


@celery_app.task(name="app.tasks.reports.generate_custom_report", bind=True)
def generate_custom_report(
    self, start_date: str, end_date: str, report_type: str = "attendance"
) -> Dict:
    """
    Generate custom report for specific date range

    Args:
        start_date: ISO format start date
        end_date: ISO format end date
        report_type: Type of report (attendance, events, users)

    Returns:
        Dict with report data and CSV
    """
    import asyncio

    async def _generate():
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)

            logger.info(
                f"Generating custom {report_type} report from {start_date} to {end_date}"
            )

            async with AsyncSessionLocal() as session:
                if report_type == "attendance":
                    # Get attendance data
                    attendance_records = await get_attendance_data(session, start, end)

                    headers = ["User", "Event", "Check In", "Check Out", "Status"]
                    rows = [
                        [
                            user_name,
                            event_title or "N/A",
                            (
                                record.check_in_time.strftime("%Y-%m-%d %H:%M")
                                if record.check_in_time
                                else ""
                            ),
                            (
                                record.check_out_time.strftime("%Y-%m-%d %H:%M")
                                if record.check_out_time
                                else ""
                            ),
                            str(record.status),
                        ]
                        for record, user_name, _, event_title in attendance_records
                    ]

                    csv_content = generate_csv_from_data(headers, rows)

                    return {
                        "status": "completed",
                        "report_type": report_type,
                        "start_date": start_date,
                        "end_date": end_date,
                        "total_records": len(rows),
                        "csv_size": len(csv_content),
                        "csv_content": csv_content,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Report type '{report_type}' not implemented yet",
                    }

        except Exception as exc:
            logger.error(f"Failed to generate custom report: {str(exc)}")
            raise

    return asyncio.run(_generate())


@celery_app.task(name="app.tasks.reports.export_users_csv")
def export_users_csv(self) -> Dict:
    """Export all active users to CSV"""
    import asyncio

    async def _export():
        try:
            logger.info("Exporting users to CSV")

            async with AsyncSessionLocal() as session:
                query = select(UserModel).where(UserModel.is_active is True)
                result = await session.execute(query)
                users = result.scalars().all()

                headers = ["ID", "Name", "Email", "Phone", "Role", "Created At"]
                rows = [
                    [
                        str(user.id),
                        user.name,
                        user.email,
                        user.phone or "",
                        str(user.role),
                        user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    ]
                    for user in users
                ]

                csv_content = generate_csv_from_data(headers, rows)

                logger.info(f"Exported {len(users)} users to CSV")

                return {
                    "status": "completed",
                    "total_users": len(users),
                    "csv_size": len(csv_content),
                    "csv_content": csv_content,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as exc:
            logger.error(f"Failed to export users: {str(exc)}")
            raise

    return asyncio.run(_export())
