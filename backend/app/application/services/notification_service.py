"""Notification Service"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.notification_repository import NotificationRepository, get_notification_repository
from app.infrastructure.database.models.notification import NotificationModel
from app.domain.value_objects.enums import NotificationType, NotificationChannel


class NotificationService:
    def __init__(
        self, notif_repo: NotificationRepository = Depends(get_notification_repository)
    ):
        self.notif_repo = notif_repo
    
    async def create_notification(
        self, user_id: str, title: str, content: str,
        notif_type: NotificationType, channel: NotificationChannel,
        db: AsyncSession
    ) -> NotificationModel:
        data = {
            "user_id": user_id, "title": title, "content": content,
            "type": notif_type, "channel": channel
        }
        return await self.notif_repo.create(data, db)
    
    async def list_user_notifications(
        self, user_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[NotificationModel], int]:
        return await self.notif_repo.list_by_user(user_id, offset, limit, db)
    
    async def mark_as_read(
        self, notification_id: str, user_id: str, db: AsyncSession
    ) -> bool:
        return await self.notif_repo.mark_as_read(notification_id, user_id, db)
    
    async def mark_all_as_read(self, user_id: str, db: AsyncSession) -> int:
        return await self.notif_repo.mark_all_as_read(user_id, db)
    
    async def delete_notification(
        self, notification_id: str, user_id: str, db: AsyncSession
    ) -> bool:
        return await self.notif_repo.delete(notification_id, user_id, db)
    
    async def broadcast_to_branch(
        self, branch_id: str, title: str, content: str,
        notif_type: NotificationType, db: AsyncSession
    ) -> int:
        data = {
            "title": title, "content": content, "type": notif_type,
            "channel": NotificationChannel.IN_APP
        }
        return await self.notif_repo.broadcast_to_branch(branch_id, data, db)
    
    async def broadcast_to_department(
        self, department_id: str, title: str, content: str,
        notif_type: NotificationType, db: AsyncSession
    ) -> int:
        # Placeholder - would need department member query
        return 0


def get_notification_service(
    notif_repo: NotificationRepository = Depends(get_notification_repository)
) -> NotificationService:
    return NotificationService(notif_repo)
