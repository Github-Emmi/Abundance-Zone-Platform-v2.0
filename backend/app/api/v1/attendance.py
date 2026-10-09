"""Attendance API Router"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from app.api.deps import CurrentUserDep, DbSessionDep
from app.api.schemas.attendance import *
from app.api.schemas.responses import ApiResponse
from app.application.services.attendance_service import AttendanceService, get_attendance_service

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.post("", response_model=ApiResponse[AttendanceResponse])
async def record_attendance(
    data: AttendanceRecordRequest, current_user: CurrentUserDep, db: DbSessionDep,
    service: AttendanceService = Depends(get_attendance_service)
):
    attendance = await service.record_single(data.event_id, data.youth_id, db)
    return ApiResponse(data=AttendanceResponse.from_orm(attendance))

@router.post("/bulk", response_model=ApiResponse[list[AttendanceResponse]])
async def record_bulk_attendance(
    data: BulkAttendanceRequest, current_user: CurrentUserDep, db: DbSessionDep,
    service: AttendanceService = Depends(get_attendance_service)
):
    attendances = await service.record_bulk(data.event_id, data.youth_ids, db)
    return ApiResponse(data=[AttendanceResponse.from_orm(a) for a in attendances])

@router.get("/summary", response_model=ApiResponse[AttendanceSummaryResponse])
async def get_summary(
    branch_id: str, current_user: CurrentUserDep, db: DbSessionDep,
    start_date: datetime | None = None, end_date: datetime | None = None,
    service: AttendanceService = Depends(get_attendance_service)
):
    summary = await service.generate_summary(branch_id, start_date, end_date, db)
    return ApiResponse(data=AttendanceSummaryResponse(**summary))
