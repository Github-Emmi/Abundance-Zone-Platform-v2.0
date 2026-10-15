"""Notification API Router"""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from app.api.deps import CurrentUserDep, DbSessionDep, require_role, CurrentUser
from app.api.schemas.notification import *
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.responses import ApiResponse, PaginatedResponse
from app.application.services.notification_service import (
    NotificationService,
    get_notification_service,
)
from app.domain.value_objects.enums import Role
from app.tasks.notifications import (
    send_push_notification,
    send_bulk_notifications,
    send_topic_notification,
    subscribe_to_topic,
    unsubscribe_from_topic,
    send_scheduled_notification,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ═══════════════════════════════════════════════════════════════════════════
# USER NOTIFICATION ENDPOINTS (AUTHENTICATED USERS)
# ═══════════════════════════════════════════════════════════════════════════


@router.get("", response_model=ApiResponse[PaginatedResponse[NotificationResponse]])
async def list_notifications(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: NotificationService = Depends(get_notification_service),
):
    """
    List user's notifications with pagination.

    **Business Rules:**
    - Returns notifications for the authenticated user only
    - Ordered by creation date (newest first)
    - Supports pagination for efficient data loading
    - Returns both read and unread notifications
    """
    notifs, total = await service.list_user_notifications(
        current_user.id, pagination.offset, pagination.limit, db
    )
    items = [NotificationResponse.from_orm(n) for n in notifs]
    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=(pagination.page * pagination.page_size) < total,
        )
    )


@router.post("/{notif_id}/read", response_model=ApiResponse[dict])
async def mark_as_read(
    notif_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: NotificationService = Depends(get_notification_service),
):
    """
    Mark a single notification as read.

    **Business Rules:**
    - Only the notification owner can mark it as read
    - Sets read_at timestamp to current time
    - Idempotent operation (can be called multiple times)
    """
    success = await service.mark_as_read(notif_id, current_user.id, db)
    return ApiResponse(data={"success": success})


@router.post("/read-all", response_model=ApiResponse[dict])
async def mark_all_as_read(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: NotificationService = Depends(get_notification_service),
):
    """
    Mark all user notifications as read.

    **Business Rules:**
    - Marks all unread notifications for the current user
    - Returns count of notifications marked as read
    - Efficient bulk operation for clearing notification badge
    """
    count = await service.mark_all_as_read(current_user.id, db)
    return ApiResponse(data={"count": count})


# ═══════════════════════════════════════════════════════════════════════════
# PUSH NOTIFICATION ENDPOINTS (ADMIN ONLY)
# ═══════════════════════════════════════════════════════════════════════════


@router.post("/push", response_model=ApiResponse[dict])
async def send_push(
    request: PushNotificationRequest,
    _: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
):
    """
    Send push notification to a single device via Firebase Cloud Messaging.

    **Access Control:** SUPER_ADMIN only

    **Business Rules:**
    - Dispatches async Celery task for background processing
    - Returns task_id for monitoring via /tasks/{task_id} endpoint
    - Task retries automatically on transient failures (3 attempts)
    - Handles invalid/unregistered device tokens gracefully
    - Supports rich notifications with images
    - Supports custom data payload for deep linking

    **Use Cases:**
    - Send personalized notification to specific user
    - Deliver urgent alerts (payment confirmation, security alert)
    - Test notification delivery before bulk send

    **Error Handling:**
    - Graceful degradation if Celery is unavailable
    - Returns error status but does not block API response
    """
    try:
        task = send_push_notification.delay(
            device_token=request.device_token,
            title=request.title,
            body=request.body,
            data=request.data,
            image_url=request.image_url,
        )
        task_id = task.id
        logger.info(
            f"Dispatched push notification task {task_id} to {request.device_token}"
        )
        status = "queued"
        message = "Push notification queued for delivery"
    except Exception as e:
        logger.warning(f"Failed to dispatch push notification task: {e}")
        task_id = None
        status = "error"
        message = "Failed to queue notification - Celery may be unavailable"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status,
            "message": message,
            "device_token": request.device_token,
            "title": request.title,
        }
    )


@router.post("/bulk", response_model=ApiResponse[dict])
async def send_bulk(
    request: BulkNotificationRequest,
    _: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
):
    """
    Send push notifications to multiple devices in a single batch.

    **Access Control:** SUPER_ADMIN only

    **Business Rules:**
    - Maximum 500 device tokens per request (enforced by schema validation)
    - Dispatches async Celery task for background processing
    - Firebase processes batch efficiently (single API call)
    - Returns task_id for monitoring delivery status
    - Partial failures are handled gracefully (some succeed, some fail)
    - Invalid tokens are filtered and reported in task result

    **Use Cases:**
    - Broadcast announcements to branch members
    - Send event reminders to multiple attendees
    - Deliver batch updates to app users

    **Performance:**
    - Firebase FCM supports up to 500 messages per batch
    - For larger audiences, use topic-based notifications
    - Task processes asynchronously to avoid blocking API

    **Error Handling:**
    - Graceful degradation if Celery is unavailable
    - Task result includes success/failure counts per token
    """
    try:
        task = send_bulk_notifications.delay(
            device_tokens=request.device_tokens,
            title=request.title,
            body=request.body,
            data=request.data,
            image_url=request.image_url,
        )
        task_id = task.id
        logger.info(
            f"Dispatched bulk notification task {task_id} "
            f"to {len(request.device_tokens)} devices"
        )
        status = "queued"
        message = f"Bulk notification queued for {len(request.device_tokens)} devices"
    except Exception as e:
        logger.warning(f"Failed to dispatch bulk notification task: {e}")
        task_id = None
        status = "error"
        message = "Failed to queue notifications - Celery may be unavailable"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status,
            "message": message,
            "device_count": len(request.device_tokens),
            "title": request.title,
        }
    )


@router.post("/topic", response_model=ApiResponse[dict])
async def send_topic(
    request: TopicNotificationRequest,
    _: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
):
    """
    Send push notification to all devices subscribed to a topic.

    **Access Control:** SUPER_ADMIN only

    **Business Rules:**
    - Sends to all devices subscribed to the specified topic
    - No device token list required - FCM handles routing
    - Dispatches async Celery task for background processing
    - Topic subscriptions managed via /topics/{topic}/subscribe endpoint
    - Supports unlimited audience size (FCM limitation: ~millions)
    - Task retries automatically on transient failures

    **Use Cases:**
    - Broadcast platform-wide announcements (topic: "all_users")
    - Send branch-specific updates (topic: "branch_lagos")
    - Department notifications (topic: "dept_media")
    - Role-based messaging (topic: "role_coordinator")

    **Topic Naming Convention:**
    - Use lowercase with underscores: "branch_lagos", "dept_media"
    - Avoid spaces and special characters
    - Topic names are case-sensitive in FCM

    **Performance:**
    - More efficient than bulk notifications for large audiences
    - Single API call regardless of subscriber count
    - FCM handles fanout automatically

    **Error Handling:**
    - Graceful degradation if Celery is unavailable
    - Task logs delivery status for monitoring
    """
    try:
        task = send_topic_notification.delay(
            topic=request.topic,
            title=request.title,
            body=request.body,
            data=request.data,
        )
        task_id = task.id
        logger.info(
            f"Dispatched topic notification task {task_id} to topic {request.topic}"
        )
        status = "queued"
        message = f"Topic notification queued for topic '{request.topic}'"
    except Exception as e:
        logger.warning(f"Failed to dispatch topic notification task: {e}")
        task_id = None
        status = "error"
        message = "Failed to queue topic notification - Celery may be unavailable"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status,
            "message": message,
            "topic": request.topic,
            "title": request.title,
        }
    )


@router.post("/topics/{topic}/subscribe", response_model=ApiResponse[dict])
async def subscribe_devices_to_topic(
    topic: str,
    request: TopicSubscriptionRequest,
    _: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
):
    """
    Subscribe device tokens to a Firebase Cloud Messaging topic.

    **Access Control:** SUPER_ADMIN only

    **Business Rules:**
    - Maximum 1000 device tokens per request (enforced by schema validation)
    - Dispatches async Celery task for background processing
    - Subscribed devices will receive notifications sent to this topic
    - Idempotent operation (subscribing twice has no effect)
    - Topic is created automatically if it doesn't exist
    - Device tokens remain subscribed until explicitly unsubscribed

    **Use Cases:**
    - Subscribe new members to branch topic on registration
    - Add coordinators to leadership topic on role assignment
    - Subscribe users to event-specific topics for reminders
    - Organize users into notification segments

    **Topic Examples:**
    - "all_users" - Platform-wide announcements
    - "branch_lagos" - Branch-specific updates
    - "dept_media" - Department notifications
    - "event_12345" - Event-specific reminders

    **Implementation Notes:**
    - FCM topics have no subscriber limit
    - Subscription persists across app reinstalls (token-based)
    - Invalid tokens are skipped (reported in task result)
    - Task result includes success/failure counts

    **Error Handling:**
    - Graceful degradation if Celery is unavailable
    - Partial failures are handled (some tokens succeed, some fail)
    """
    try:
        task = subscribe_to_topic.delay(
            device_tokens=request.device_tokens,
            topic=topic,
        )
        task_id = task.id
        logger.info(
            f"Dispatched topic subscription task {task_id} "
            f"for {len(request.device_tokens)} devices to topic {topic}"
        )
        status = "queued"
        message = f"Subscription queued for {len(request.device_tokens)} devices to topic '{topic}'"
    except Exception as e:
        logger.warning(f"Failed to dispatch topic subscription task: {e}")
        task_id = None
        status = "error"
        message = "Failed to queue topic subscription - Celery may be unavailable"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status,
            "message": message,
            "topic": topic,
            "device_count": len(request.device_tokens),
        }
    )


@router.post("/topics/{topic}/unsubscribe", response_model=ApiResponse[dict])
async def unsubscribe_devices_from_topic(
    topic: str,
    request: TopicSubscriptionRequest,
    _: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
):
    """
    Unsubscribe device tokens from a Firebase Cloud Messaging topic.

    **Access Control:** SUPER_ADMIN only

    **Business Rules:**
    - Maximum 1000 device tokens per request (enforced by schema validation)
    - Dispatches async Celery task for background processing
    - Unsubscribed devices will no longer receive notifications for this topic
    - Idempotent operation (unsubscribing twice has no effect)
    - Does not affect other topic subscriptions for the device

    **Use Cases:**
    - Unsubscribe members when leaving a branch
    - Remove users from event topics after event completion
    - Unsubscribe users on role change (e.g., coordinator -> member)
    - Clean up inactive device tokens from topics

    **Implementation Notes:**
    - Unsubscribing from non-existent topic is a no-op
    - Invalid tokens are skipped (reported in task result)
    - Task result includes success/failure counts
    - Devices can be resubscribed at any time

    **Error Handling:**
    - Graceful degradation if Celery is unavailable
    - Partial failures are handled (some tokens succeed, some fail)
    """
    try:
        task = unsubscribe_from_topic.delay(
            device_tokens=request.device_tokens,
            topic=topic,
        )
        task_id = task.id
        logger.info(
            f"Dispatched topic unsubscription task {task_id} "
            f"for {len(request.device_tokens)} devices from topic {topic}"
        )
        status = "queued"
        message = f"Unsubscription queued for {len(request.device_tokens)} devices from topic '{topic}'"
    except Exception as e:
        logger.warning(f"Failed to dispatch topic unsubscription task: {e}")
        task_id = None
        status = "error"
        message = "Failed to queue topic unsubscription - Celery may be unavailable"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status,
            "message": message,
            "topic": topic,
            "device_count": len(request.device_tokens),
        }
    )


@router.post("/schedule", response_model=ApiResponse[dict])
async def schedule_notification(
    request: ScheduledNotificationRequest,
    _: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
):
    """
    Schedule a push notification to be sent at a specific future time.

    **Access Control:** SUPER_ADMIN only

    **Business Rules:**
    - Schedule time must be in the future (enforced by schema validation)
    - Dispatches async Celery task with countdown delay
    - Task is queued immediately but executes at scheduled time
    - Requires Celery Beat for production scheduling reliability
    - Maximum schedule horizon depends on Celery configuration

    **Use Cases:**
    - Schedule event reminders (1 hour before event)
    - Send birthday wishes at midnight
    - Queue pledge reminders for specific dates
    - Pre-schedule announcement deliveries

    **Implementation Notes:**
    - Uses Celery countdown (not ETA) for better reliability
    - Scheduled task can be revoked via task_id if needed
    - Task persists in broker queue until execution time
    - Schedule accuracy: ±1 minute (depends on worker polling)

    **Celery Beat Requirement:**
    - For production: Use Celery Beat for persistent scheduling
    - For testing: countdown works without Beat
    - Beat ensures scheduled tasks survive worker restarts

    **Error Handling:**
    - Validates schedule_time is in the future
    - Graceful degradation if Celery is unavailable
    - Returns calculated delay_seconds for verification
    """
    try:
        # Calculate delay in seconds
        now = datetime.utcnow()
        schedule_dt = request.schedule_time.replace(tzinfo=None)
        delay_seconds = int((schedule_dt - now).total_seconds())

        task = send_scheduled_notification.delay(
            device_token=request.device_token,
            title=request.title,
            body=request.body,
            schedule_time=request.schedule_time.isoformat(),
            data=request.data,
        )
        task_id = task.id
        logger.info(
            f"Scheduled push notification task {task_id} "
            f"for {request.schedule_time} (delay: {delay_seconds}s)"
        )
        status = "scheduled"
        message = f"Notification scheduled for {request.schedule_time}"
    except Exception as e:
        logger.warning(f"Failed to schedule notification task: {e}")
        task_id = None
        status = "error"
        message = "Failed to schedule notification - Celery may be unavailable"
        delay_seconds = 0

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status,
            "message": message,
            "scheduled_time": request.schedule_time.isoformat(),
            "delay_seconds": delay_seconds,
            "device_token": request.device_token,
            "title": request.title,
        }
    )
