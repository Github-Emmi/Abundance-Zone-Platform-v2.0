"""
Branch Management Service (Application Layer)
Business logic for branch operations
"""

from uuid import uuid4
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.repositories.branch_repository import (
    BranchRepository,
    get_branch_repository,
)
from app.infrastructure.repositories.user_repository import (
    UserRepository,
    get_user_repository,
)
from app.infrastructure.database.models.branch import BranchModel
from app.domain.value_objects.enums import Role


class BranchService:
    """Branch management business logic service."""

    def __init__(
        self,
        branch_repo: BranchRepository = Depends(get_branch_repository),
        user_repo: UserRepository = Depends(get_user_repository),
    ):
        self.branch_repo = branch_repo
        self.user_repo = user_repo

    async def create_branch(
        self,
        name: str,
        location: str,
        address: str | None,
        phone: str | None,
        description: str | None,
        db: AsyncSession,
    ) -> BranchModel:
        """
        Create a new branch.

        Business rules:
        - Branch name must be unique
        - Only SUPER_ADMIN can create branches
        """
        # Check if branch name already exists
        existing = await self.branch_repo.find_by_name(name, db)
        if existing:
            raise ValidationException(f"Branch with name '{name}' already exists")

        branch = BranchModel(
            id=str(uuid4()),
            name=name,
            location=location,
            address=address,
            phone=phone,
            description=description,
            is_active=True,
        )

        return await self.branch_repo.save(branch, db)

    async def get_branch(self, branch_id: str, db: AsyncSession) -> BranchModel:
        """Get branch by ID."""
        branch = await self.branch_repo.get_by_id(branch_id, db)
        if not branch:
            raise NotFoundException(f"Branch {branch_id} not found")
        return branch

    async def list_branches(
        self, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[BranchModel], int]:
        """List all active branches with pagination."""
        return await self.branch_repo.list_all(offset, limit, db)

    async def update_branch(
        self, branch_id: str, updates: dict, db: AsyncSession
    ) -> BranchModel:
        """
        Update branch details.

        Business rules:
        - Cannot change branch name to one that already exists
        """
        branch = await self.get_branch(branch_id, db)

        # If updating name, check uniqueness
        if "name" in updates and updates["name"] != branch.name:
            existing = await self.branch_repo.find_by_name(updates["name"], db)
            if existing:
                raise ValidationException(
                    f"Branch with name '{updates['name']}' already exists"
                )

        # Apply updates
        for key, value in updates.items():
            if hasattr(branch, key):
                setattr(branch, key, value)

        return await self.branch_repo.save(branch, db)

    async def delete_branch(self, branch_id: str, db: AsyncSession) -> bool:
        """
        Soft delete a branch.

        Business rules:
        - Only SUPER_ADMIN can delete branches
        - Deletion is soft (sets is_active=False)
        """
        await self.get_branch(branch_id, db)
        return await self.branch_repo.delete(branch_id, db)

    async def assign_coordinator(
        self, branch_id: str, coordinator_id: str, db: AsyncSession
    ) -> BranchModel:
        """
        Assign a coordinator to a branch.

        Business rules:
        - Coordinator must have BRANCH_COORDINATOR role
        - Coordinator can only be assigned to one branch
        """
        # Validate branch exists
        await self.get_branch(branch_id, db)

        # Validate coordinator exists and has correct role
        coordinator = await self.user_repo.get_by_id(coordinator_id, db)
        if not coordinator:
            raise NotFoundException(f"User {coordinator_id} not found")

        if coordinator.role != Role.BRANCH_COORDINATOR.value:
            raise ValidationException("User must have BRANCH_COORDINATOR role")

        return await self.branch_repo.assign_coordinator(branch_id, coordinator_id, db)

    async def get_statistics(self, branch_id: str, db: AsyncSession) -> dict:
        """
        Get branch statistics.

        Returns:
        - branch: BranchModel
        - youth_count: int
        - department_count: int
        - attendance_rate: float
        """
        return await self.branch_repo.get_with_statistics(branch_id, db)


def get_branch_service(
    branch_repo: BranchRepository = Depends(get_branch_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> BranchService:
    """Factory function for dependency injection."""
    return BranchService(branch_repo, user_repo)
