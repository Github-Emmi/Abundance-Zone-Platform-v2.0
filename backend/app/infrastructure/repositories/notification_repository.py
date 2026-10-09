"""
Notification Repository Implementation (Infrastructure Layer)
SQLAlchemy implementation of INotificationRepository
"""

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.notification import NotificationModel
from app.infrastructure.database.models.user import UserModel


class NotificationRepository:
    """SQLAlchemy implementation of notification repository."""
    
    async def create(
        self,
        notification_data: dict,
        db: AsyncSession
    ) -> NotificationModel:
        """Create a notification."""
        from uuid import uuid4
        notification = NotificationModel(
            id=str(uuid4()),
            **notification_data
        )
        db.add(notification)
        await db.flush()
        await db.refresh(notification)
        return notification
    
    async def list_by_user(
        self,
        user_id: str,
        offset: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[NotificationModel], int]:
        """List notifications for a user with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(NotificationModel).where(
                NotificationModel.user_id == user_id
            )
        )
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .offset(offset)
            .limit(limit)
            .order_by(NotificationModel.created_at.desc())
        )
        notifications = result.scalars().all()
        return list(notifications), total
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str,
        db: AsyncSession
    ) -> bool:
        """Mark a notification as read."""
        from datetime import datetime, timezone
        result = await db.execute(
            update(NotificationModel)
            .where(
                NotificationModel.id == notification_id,
                NotificationModel.user_id == user_id
            )
            .values(read_at=datetime.now(timezone.utc))
        )
        await db.flush()
        return result.rowcount > 0
    
    async def mark_all_as_read(
        self,
        user_id: str,
        db: AsyncSession
    ) -> int:
        """
        Mark all notifications for a user as read.
        Returns count of notifications marked.
        """
        from datetime import datetime, timezone
        result = await db.execute(
            update(NotificationModel)
            .where(
                NotificationModel.user_id == user_id,
                NotificationModel.read_at.is_(None)
            )
            .values(read_at=datetime.now(timezone.utc))
        )
        await db.flush()
        return result.rowcount
    
    async def delete(
        self,
        notification_id: str,
        user_id: str,
        db: AsyncSession
    ) -> bool:
        """Delete a notification (user can only delete their own)."""
        result = await db.execute(
            select(NotificationModel).where(
                NotificationModel.id == notification_id,
                NotificationModel.user_id == user_id
            )
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        await db.delete(notification)
        await db.flush()
        return True
    
    async def count_unread(
        self,
        user_id: str,
        db: AsyncSession
    ) -> int:
        """Count unread notifications for a user."""
        result = await db.execute(
            select(func.count()).select_from(NotificationModel).where(
                NotificationModel.user_id == user_id,
                NotificationModel.read_at.is_(None)
            )
        )
        return result.scalar()
    
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
        # Get all users in the branch
        result = await db.execute(
            select(UserModel.id).where(
                UserModel.branch_id == branch_id,
                UserModel.is_active == True
            )
        )
        user_ids = result.scalars().all()
        
        # Create notification for each user
        from uuid import uuid4
        notifications = []
        for user_id in user_ids:
            notification = NotificationModel(
                id=str(uuid4()),
                user_id=user_id,
                **notification_data
            )
            notifications.append(notification)
            db.add(notification)
        
        await db.flush()
        return len(notifications)


def get_notification_repository() -> NotificationRepository:
    """Factory function for dependency injection."""
    return NotificationRepository()
