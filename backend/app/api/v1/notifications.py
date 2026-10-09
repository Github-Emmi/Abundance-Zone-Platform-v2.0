"""Notification API Router"""
from fastapi import APIRouter, Depends
from app.api.deps import CurrentUserDep, DbSessionDep
from app.api.schemas.notification import *
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.responses import ApiResponse, PaginatedResponse
from app.application.services.notification_service import NotificationService, get_notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=ApiResponse[PaginatedResponse[NotificationResponse]])
async def list_notifications(
    current_user: CurrentUserDep, db: DbSessionDep,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: NotificationService = Depends(get_notification_service)
):
    notifs, total = await service.list_user_notifications(
        current_user.id, pagination.offset, pagination.limit, db
    )
    items = [NotificationResponse.from_orm(n) for n in notifs]
    return ApiResponse(data=PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size,
        has_next=(pagination.page * pagination.page_size) < total
    ))

@router.post("/{notif_id}/read", response_model=ApiResponse[dict])
async def mark_as_read(
    notif_id: str, current_user: CurrentUserDep, db: DbSessionDep,
    service: NotificationService = Depends(get_notification_service)
):
    success = await service.mark_as_read(notif_id, current_user.id, db)
    return ApiResponse(data={"success": success})

@router.post("/read-all", response_model=ApiResponse[dict])
async def mark_all_as_read(
    current_user: CurrentUserDep, db: DbSessionDep,
    service: NotificationService = Depends(get_notification_service)
):
    count = await service.mark_all_as_read(current_user.id, db)
    return ApiResponse(data={"count": count})
