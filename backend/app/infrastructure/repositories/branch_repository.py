"""
Branch Repository Implementation (Infrastructure Layer)
SQLAlchemy implementation of IBranchRepository
"""

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.infrastructure.database.models.branch import BranchModel
from app.infrastructure.database.models.youth import YouthModel
from app.infrastructure.database.models.department import DepartmentModel


class BranchRepository:
    """SQLAlchemy implementation of branch repository."""
    
    async def get_by_id(self, branch_id: str, db: AsyncSession) -> BranchModel | None:
        """Get branch by ID with coordinator loaded."""
        result = await db.execute(
            select(BranchModel)
            .options(selectinload(BranchModel.coordinator))
            .where(BranchModel.id == branch_id)
        )
        return result.scalar_one_or_none()
    
    async def find_by_name(self, name: str, db: AsyncSession) -> BranchModel | None:
        """Find branch by name."""
        result = await db.execute(
            select(BranchModel).where(BranchModel.name == name)
        )
        return result.scalar_one_or_none()
    
    async def list_all(
        self,
        offset: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[BranchModel], int]:
        """List all branches with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(BranchModel).where(BranchModel.is_active == True)
        )
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            select(BranchModel)
            .options(selectinload(BranchModel.coordinator))
            .where(BranchModel.is_active == True)
            .offset(offset)
            .limit(limit)
            .order_by(BranchModel.created_at.desc())
        )
        branches = result.scalars().all()
        return list(branches), total
    
    async def save(self, branch: BranchModel, db: AsyncSession) -> BranchModel:
        """Create or update a branch."""
        db.add(branch)
        await db.flush()
        await db.refresh(branch)
        return branch
    
    async def delete(self, branch_id: str, db: AsyncSession) -> bool:
        """Delete a branch (soft delete by setting is_active=False)."""
        result = await db.execute(
            update(BranchModel)
            .where(BranchModel.id == branch_id)
            .values(is_active=False)
        )
        await db.flush()
        return result.rowcount > 0
    
    async def assign_coordinator(
        self,
        branch_id: str,
        coordinator_id: str,
        db: AsyncSession
    ) -> BranchModel:
        """Assign a coordinator to a branch."""
        branch = await self.get_by_id(branch_id, db)
        if not branch:
            raise NotFoundException(f"Branch {branch_id} not found")
        
        branch.coordinator_id = coordinator_id
        await db.flush()
        await db.refresh(branch)
        return branch
    
    async def get_with_statistics(
        self,
        branch_id: str,
        db: AsyncSession
    ) -> dict:
        """
        Get branch with calculated statistics.
        
        Returns dict with:
        - branch: BranchModel
        - youth_count: int
        - department_count: int
        - attendance_rate: float
        """
        branch = await self.get_by_id(branch_id, db)
        if not branch:
            raise NotFoundException(f"Branch {branch_id} not found")
        
        # Count youths
        youth_count_result = await db.execute(
            select(func.count()).select_from(YouthModel).where(YouthModel.branch_id == branch_id)
        )
        youth_count = youth_count_result.scalar()
        
        # Count departments
        dept_count_result = await db.execute(
            select(func.count()).select_from(DepartmentModel).where(
                DepartmentModel.branch_id == branch_id,
                DepartmentModel.is_active == True
            )
        )
        department_count = dept_count_result.scalar()
        
        # Calculate attendance rate (avg of all youths' attendance rates)
        attendance_rate_result = await db.execute(
            select(func.avg(YouthModel.attendance_rate)).where(YouthModel.branch_id == branch_id)
        )
        attendance_rate = attendance_rate_result.scalar() or 0.0
        
        return {
            "branch": branch,
            "youth_count": youth_count,
            "department_count": department_count,
            "attendance_rate": float(attendance_rate)
        }
    
    async def count_active(self, db: AsyncSession) -> int:
        """Count active branches."""
        result = await db.execute(
            select(func.count()).select_from(BranchModel).where(BranchModel.is_active == True)
        )
        return result.scalar()


def get_branch_repository() -> BranchRepository:
    """Factory function for dependency injection."""
    return BranchRepository()
