"""Attendance Service"""
from datetime import datetime
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.attendance_repository import AttendanceRepository, get_attendance_repository
from app.infrastructure.database.models.attendance import AttendanceModel


class AttendanceService:
    def __init__(
        self, attendance_repo: AttendanceRepository = Depends(get_attendance_repository)
    ):
        self.attendance_repo = attendance_repo
    
    async def record_single(
        self, event_id: str, youth_id: str, db: AsyncSession
    ) -> AttendanceModel:
        return await self.attendance_repo.record_attendance(event_id, youth_id, db)
    
    async def record_bulk(
        self, event_id: str, youth_ids: list[str], db: AsyncSession
    ) -> list[AttendanceModel]:
        return await self.attendance_repo.bulk_record(event_id, youth_ids, db)
    
    async def get_event_attendance(
        self, event_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[AttendanceModel], int]:
        return await self.attendance_repo.get_by_event(event_id, offset, limit, db)
    
    async def get_youth_attendance(
        self, youth_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[AttendanceModel], int]:
        return await self.attendance_repo.get_by_youth(youth_id, offset, limit, db)
    
    async def generate_summary(
        self, branch_id: str, start_date: datetime | None,
        end_date: datetime | None, db: AsyncSession
    ) -> dict:
        return await self.attendance_repo.get_summary(branch_id, start_date, end_date, db)
    
    async def generate_heatmap(
        self, branch_id: str, start_date: datetime,
        end_date: datetime, db: AsyncSession
    ) -> list[dict]:
        return await self.attendance_repo.generate_heatmap(branch_id, start_date, end_date, db)


def get_attendance_service(
    attendance_repo: AttendanceRepository = Depends(get_attendance_repository)
) -> AttendanceService:
    return AttendanceService(attendance_repo)
