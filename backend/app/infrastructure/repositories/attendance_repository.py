"""
Attendance Repository Implementation (Infrastructure Layer)
SQLAlchemy implementation of IAttendanceRepository
"""

from datetime import datetime
from sqlalchemy import func, select, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError

from app.infrastructure.database.models.attendance import AttendanceModel
from app.infrastructure.database.models.event import EventModel
from app.infrastructure.database.models.youth import YouthModel
from app.domain.value_objects.enums import AttendanceStatus


class AttendanceRepository:
    """SQLAlchemy implementation of attendance repository."""

    async def record_attendance(
        self, event_id: str, youth_id: str, db: AsyncSession
    ) -> AttendanceModel:
        """
        Record attendance for a youth at an event.
        Should be idempotent (duplicate check-ins return existing record).
        """
        # Check if attendance already exists
        result = await db.execute(
            select(AttendanceModel).where(
                AttendanceModel.event_id == event_id,
                AttendanceModel.youth_id == youth_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Already checked in, return existing record
            return existing

        # Create new attendance record
        from uuid import uuid4

        attendance = AttendanceModel(
            id=str(uuid4()),
            event_id=event_id,
            youth_id=youth_id,
            status=AttendanceStatus.CHECKED_IN,
            check_in_time=datetime.utcnow(),
        )

        db.add(attendance)
        try:
            await db.flush()
            await db.refresh(attendance)
        except IntegrityError:
            # Race condition - record was created between check and insert
            await db.rollback()
            result = await db.execute(
                select(AttendanceModel).where(
                    AttendanceModel.event_id == event_id,
                    AttendanceModel.youth_id == youth_id,
                )
            )
            attendance = result.scalar_one()

        return attendance

    async def bulk_record(
        self, event_id: str, youth_ids: list[str], db: AsyncSession
    ) -> list[AttendanceModel]:
        """Record attendance for multiple youths at once."""
        attendances = []

        for youth_id in youth_ids:
            attendance = await self.record_attendance(event_id, youth_id, db)
            attendances.append(attendance)

        return attendances

    async def get_by_event(
        self, event_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[AttendanceModel], int]:
        """Get attendance records for an event with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count())
            .select_from(AttendanceModel)
            .where(AttendanceModel.event_id == event_id)
        )
        total = count_result.scalar()

        # Get paginated results
        result = await db.execute(
            select(AttendanceModel)
            .options(
                selectinload(AttendanceModel.youth), selectinload(AttendanceModel.event)
            )
            .where(AttendanceModel.event_id == event_id)
            .offset(offset)
            .limit(limit)
            .order_by(AttendanceModel.check_in_time.desc())
        )
        attendances = result.scalars().all()
        return list(attendances), total

    async def get_by_youth(
        self, youth_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[AttendanceModel], int]:
        """Get attendance records for a youth with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count())
            .select_from(AttendanceModel)
            .where(AttendanceModel.youth_id == youth_id)
        )
        total = count_result.scalar()

        # Get paginated results
        result = await db.execute(
            select(AttendanceModel)
            .options(
                selectinload(AttendanceModel.youth), selectinload(AttendanceModel.event)
            )
            .where(AttendanceModel.youth_id == youth_id)
            .offset(offset)
            .limit(limit)
            .order_by(AttendanceModel.check_in_time.desc())
        )
        attendances = result.scalars().all()
        return list(attendances), total

    async def get_summary(
        self,
        branch_id: str,
        start_date: datetime | None,
        end_date: datetime | None,
        db: AsyncSession,
    ) -> dict:
        """
        Get attendance summary for a branch.

        Returns dict with:
        - total_events: int
        - total_attendances: int
        - unique_youths: int
        - attendance_rate: float (0.0-100.0)
        """
        conditions = [EventModel.branch_id == branch_id]
        if start_date:
            conditions.append(EventModel.event_date >= start_date)
        if end_date:
            conditions.append(EventModel.event_date <= end_date)

        # Count total events
        event_count_result = await db.execute(
            select(func.count()).select_from(EventModel).where(and_(*conditions))
        )
        total_events = event_count_result.scalar()

        # Count total attendances and unique youths
        attendance_result = await db.execute(
            select(
                func.count(AttendanceModel.id).label("total_attendances"),
                func.count(func.distinct(AttendanceModel.youth_id)).label(
                    "unique_youths"
                ),
            )
            .select_from(AttendanceModel)
            .join(EventModel, AttendanceModel.event_id == EventModel.id)
            .where(and_(*conditions))
        )
        row = attendance_result.one()
        total_attendances = row.total_attendances
        unique_youths = row.unique_youths

        # Calculate attendance rate
        # Rate = (total attendances) / (total events * total branch youths) * 100
        youth_count_result = await db.execute(
            select(func.count())
            .select_from(YouthModel)
            .where(YouthModel.branch_id == branch_id)
        )
        total_youths = youth_count_result.scalar()

        if total_events > 0 and total_youths > 0:
            attendance_rate = (total_attendances / (total_events * total_youths)) * 100
        else:
            attendance_rate = 0.0

        return {
            "total_events": total_events,
            "total_attendances": total_attendances,
            "unique_youths": unique_youths,
            "attendance_rate": float(attendance_rate),
        }

    async def generate_heatmap(
        self, branch_id: str, start_date: datetime, end_date: datetime, db: AsyncSession
    ) -> list[dict]:
        """
        Generate attendance heatmap data.

        Returns list of dicts with:
        - date: str (YYYY-MM-DD)
        - count: int (number of attendances that day)
        """
        result = await db.execute(
            select(
                func.date(AttendanceModel.check_in_time).label("date"),
                func.count(AttendanceModel.id).label("count"),
            )
            .select_from(AttendanceModel)
            .join(EventModel, AttendanceModel.event_id == EventModel.id)
            .where(
                EventModel.branch_id == branch_id,
                AttendanceModel.check_in_time >= start_date,
                AttendanceModel.check_in_time <= end_date,
            )
            .group_by(func.date(AttendanceModel.check_in_time))
            .order_by(func.date(AttendanceModel.check_in_time))
        )

        heatmap_data = []
        for row in result:
            heatmap_data.append({"date": str(row.date), "count": row.count})

        return heatmap_data

    async def calculate_rate(
        self,
        youth_id: str | None,
        branch_id: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
        db: AsyncSession,
    ) -> float:
        """
        Calculate attendance rate as percentage.
        Can calculate for a specific youth or entire branch.
        """
        if youth_id:
            # Calculate for specific youth
            event_conditions = []
            if start_date:
                event_conditions.append(EventModel.event_date >= start_date)
            if end_date:
                event_conditions.append(EventModel.event_date <= end_date)

            # Count total events the youth could attend
            youth_result = await db.execute(
                select(YouthModel).where(YouthModel.id == youth_id)
            )
            youth = youth_result.scalar_one_or_none()
            if not youth:
                return 0.0

            event_conditions.append(EventModel.branch_id == youth.branch_id)

            event_count_result = await db.execute(
                select(func.count())
                .select_from(EventModel)
                .where(and_(*event_conditions))
            )
            total_events = event_count_result.scalar()

            # Count attendances
            attendance_conditions = [AttendanceModel.youth_id == youth_id]
            if start_date or end_date:
                attendance_conditions.append(
                    select(EventModel.id)
                    .where(and_(*event_conditions))
                    .scalar_subquery()
                    .in_([AttendanceModel.event_id])
                )

            attendance_count_result = await db.execute(
                select(func.count())
                .select_from(AttendanceModel)
                .where(and_(*attendance_conditions))
            )
            attendances = attendance_count_result.scalar()

            if total_events > 0:
                return (attendances / total_events) * 100
            return 0.0

        elif branch_id:
            # Calculate for entire branch
            summary = await self.get_summary(branch_id, start_date, end_date, db)
            return summary["attendance_rate"]

        return 0.0


def get_attendance_repository() -> AttendanceRepository:
    """Factory function for dependency injection."""
    return AttendanceRepository()
