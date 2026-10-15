"""
Attendance Repository Interface (Domain Layer)
Abstract protocol for attendance data access operations
"""

from typing import Protocol
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.attendance import AttendanceModel


class IAttendanceRepository(Protocol):
    """
    Attendance repository interface defining data access contract.

    Implementations must handle recording, bulk operations, and analytics.
    """

    async def record_attendance(
        self, event_id: str, youth_id: str, db: AsyncSession
    ) -> AttendanceModel:
        """
        Record attendance for a youth at an event.
        Should be idempotent (duplicate check-ins return existing record).
        """
        ...

    async def bulk_record(
        self, event_id: str, youth_ids: list[str], db: AsyncSession
    ) -> list[AttendanceModel]:
        """Record attendance for multiple youths at once."""
        ...

    async def get_by_event(
        self, event_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[AttendanceModel], int]:
        """Get attendance records for an event with pagination."""
        ...

    async def get_by_youth(
        self, youth_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[AttendanceModel], int]:
        """Get attendance records for a youth with pagination."""
        ...

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
        ...

    async def generate_heatmap(
        self, branch_id: str, start_date: datetime, end_date: datetime, db: AsyncSession
    ) -> list[dict]:
        """
        Generate attendance heatmap data.

        Returns list of dicts with:
        - date: str (YYYY-MM-DD)
        - count: int (number of attendances that day)
        """
        ...

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
        ... 
