"""
Department Repository Implementation (Infrastructure Layer)
SQLAlchemy implementation of IDepartmentRepository
"""

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.infrastructure.database.models.department import DepartmentModel
from app.infrastructure.database.models.user import UserModel


class DepartmentRepository:
    """SQLAlchemy implementation of department repository."""

    async def get_by_id(self, dept_id: str, db: AsyncSession) -> DepartmentModel | None:
        """Get department by ID with leader loaded."""
        result = await db.execute(
            select(DepartmentModel)
            .options(
                selectinload(DepartmentModel.leader),
                selectinload(DepartmentModel.branch),
            )
            .where(DepartmentModel.id == dept_id)
        )
        return result.scalar_one_or_none()

    async def list_by_branch(
        self, branch_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[DepartmentModel], int]:
        """List departments in a specific branch with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count())
            .select_from(DepartmentModel)
            .where(
                DepartmentModel.branch_id == branch_id,
                DepartmentModel.is_active.is_(True),
            )
        )
        total = count_result.scalar()

        # Get paginated results
        result = await db.execute(
            select(DepartmentModel)
            .options(
                selectinload(DepartmentModel.leader),
                selectinload(DepartmentModel.branch),
            )
            .where(
                DepartmentModel.branch_id == branch_id,
                DepartmentModel.is_active.is_(True),
            )
            .offset(offset)
            .limit(limit)
            .order_by(DepartmentModel.created_at.desc())
        )
        departments = result.scalars().all()
        return list(departments), total

    async def save(
        self, department: DepartmentModel, db: AsyncSession
    ) -> DepartmentModel:
        """Create or update a department."""
        db.add(department)
        await db.flush()
        await db.refresh(department)
        return department

    async def delete(self, dept_id: str, db: AsyncSession) -> bool:
        """Delete a department (soft delete by setting is_active=False)."""
        result = await db.execute(
            update(DepartmentModel)
            .where(DepartmentModel.id == dept_id)
            .values(is_active=False)
        )
        await db.flush()
        return result.rowcount > 0

    async def assign_leader(
        self, dept_id: str, leader_id: str, db: AsyncSession
    ) -> DepartmentModel:
        """Assign a leader to a department."""
        department = await self.get_by_id(dept_id, db)
        if not department:
            raise NotFoundException(f"Department {dept_id} not found")

        department.leader_id = leader_id
        await db.flush()
        await db.refresh(department)
        return department

    async def add_member(self, dept_id: str, user_id: str, db: AsyncSession) -> bool:
        """Add a member to a department."""
        # Update user's department_id
        result = await db.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(department_id=dept_id)
        )
        await db.flush()
        return result.rowcount > 0

    async def remove_member(self, dept_id: str, user_id: str, db: AsyncSession) -> bool:
        """Remove a member from a department."""
        # Set user's department_id to None
        result = await db.execute(
            update(UserModel)
            .where(UserModel.id == user_id, UserModel.department_id == dept_id)
            .values(department_id=None)
        )
        await db.flush()
        return result.rowcount > 0

    async def get_members(
        self, dept_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[UserModel], int]:
        """Get department members with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.department_id == dept_id)
        )
        total = count_result.scalar()

        # Get paginated results
        result = await db.execute(
            select(UserModel)
            .where(UserModel.department_id == dept_id)
            .offset(offset)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        members = result.scalars().all()
        return list(members), total

    async def get_schedule(self, dept_id: str, db: AsyncSession) -> dict | None:
        """Get department meeting schedule (JSONB field)."""
        department = await self.get_by_id(dept_id, db)
        if not department:
            return None
        # Assuming there's a schedule JSONB field in the model
        # If not present, return empty dict
        return getattr(department, "schedule", {})

    async def update_schedule(
        self, dept_id: str, schedule: dict, db: AsyncSession
    ) -> bool:
        """Update department meeting schedule."""
        department = await self.get_by_id(dept_id, db)
        if not department:
            return False

        # Assuming there's a schedule JSONB field
        # If not present in model, this will need to be added
        if hasattr(department, "schedule"):
            department.schedule = schedule
            await db.flush()
            return True
        return False


def get_department_repository() -> DepartmentRepository:
    """Factory function for dependency injection."""
    return DepartmentRepository()
