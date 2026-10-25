"""
Youth Repository Implementation (Infrastructure Layer)
SQLAlchemy implementation of IYouthRepository
"""

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.youth import YouthModel
from app.infrastructure.database.models.attendance import AttendanceModel
from app.infrastructure.database.models.event import EventModel
from app.domain.value_objects.enums import MembershipStatus


class YouthRepository:
    """SQLAlchemy implementation of youth repository."""

    async def get_by_id(self, youth_id: str, db: AsyncSession) -> YouthModel | None:
        """Get youth by ID with branch and department loaded."""
        result = await db.execute(
            select(YouthModel)
            .options(
                selectinload(YouthModel.branch), selectinload(YouthModel.department)
            )
            .where(YouthModel.id == youth_id)
        )
        return result.scalar_one_or_none()

    async def list_by_branch(
        self, branch_id: str | None, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[YouthModel], int]:
        """List youths in a specific branch with pagination."""
        # Get total count
        # Build count query conditionally
        count_query = select(func.count()).select_from(YouthModel).where(
            YouthModel.membership_status == MembershipStatus.ACTIVE
        )
        if branch_id is not None:
            count_query = count_query.where(YouthModel.branch_id == branch_id)
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()

        # Get paginated results
        # Build list query conditionally
        list_query = (
            select(YouthModel)
            .options(
                selectinload(YouthModel.branch), selectinload(YouthModel.department)
            )
            .where(YouthModel.membership_status == MembershipStatus.ACTIVE)
        )
        if branch_id is not None:
            list_query = list_query.where(YouthModel.branch_id == branch_id)
        
        list_query = list_query.offset(offset).limit(limit).order_by(YouthModel.created_at.desc())
        result = await db.execute(list_query)
        youths = result.scalars().all()
        return list(youths), total

    async def list_by_department(
        self, department_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[YouthModel], int]:
        """List youths in a specific department with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count())
            .select_from(YouthModel)
            .where(
                YouthModel.department_id == department_id,
                YouthModel.membership_status == MembershipStatus.ACTIVE,
            )
        )
        total = count_result.scalar()

        # Get paginated results
        result = await db.execute(
            select(YouthModel)
            .options(
                selectinload(YouthModel.branch), selectinload(YouthModel.department)
            )
            .where(
                YouthModel.department_id == department_id,
                YouthModel.membership_status == MembershipStatus.ACTIVE,
            )
            .offset(offset)
            .limit(limit)
            .order_by(YouthModel.created_at.desc())
        )
        youths = result.scalars().all()
        return list(youths), total

    async def save(self, youth: YouthModel, db: AsyncSession) -> YouthModel:
        """Create or update a youth."""
        db.add(youth)
        await db.flush()
        await db.refresh(youth)
        return youth

    async def delete(self, youth_id: str, db: AsyncSession) -> bool:
        """Delete a youth (soft delete by setting membership_status=INACTIVE)."""
        result = await db.execute(
            update(YouthModel)
            .where(YouthModel.id == youth_id)
            .values(membership_status=MembershipStatus.INACTIVE)
        )
        await db.flush()
        return result.rowcount > 0

    async def search(
        self,
        query: str,
        branch_id: str | None,
        offset: int,
        limit: int,
        db: AsyncSession,
    ) -> tuple[list[YouthModel], int]:
        """
        Search youths by name or email with full-text search.
        If branch_id is provided, limit search to that branch.
        """
        # Build search condition
        search_condition = or_(
            YouthModel.fullname.ilike(f"%{query}%"),
            YouthModel.email.ilike(f"%{query}%"),
        )

        # Add branch filter if provided
        conditions = [
            search_condition,
            YouthModel.membership_status == MembershipStatus.ACTIVE,
        ]
        if branch_id:
            conditions.append(YouthModel.branch_id == branch_id)

        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(YouthModel).where(*conditions)
        )
        total = count_result.scalar()

        # Get paginated results
        result = await db.execute(
            select(YouthModel)
            .options(
                selectinload(YouthModel.branch), selectinload(YouthModel.department)
            )
            .where(*conditions)
            .offset(offset)
            .limit(limit)
            .order_by(YouthModel.created_at.desc())
        )
        youths = result.scalars().all()
        return list(youths), total

    async def get_attendance_history(
        self, youth_id: str, limit: int, db: AsyncSession
    ) -> list[dict]:
        """
        Get attendance history for a youth.

        Returns list of dicts with:
        - event_id: str
        - event_title: str
        - attended_at: datetime
        - status: str
        """
        result = await db.execute(
            select(AttendanceModel, EventModel)
            .join(EventModel, AttendanceModel.event_id == EventModel.id)
            .where(AttendanceModel.youth_id == youth_id)
            .order_by(AttendanceModel.check_in_time.desc())
            .limit(limit)
        )

        attendance_history = []
        for attendance, event in result.all():
            attendance_history.append(
                {
                    "event_id": event.id,
                    "event_title": event.title,
                    "attended_at": attendance.check_in_time,
                    "status": attendance.status,
                }
            )

        return attendance_history

    async def update_avatar(
        self, youth_id: str, avatar_url: str, db: AsyncSession
    ) -> bool:
        """Update youth avatar/profile image URL."""
        result = await db.execute(
            update(YouthModel)
            .where(YouthModel.id == youth_id)
            .values(profile_image_url=avatar_url)
        )
        await db.flush()
        return result.rowcount > 0

    async def count_by_branch(self, branch_id: str, db: AsyncSession) -> int:
        """Count youths in a branch."""
        result = await db.execute(
            select(func.count())
            .select_from(YouthModel)
            .where(
                YouthModel.branch_id == branch_id,
                YouthModel.membership_status == MembershipStatus.ACTIVE,
            )
        )
        return result.scalar()


def get_youth_repository() -> YouthRepository:
    """Factory function for dependency injection."""
    return YouthRepository()
