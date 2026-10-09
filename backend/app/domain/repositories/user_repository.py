"""
User Repository Interface (Domain Layer)
Abstract protocol for user data access operations
"""

from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.user import UserModel


class IUserRepository(Protocol):
    """
    User repository interface defining data access contract.
    
    Implementations must handle all CRUD operations and user-specific queries.
    """
    
    async def create(self, user_data: dict, db: AsyncSession) -> UserModel:
        """
        Create a new user.
        
        Args:
            user_data: Dictionary containing user fields
            db: Database session
            
        Returns:
            Created UserModel instance
        """
        ...
    
    async def get_by_id(self, user_id: str, db: AsyncSession) -> UserModel | None:
        """Get user by ID."""
        ...
    
    async def get_by_email(self, email: str, db: AsyncSession) -> UserModel | None:
        """Get user by email address."""
        ...
    
    async def get_by_phone(self, phone: str, db: AsyncSession) -> UserModel | None:
        """Get user by phone number."""
        ...
    
    async def list_by_branch(
        self, 
        branch_id: str,
        offset: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[UserModel], int]:
        """List users in a specific branch with pagination."""
        ...
    
    async def list_by_role(
        self, 
        role: str,
        offset: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[UserModel], int]:
        """List users by role with pagination."""
        ...
    
    async def update(self, user_id: str, updates: dict, db: AsyncSession) -> UserModel:
        """Update user fields."""
        ...
    
    async def update_password(self, user_id: str, hashed_password: str, db: AsyncSession) -> bool:
        """Update user password."""
        ...
    
    async def update_email_verified(self, user_id: str, verified: bool, db: AsyncSession) -> bool:
        """Update email verification status."""
        ...
    
    async def delete(self, user_id: str, db: AsyncSession) -> bool:
        """Soft delete user (set is_active = False)."""
        ...
    
    async def count_by_branch(self, branch_id: str, db: AsyncSession) -> int:
        """Count users in a branch."""
        ...
