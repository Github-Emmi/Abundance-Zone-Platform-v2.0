"""
Department Repository Interface (Domain Layer)
Abstract protocol for department data access operations
"""

from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.department import DepartmentModel
from app.infrastructure.database.models.user import UserModel


class IDepartmentRepository(Protocol):
    """
    Department repository interface defining data access contract.
    
    Implementations must handle CRUD operations, member management, and schedules.
    """
    
    async def get_by_id(self, dept_id: str, db: AsyncSession) -> DepartmentModel | None:
        """Get department by ID."""
        ...
    
    async def list_by_branch(
        self,
        branch_id: str,
        offset: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[DepartmentModel], int]:
        """List departments in a specific branch with pagination."""
        ...
    
    async def save(self, department: DepartmentModel, db: AsyncSession) -> DepartmentModel:
        """Create or update a department."""
        ...
    
    async def delete(self, dept_id: str, db: AsyncSession) -> bool:
        """Delete a department (soft delete by setting is_active=False)."""
        ...
    
    async def assign_leader(
        self,
        dept_id: str,
        leader_id: str,
        db: AsyncSession
    ) -> DepartmentModel:
        """Assign a leader to a department."""
        ...
    
    async def add_member(
        self,
        dept_id: str,
        user_id: str,
        db: AsyncSession
    ) -> bool:
        """Add a member to a department."""
        ...
    
    async def remove_member(
        self,
        dept_id: str,
        user_id: str,
        db: AsyncSession
    ) -> bool:
        """Remove a member from a department."""
        ...
    
    async def get_members(
        self,
        dept_id: str,
        offset: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[UserModel], int]:
        """Get department members with pagination."""
        ...
    
    async def get_schedule(self, dept_id: str, db: AsyncSession) -> dict | None:
        """Get department meeting schedule (JSONB field)."""
        ...
    
    async def update_schedule(
        self,
        dept_id: str,
        schedule: dict,
        db: AsyncSession
    ) -> bool:
        """Update department meeting schedule."""
        ...
