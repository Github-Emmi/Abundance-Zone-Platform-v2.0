"""
Notification Repository Interface (Domain Layer)
Abstract protocol for notification data access operations
"""

from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.notification import NotificationModel


class INotificationRepository(Protocol):
    """
    Notification repository interface defining data access contract.
    
    Implementations must handle CRUD operations and broadcast functionality.
    """
    
    async def create(
        self,
        notification_data: dict,
        db: AsyncSession
    ) -> NotificationModel:
        """Create a notification."""
        ...
    
    async def list_by_user(
        self,
        user_id: str,
        offset: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[NotificationModel], int]:
        """List notifications for a user with pagination."""
        ...
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str,
        db: AsyncSession
    ) -> bool:
        """Mark a notification as read."""
        ...
    
    async def mark_all_as_read(
        self,
        user_id: str,
        db: AsyncSession
    ) -> int:
        """
        Mark all notifications for a user as read.
        Returns count of notifications marked.
        """
        ...
    
    async def delete(
        self,
        notification_id: str,
        user_id: str,
        db: AsyncSession
    ) -> bool:
        """Delete a notification (user can only delete their own)."""
        ...
    
    async def count_unread(
        self,
        user_id: str,
        db: AsyncSession
    ) -> int:
        """Count unread notifications for a user."""
        ...
    
    async def broadcast_to_branch(
        self,
        branch_id: str,
        notification_data: dict,
        db: AsyncSession
    ) -> int:
        """
        Broadcast notification to all users in a branch.
        Returns count of notifications created.
        """
        ...
