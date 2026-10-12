"""
Branch Repository Interface (Domain Layer)
Abstract protocol for branch data access operations
"""

from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.branch import BranchModel


class IBranchRepository(Protocol):
    """
    Branch repository interface defining data access contract.

    Implementations must handle CRUD operations and branch-specific queries.
    """

    async def get_by_id(self, branch_id: str, db: AsyncSession) -> BranchModel | None:
        """Get branch by ID."""
        ...

    async def find_by_name(self, name: str, db: AsyncSession) -> BranchModel | None:
        """Find branch by name."""
        ...

    async def list_all(
        self, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[BranchModel], int]:
        """List all branches with pagination."""
        ...

    async def save(self, branch: BranchModel, db: AsyncSession) -> BranchModel:
        """Create or update a branch."""
        ...

    async def delete(self, branch_id: str, db: AsyncSession) -> bool:
        """Delete a branch (soft delete by setting is_active=False)."""
        ...

    async def assign_coordinator(
        self, branch_id: str, coordinator_id: str, db: AsyncSession
    ) -> BranchModel:
        """Assign a coordinator to a branch."""
        ...

    async def get_with_statistics(self, branch_id: str, db: AsyncSession) -> dict:
        """
        Get branch with calculated statistics.

        Returns dict with:
        - branch: BranchModel
        - youth_count: int
        - department_count: int
        - attendance_rate: float
        """
        ...

    async def count_active(self, db: AsyncSession) -> int:
        """Count active branches."""
        ...
