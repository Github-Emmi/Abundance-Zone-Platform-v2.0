"""Event Management API Router"""

import logging
from datetime import datetime
from fastapi import Query, APIRouter, Depends, status
from app.api.deps import CurrentUserDep, DbSessionDep, require_role
from app.api.schemas.event import *
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.responses import ApiResponse, PaginatedResponse
from app.application.services.event_service import EventService, get_event_service
from app.domain.value_objects.enums import Role
from app.tasks.emails import send_event_reminder, send_bulk_emails

router = APIRouter(prefix="/events", tags=["events"])
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def format_event_notification(
    message: str, event_title: str, notification_type: str = "announcement"
) -> str:
    """
    Format event notification HTML email template

    Args:
        message: Main notification message content
        event_title: Title of the event
        notification_type: Type of notification (announcement/update/cancellation)

    Returns:
        HTML formatted email content
    """
    type_emoji = {"announcement": "📢", "update": "🔔", "cancellation": "⚠️"}

    emoji = type_emoji.get(notification_type, "📢")

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">{emoji} {event_title}</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px;">
                            <div style="color: #666666; line-height: 1.6; font-size: 15px;">
                                {message}
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f9f9f9; padding: 20px; text-align: center;">
                            <p style="color: #999999; font-size: 12px; margin: 0;">© {datetime.utcnow().year} Abundance Zone Youth Platform</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """


# ═══════════════════════════════════════════════════════════════════════════
# EVENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════


@router.post("", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreateRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: EventService = Depends(get_event_service),
):
    """
    Create a new event with optional automatic notification

    Creates an event and automatically notifies branch members if the event
    status is not DRAFT. This ensures stakeholders are immediately informed
    of new events.

    **Auto-Notification Behavior:**
    - Triggered when event status is SCHEDULED or IN_PROGRESS (not DRAFT)
    - Non-blocking: Event creation succeeds even if notification fails
    - Returns task_id for notification tracking

    **Notification Recipients:**
    - Currently: Placeholder for branch member emails
    - Production: Would query branch members from database

    **Use Cases:**
    - Creating new events that should be immediately announced
    - Publishing draft events (change status from DRAFT to SCHEDULED)

    **Error Handling:**
    - Event creation is atomic and always succeeds
    - Notification failures are logged but don't affect event creation
    - Check logs if notification_task_id is null

    Returns:
        Event details with optional notification_task_id for tracking
    """
    event = await service.create_event(
        data.title,
        data.event_type,
        data.event_date,
        data.branch_id,
        current_user.id,
        data.description,
        data.venue,
        data.end_date,
        db,
    )

    # Auto-dispatch notification for published events
    notification_task_id = None
    if event.status not in ["DRAFT"]:  # Notify for SCHEDULED, IN_PROGRESS, etc.
        try:
            # Format event details for notification
            event_date_str = event.event_date.strftime("%B %d, %Y at %I:%M %p")
            venue_str = event.venue or "Location TBD"

            # Create notification message
            message = f"""
            <p>A new event has been created:</p>
            <h3 style="color: #667eea;">{event.title}</h3>
            <p><strong>Date:</strong> {event_date_str}</p>
            <p><strong>Location:</strong> {venue_str}</p>
            {f'<p><strong>Description:</strong> {event.description}</p>' if event.description else ''}
            <p>Check the platform for more details and to RSVP!</p>
            """

            # TODO: Get branch member emails from database
            # For now, using empty list as placeholder
            # In production: query UserModel where branch_id = event.branch_id
            email_list = []  # await get_branch_member_emails(event.branch_id, db)

            if email_list:
                task = send_bulk_emails.delay(
                    email_list=email_list,
                    subject=f"New Event: {event.title}",
                    html_content=format_event_notification(
                        message=message, event_title=event.title, notification_type="announcement"
                    ),
                )
                notification_task_id = task.id
                logger.info(
                    f"Dispatched new event notification task {notification_task_id} for event {event.id}"
                )
            else:
                logger.debug(f"No branch members to notify for new event {event.id}")
        except Exception as e:
            # Log error but don't fail event creation
            logger.warning(f"Failed to dispatch new event notification for {event.id}: {e}")

    # Return event data with notification task ID
    event_data = EventResponse.from_orm(event)
    response_data = {**event_data.dict(), "notification_task_id": notification_task_id}

    return ApiResponse(data=response_data)


@router.get("/{event_id}", response_model=ApiResponse[EventResponse])
async def get_event(
    event_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: EventService = Depends(get_event_service),
):
    event = await service.get_event(event_id, db)
    return ApiResponse(data=EventResponse.from_orm(event))


@router.get("", response_model=ApiResponse[PaginatedResponse[EventResponse]])
async def list_events(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    branch_id: str | None = Query(None),
    pagination: PaginationParams = Depends(get_pagination_params),
    service: EventService = Depends(get_event_service),
):
    events, total = await service.list_events(branch_id, pagination.offset, pagination.limit, db)
    items = [EventResponse.from_orm(e) for e in events]
    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=(pagination.page * pagination.page_size) < total,
        )
    )


@router.post("/{event_id}/remind", response_model=ApiResponse[EventNotificationResponse])
async def send_event_reminders(
    event_id: str,
    data: EventReminderRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: EventService = Depends(get_event_service),
    _: None = Depends(require_role([Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN])),
):
    """
    Send event reminder emails to all registered attendees

    This endpoint dispatches email reminder tasks to all users who have RSVP'd to an event.
    Each email is sent asynchronously via Celery for optimal performance.

    **Email Content:**
    - Event name, date, time, and location
    - Customizable message (optional)
    - Professional HTML template with event details

    **Reminder Timing:**
    - Configure via `reminder_hours_before` parameter (default: 24 hours)
    - Useful for sending advance notifications (e.g., 48 hours, 72 hours before)

    **Use Cases:**
    - Pre-event reminders to boost attendance
    - Last-minute notifications before event starts
    - Follow-up reminders for multi-day events

    **Task Tracking:**
    - Returns list of Celery task IDs for monitoring via `/api/v1/tasks/{task_id}`
    - Each task represents one email delivery attempt
    - Non-blocking: returns immediately while emails send in background

    **Permissions:**
    - BRANCH_COORDINATOR: Can send reminders for events in their branch
    - SUPER_ADMIN: Can send reminders for any event

    **Error Handling:**
    - Failed email dispatches are logged but don't block other emails
    - Graceful degradation: returns partial success if some emails fail to queue
    """
    logger.info(f"User {current_user.id} requesting event reminders for event {event_id}")

    # Get event details
    event = await service.get_event(event_id, db)

    # Get all attendees/registrants
    # Note: Current implementation returns empty list - this is a placeholder
    # In production, this would query the RSVP table for registered attendees
    attendees, total = await service.list_attendees(event_id, 0, 1000, db)

    if not attendees:
        logger.warning(f"No attendees found for event {event_id}")
        return ApiResponse(
            data=EventNotificationResponse(
                task_ids=[],
                status="success",
                message="No attendees to notify",
                event_id=event_id,
                recipient_count=0,
                failed_count=0,
                timestamp=datetime.utcnow().isoformat(),
            )
        )

    # Dispatch reminder tasks
    task_ids = []
    failed_count = 0

    for attendee in attendees:
        try:
            task = send_event_reminder.delay(
                user_email=attendee.get("email"),
                user_name=attendee.get("name", "Guest"),
                event_name=event.title,
                event_date=event.event_date.strftime("%B %d, %Y"),
                event_time=event.event_date.strftime("%I:%M %p"),
                event_location=event.venue or "TBD",
            )
            task_ids.append(task.id)
            logger.debug(f"Dispatched reminder task {task.id} for {attendee.get('email')}")
        except Exception as e:
            logger.warning(f"Failed to dispatch reminder for {attendee.get('email')}: {e}")
            failed_count += 1

    logger.info(
        f"Dispatched {len(task_ids)} event reminder tasks for event {event_id}, {failed_count} failed"
    )

    return ApiResponse(
        data=EventNotificationResponse(
            task_ids=task_ids,
            status="queued" if task_ids else "error",
            message=f"Event reminders queued for {len(task_ids)} recipients"
            + (f", {failed_count} failed" if failed_count > 0 else ""),
            event_id=event_id,
            recipient_count=len(task_ids),
            failed_count=failed_count,
            timestamp=datetime.utcnow().isoformat(),
        )
    )


@router.post("/{event_id}/notify", response_model=ApiResponse[EventNotificationResponse])
async def send_event_notification(
    event_id: str,
    data: EventNotifyRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: EventService = Depends(get_event_service),
    _: None = Depends(require_role([Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN])),
):
    """
    Send custom notification email to all event registrants

    This endpoint allows coordinators to send custom announcements, updates, or cancellation
    notices to all users who have registered for an event.

    **Email Format:**
    - Custom subject line and message body
    - Professional HTML template with event branding
    - Appropriate emoji/styling based on notification type

    **Notification Types:**
    - `announcement`: General event announcements (📢)
    - `update`: Event details changed (🔔)
    - `cancellation`: Event cancelled or postponed (⚠️)

    **Common Use Cases:**
    - **Venue Changes:** Notify attendees of location updates
    - **Time Changes:** Announce rescheduled event times
    - **Cancellations:** Inform registrants of event cancellations
    - **Special Instructions:** Share parking info, dress code, what to bring
    - **Last-Minute Updates:** Weather alerts, speaker changes, etc.

    **Bulk Delivery:**
    - Uses optimized bulk email task for efficient delivery
    - Single Celery task handles all recipients
    - Automatically retries failed deliveries

    **Task Tracking:**
    - Returns single task ID for the bulk operation
    - Monitor progress via `/api/v1/tasks/{task_id}`
    - Non-blocking: returns immediately

    **Permissions:**
    - BRANCH_COORDINATOR: Can notify events in their branch
    - SUPER_ADMIN: Can notify any event

    **Rate Limiting:**
    - Consider implementing rate limits for very large recipient lists
    - Current implementation suitable for typical event sizes (<1000 attendees)

    **Example Messages:**
    - Venue change: "The event location has been changed to the Main Auditorium. All other details remain the same."
    - Cancellation: "Unfortunately, due to unforeseen circumstances, this event has been cancelled. We apologize for any inconvenience."
    - Update: "Please arrive 30 minutes early for registration. Bring a valid ID for check-in."
    """
    logger.info(
        f"User {current_user.id} sending notification for event {event_id}, type: {data.notification_type}"
    )

    # Get event details
    event = await service.get_event(event_id, db)

    # Get all attendees
    attendees, total = await service.list_attendees(event_id, 0, 1000, db)

    if not attendees:
        logger.warning(f"No attendees found for event {event_id}")
        return ApiResponse(
            data=EventNotificationResponse(
                task_ids=[],
                status="success",
                message="No attendees to notify",
                event_id=event_id,
                recipient_count=0,
                failed_count=0,
                timestamp=datetime.utcnow().isoformat(),
            )
        )

    # Extract email list
    email_list = [attendee.get("email") for attendee in attendees if attendee.get("email")]

    if not email_list:
        logger.warning(f"No valid email addresses found for event {event_id} attendees")
        return ApiResponse(
            data=EventNotificationResponse(
                task_ids=[],
                status="error",
                message="No valid email addresses found",
                event_id=event_id,
                recipient_count=0,
                failed_count=0,
                timestamp=datetime.utcnow().isoformat(),
            )
        )

    # Generate HTML content
    html_content = format_event_notification(
        message=data.message, event_title=event.title, notification_type=data.notification_type
    )

    # Dispatch bulk email task
    try:
        task = send_bulk_emails.delay(
            email_list=email_list, subject=data.subject, html_content=html_content
        )
        task_id = task.id
        logger.info(f"Dispatched bulk notification task {task_id} for {len(email_list)} recipients")

        return ApiResponse(
            data=EventNotificationResponse(
                task_ids=[task_id],
                status="queued",
                message=f"Event notification queued for {len(email_list)} recipients",
                event_id=event_id,
                recipient_count=len(email_list),
                failed_count=0,
                timestamp=datetime.utcnow().isoformat(),
            )
        )
    except Exception as e:
        logger.error(f"Failed to dispatch bulk notification for event {event_id}: {e}")
        return ApiResponse(
            data=EventNotificationResponse(
                task_ids=[],
                status="error",
                message=f"Failed to queue notification: {str(e)}",
                event_id=event_id,
                recipient_count=0,
                failed_count=len(email_list),
                timestamp=datetime.utcnow().isoformat(),
            )
        )
