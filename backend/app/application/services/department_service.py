"""
Department Management Service (Application Layer)
Business logic for department operations
"""

from uuid import uuid4
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.repositories.department_repository import (
    DepartmentRepository,
    get_department_repository,
)
from app.infrastructure.repositories.branch_repository import (
    BranchRepository,
    get_branch_repository,
)
from app.infrastructure.repositories.user_repository import (
    UserRepository,
    get_user_repository,
)
from app.infrastructure.database.models.department import DepartmentModel
from app.domain.value_objects.enums import Role


class DepartmentService:
    """Department management business logic service."""

    def __init__(
        self,
        dept_repo: DepartmentRepository = Depends(get_department_repository),
        branch_repo: BranchRepository = Depends(get_branch_repository),
        user_repo: UserRepository = Depends(get_user_repository),
    ):
        self.dept_repo = dept_repo
        self.branch_repo = branch_repo
        self.user_repo = user_repo

    async def create_department(
        self, name: str, branch_id: str, description: str | None, db: AsyncSession
    ) -> DepartmentModel:
        """Create a new department."""
        # Validate branch exists
        branch = await self.branch_repo.get_by_id(branch_id, db)
        if not branch:
            raise NotFoundException(f"Branch {branch_id} not found")

        department = DepartmentModel(
            id=str(uuid4()),
            name=name,
            branch_id=branch_id,
            description=description,
            is_active=True,
        )

        return await self.dept_repo.save(department, db)

    async def get_department(self, dept_id: str, db: AsyncSession) -> DepartmentModel:
        """Get department by ID."""
        dept = await self.dept_repo.get_by_id(dept_id, db)
        if not dept:
            raise NotFoundException(f"Department {dept_id} not found")
        return dept

    async def list_departments(
        self, branch_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[DepartmentModel], int]:
        """List departments in a branch with pagination."""
        return await self.dept_repo.list_by_branch(branch_id, offset, limit, db)

    async def update_department(
        self, dept_id: str, updates: dict, db: AsyncSession
    ) -> DepartmentModel:
        """Update department details."""
        dept = await self.get_department(dept_id, db)

        # Apply updates
        for key, value in updates.items():
            if hasattr(dept, key):
                setattr(dept, key, value)

        return await self.dept_repo.save(dept, db)

    async def delete_department(self, dept_id: str, db: AsyncSession) -> bool:
        """Soft delete a department."""
        dept = await self.get_department(dept_id, db)
        return await self.dept_repo.delete(dept_id, db)

    async def assign_leader(
        self, dept_id: str, leader_id: str, db: AsyncSession
    ) -> DepartmentModel:
        """
        Assign a leader to a department.

        Business rules:
        - Leader must have DEPARTMENT_LEADER role
        """
        # Validate department exists
        dept = await self.get_department(dept_id, db)

        # Validate leader exists and has correct role
        leader = await self.user_repo.get_by_id(leader_id, db)
        if not leader:
            raise NotFoundException(f"User {leader_id} not found")

        if leader.role != Role.DEPARTMENT_LEADER.value:
            raise ValidationException("User must have DEPARTMENT_LEADER role")

        # Ensure leader is in same branch as department
        if leader.branch_id != dept.branch_id:
            raise ValidationException(
                "Leader must be in the same branch as the department"
            )

        return await self.dept_repo.assign_leader(dept_id, leader_id, db)

    async def add_members(
        self, dept_id: str, user_ids: list[str], db: AsyncSession
    ) -> int:
        """
        Add multiple members to a department.

        Returns count of members added.
        """
        dept = await self.get_department(dept_id, db)

        count = 0
        for user_id in user_ids:
            # Validate user exists and is in same branch
            user = await self.user_repo.get_by_id(user_id, db)
            if not user:
                continue

            if user.branch_id != dept.branch_id:
                continue

            success = await self.dept_repo.add_member(dept_id, user_id, db)
            if success:
                count += 1

        return count

    async def remove_members(
        self, dept_id: str, user_id: str, db: AsyncSession
    ) -> bool:
        """Remove a member from a department."""
        dept = await self.get_department(dept_id, db)
        return await self.dept_repo.remove_member(dept_id, user_id, db)

    async def update_schedule(
        self, dept_id: str, schedule: dict, db: AsyncSession
    ) -> bool:
        """Update department meeting schedule."""
        dept = await self.get_department(dept_id, db)
        return await self.dept_repo.update_schedule(dept_id, schedule, db)


def get_department_service(
    dept_repo: DepartmentRepository = Depends(get_department_repository),
    branch_repo: BranchRepository = Depends(get_branch_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> DepartmentService:
    """Factory function for dependency injection."""
    return DepartmentService(dept_repo, branch_repo, user_repo)
