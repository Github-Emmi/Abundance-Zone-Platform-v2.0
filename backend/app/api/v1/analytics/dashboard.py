"""
Dashboard Analytics API Endpoints

Provides real-time analytics and statistics for the Super Admin Dashboard.
All endpoints return aggregated data with proper error handling and correct PostgreSQL GROUP BY syntax.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.api.deps import CurrentUserDep, DbSessionDep, require_role
from app.api.schemas.responses import ApiResponse
from app.infrastructure.database.models import (
    YouthModel,
    EventModel,
    AttendanceModel,
    BranchModel,
    DepartmentModel,
    PaymentModel,
    PledgeModel
)
from app.domain.value_objects.enums import Role, AttendanceStatus, EventStatus, PledgeStatus
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["Dashboard Analytics"])


# Response Models
class DashboardSummary(BaseModel):
    total_revenue: float
    youth_growth_percent: float
    revenue_growth_percent: float
    attendance_change_percent: float


class YouthGrowthData(BaseModel):
    month: str
    count: int
    date: str


class AttendanceTrendData(BaseModel):
    date: str
    present: int
    absent: int
    rate: float


class RevenueSummaryData(BaseModel):
    total_revenue: float
    pledges_fulfilled: int = 0
    outstanding_payments: int = 0
    monthly_breakdown: List[Dict[str, Any]]
    growth_rate: float


class ActivityItem(BaseModel):
    id: str
    type: str
    description: str
    timestamp: datetime
    user: str
    metadata: Dict[str, Any] = {}


class SystemAlert(BaseModel):
    id: str
    severity: str
    title: str
    message: str
    timestamp: datetime
    acknowledged: bool = False


@router.get(
    "/summary",
    response_model=ApiResponse[DashboardSummary],
    dependencies=[Depends(require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]))],
)
async def get_dashboard_summary(
    current_user: CurrentUserDep,
    db: DbSessionDep,
):
    """Get overall dashboard summary statistics."""
    
    now = datetime.utcnow()
    last_month_start = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
    current_month_start = now.replace(day=1)
    
    # Get total revenue
    total_revenue_result = await db.execute(
        select(func.coalesce(func.sum(PaymentModel.amount), 0.0))
    )
    total_revenue = float(total_revenue_result.scalar_one())
    
    # Youth growth
    youth_this_month = await db.execute(
        select(func.count(YouthModel.id)).where(
            YouthModel.created_at >= current_month_start
        )
    )
    youth_last_month = await db.execute(
        select(func.count(YouthModel.id)).where(
            and_(
                YouthModel.created_at >= last_month_start,
                YouthModel.created_at < current_month_start
            )
        )
    )
    
    this_month_count = youth_this_month.scalar_one()
    last_month_count = youth_last_month.scalar_one()
    youth_growth = (
        ((this_month_count - last_month_count) / last_month_count * 100)
        if last_month_count > 0 else 0.0
    )
    
    # Revenue growth
    revenue_this_month = await db.execute(
        select(func.coalesce(func.sum(PaymentModel.amount), 0.0)).where(
            PaymentModel.created_at >= current_month_start
        )
    )
    revenue_last_month = await db.execute(
        select(func.coalesce(func.sum(PaymentModel.amount), 0.0)).where(
            and_(
                PaymentModel.created_at >= last_month_start,
                PaymentModel.created_at < current_month_start
            )
        )
    )
    
    this_month_revenue = float(revenue_this_month.scalar_one())
    last_month_revenue = float(revenue_last_month.scalar_one())
    revenue_growth = (
        ((this_month_revenue - last_month_revenue) / last_month_revenue * 100)
        if last_month_revenue > 0 else 0.0
    )
    
    # Attendance rate change
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)
    
    recent_attendance = await db.execute(
        select(
            func.count(AttendanceModel.id).filter(AttendanceModel.status == AttendanceStatus.PRESENT).label("present"),
            func.count(AttendanceModel.id).label("total")
        ).where(AttendanceModel.created_at >= thirty_days_ago)
    )
    
    prev_attendance = await db.execute(
        select(
            func.count(AttendanceModel.id).filter(AttendanceModel.status == AttendanceStatus.PRESENT).label("present"),
            func.count(AttendanceModel.id).label("total")
        ).where(
            and_(
                AttendanceModel.created_at >= sixty_days_ago,
                AttendanceModel.created_at < thirty_days_ago
            )
        )
    )
    
    recent = recent_attendance.one()
    prev = prev_attendance.one()
    
    recent_rate = (recent.present / recent.total * 100) if recent.total > 0 else 0.0
    prev_rate = (prev.present / prev.total * 100) if prev.total > 0 else 0.0
    attendance_change = recent_rate - prev_rate
    
    return ApiResponse(
        data=DashboardSummary(
            total_revenue=total_revenue,
            youth_growth_percent=round(youth_growth, 2),
            revenue_growth_percent=round(revenue_growth, 2),
            attendance_change_percent=round(attendance_change, 2),
        )
    )


@router.get(
    "/youth-growth",
    response_model=ApiResponse[List[YouthGrowthData]],
    dependencies=[Depends(require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]))],
)
async def get_youth_growth(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    months: int = Query(default=6, ge=1, le=12),
):
    """Get youth growth data by month."""
    
    now = datetime.utcnow()
    start_date = now - timedelta(days=months * 30)
    
    # Use text() for raw SQL to ensure PostgreSQL compatibility
    query = text("""
        SELECT 
            date_trunc('month', created_at) as month,
            COUNT(id) as count
        FROM youths
        WHERE created_at >= :start_date
        GROUP BY date_trunc('month', created_at)
        ORDER BY month
    """)
    
    result = await db.execute(query, {"start_date": start_date})
    rows = result.all()
    
    data = [
        YouthGrowthData(
            month=row.month.strftime("%b %Y") if row.month else "Unknown",
            count=row.count,
            date=row.month.isoformat() if row.month else ""
        )
        for row in rows
    ]
    
    return ApiResponse(data=data)


@router.get(
    "/attendance-trends",
    response_model=ApiResponse[List[AttendanceTrendData]],
    dependencies=[Depends(require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]))],
)
async def get_attendance_trends(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    days: int = Query(default=30, ge=7, le=90),
):
    """Get attendance trends by day."""
    
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)
    
    query = text("""
        SELECT 
            date_trunc('day', created_at) as date,
            COUNT(CASE WHEN status = 'PRESENT' THEN 1 END) as present,
            COUNT(CASE WHEN status = 'ABSENT' THEN 1 END) as absent
        FROM attendance
        WHERE created_at >= :start_date
        GROUP BY date_trunc('day', created_at)
        ORDER BY date
    """)
    
    result = await db.execute(query, {"start_date": start_date})
    rows = result.all()
    
    data = [
        AttendanceTrendData(
            date=row.date.isoformat() if row.date else "",
            present=row.present or 0,
            absent=row.absent or 0,
            rate=round((row.present / (row.present + row.absent) * 100), 2) 
                if (row.present + row.absent) > 0 else 0.0
        )
        for row in rows
    ]
    
    return ApiResponse(data=data)


@router.get(
    "/revenue-summary",
    response_model=ApiResponse[RevenueSummaryData],
    dependencies=[Depends(require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]))],
)
async def get_revenue_summary(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    months: int = Query(default=12, ge=1, le=24),
):
    """Get revenue summary by month."""
    
    now = datetime.utcnow()
    start_date = now - timedelta(days=months * 30)
    
    query = text("""
        SELECT 
            date_trunc('month', created_at) as month,
            COALESCE(SUM(amount), 0.0) as total
        FROM payments
        WHERE created_at >= :start_date
        GROUP BY date_trunc('month', created_at)
        ORDER BY month
    """)
    
    result = await db.execute(query, {"start_date": start_date})
    rows = result.all()
    
    total_revenue = sum(float(row.total) for row in rows)
    monthly_breakdown = [
        {
            "month": row.month.strftime("%b %Y") if row.month else "Unknown",
            "revenue": float(row.total),
            "pledges": 0,
            "payments": 0
        }
        for row in rows
    ]
    
    growth_rate = 0.0
    if len(rows) >= 2:
        last_month = float(rows[-1].total)
        prev_month = float(rows[-2].total)
        if prev_month > 0:
            growth_rate = ((last_month - prev_month) / prev_month * 100)
    
    return ApiResponse(
        data=RevenueSummaryData(
            total_revenue=float(total_revenue),
            pledges_fulfilled=0,
            outstanding_payments=0,
            monthly_breakdown=monthly_breakdown,
            growth_rate=round(growth_rate, 2)
        )
    )


@router.get(
    "/recent-activity",
    response_model=ApiResponse[List[ActivityItem]],
    dependencies=[Depends(require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]))],
)
async def get_recent_activity(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get recent platform activity."""
    
    query = select(YouthModel).order_by(YouthModel.created_at.desc()).limit(limit)
    result = await db.execute(query)
    youths = result.scalars().all()
    
    activities = [
        ActivityItem(
            id=str(youth.id),
            type="youth_registration",
            description=f"New youth registered: {youth.fullname}",
            timestamp=youth.created_at,
            user="System",
            metadata={"youth_id": str(youth.id), "branch_id": str(youth.branch_id) if youth.branch_id else None}
        )
        for youth in youths
    ]
    
    return ApiResponse(data=activities)


@router.get(
    "/alerts",
    response_model=ApiResponse[List[SystemAlert]],
    dependencies=[Depends(require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]))],
)
async def get_system_alerts(
    current_user: CurrentUserDep,
    db: DbSessionDep,
):
    """Get system alerts and notifications."""
    
    alerts = []
    now = datetime.utcnow()
    
    # Check for upcoming events
    upcoming_events = await db.execute(
        select(func.count(EventModel.id)).where(
            and_(
                EventModel.event_date >= now,
                EventModel.event_date <= now + timedelta(days=7),
                EventModel.status == EventStatus.SCHEDULED
            )
        )
    )
    event_count = upcoming_events.scalar_one()
    
    if event_count > 0:
        alerts.append(
            SystemAlert(
                id="alert_upcoming_events",
                severity="info",
                title="Upcoming Events",
                message=f"{event_count} event(s) scheduled in the next 7 days",
                timestamp=now
            )
        )
    
    # Check for overdue pledges
    overdue_pledges = await db.execute(
        select(func.count(PledgeModel.id)).where(
            and_(
                PledgeModel.due_date < now,
                PledgeModel.status != PledgeStatus.FULLY_PAID
            )
        )
    )
    overdue_count = overdue_pledges.scalar_one()
    
    if overdue_count > 0:
        alerts.append(
            SystemAlert(
                id="alert_overdue_pledges",
                severity="warning",
                title="Overdue Pledges",
                message=f"{overdue_count} pledge(s) are overdue",
                timestamp=now
            )
        )
    
    # Check for low attendance
    seven_days_ago = now - timedelta(days=7)
    recent_attendance = await db.execute(
        select(
            func.count(AttendanceModel.id).filter(AttendanceModel.status == AttendanceStatus.PRESENT).label("present"),
            func.count(AttendanceModel.id).label("total")
        ).where(AttendanceModel.created_at >= seven_days_ago)
    )
    att_result = recent_attendance.one()
    
    if att_result.total > 0:
        rate = (att_result.present / att_result.total * 100)
        if rate < 50:
            alerts.append(
                SystemAlert(
                    id="alert_low_attendance",
                    severity="error",
                    title="Low Attendance Alert",
                    message=f"Attendance rate is {rate:.1f}% in the last 7 days",
                    timestamp=now
                )
            )
    
    return ApiResponse(data=alerts)
