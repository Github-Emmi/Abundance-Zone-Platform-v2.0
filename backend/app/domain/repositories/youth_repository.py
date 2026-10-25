"""
Youth Repository Interface (Domain Layer)
Abstract protocol for youth data access operations
"""

from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.youth import YouthModel


class IYouthRepository(Protocol):
    """
    Youth repository interface defining data access contract.

    Implementations must handle CRUD operations, search, and attendance history.
    """

    async def get_by_id(self, youth_id: str, db: AsyncSession) -> YouthModel | None:
        """Get youth by ID."""
        ...

    async def list_by_branch(
        self, branch_id: str | None, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[YouthModel], int]:
        """List youths in a specific branch with pagination."""
        ...

    async def list_by_department(
        self, department_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[YouthModel], int]:
        """List youths in a specific department with pagination."""
        ...

    async def save(self, youth: YouthModel, db: AsyncSession) -> YouthModel:
        """Create or update a youth."""
        ...

    async def delete(self, youth_id: str, db: AsyncSession) -> bool:
        """Delete a youth (soft delete by setting membership_status=INACTIVE)."""
        ...

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
        ...

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
        ...

    async def update_avatar(
        self, youth_id: str, avatar_url: str, db: AsyncSession
    ) -> bool:
        """Update youth avatar/profile image URL."""
        ...

    async def count_by_branch(self, branch_id: str, db: AsyncSession) -> int:
        """Count youths in a branch."""
        ...
