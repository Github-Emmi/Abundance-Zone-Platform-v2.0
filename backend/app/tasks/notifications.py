"""
Push Notification Background Tasks - Firebase Cloud Messaging
Production-ready notification service with error handling and retry logic
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
except ImportError:
    firebase_admin = None
    messaging = None

from app.tasks.celery_app import celery_app
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Firebase (singleton pattern)
_firebase_initialized = False


def initialize_firebase():
    """Initialize Firebase Admin SDK (idempotent)"""
    global _firebase_initialized

    if _firebase_initialized or not firebase_admin:
        return

    try:
        # Check if already initialized
        firebase_admin.get_app()
        _firebase_initialized = True
        logger.info("Firebase already initialized")
    except ValueError:
        # Not initialized, so initialize now
        try:
            cred = credentials.Certificate(
                {
                    "type": "service_account",
                    "project_id": settings.FIREBASE_PROJECT_ID,
                    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                    "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
                    "client_email": settings.FIREBASE_CLIENT_EMAIL,
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            )
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise


# ═══════════════════════════════════════════════════════════════════════════
# CELERY NOTIFICATION TASKS
# ═══════════════════════════════════════════════════════════════════════════


@celery_app.task(
    name="app.tasks.notifications.send_push_notification",
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def send_push_notification(
    self,
    device_token: str,
    title: str,
    body: str,
    data: Optional[Dict] = None,
    image_url: Optional[str] = None,
) -> Dict:
    """
    Send push notification to a single device

    Args:
        device_token: FCM device token
        title: Notification title
        body: Notification body
        data: Optional custom data payload
        image_url: Optional image URL for rich notification

    Returns:
        Dict with status and message_id
    """
    if not firebase_admin or not messaging:
        logger.error("Firebase Admin SDK not installed")
        return {"status": "error", "message": "Firebase not configured"}

    try:
        initialize_firebase()

        logger.info(f"Sending push notification: {title}")

        # Build notification
        notification = messaging.Notification(
            title=title, body=body, image=image_url if image_url else None
        )

        # Build message
        message = messaging.Message(
            notification=notification,
            data=data or {},
            token=device_token,
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    sound="default", color="#667eea"
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default", badge=1)
                )
            ),
        )

        # Send message
        response = messaging.send(message)

        logger.info(f"Push notification sent successfully: {response}")

        return {
            "status": "sent",
            "message_id": response,
            "title": title,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except messaging.UnregisteredError:
        logger.warning(f"Device token unregistered: {device_token}")
        return {
            "status": "unregistered",
            "message": "Device token is no longer valid",
            "device_token": device_token,
        }
    except messaging.SenderIdMismatchError:
        logger.error(f"Sender ID mismatch for token: {device_token}")
        return {"status": "error", "message": "Sender ID mismatch"}
    except Exception as exc:
        logger.error(f"Failed to send push notification: {str(exc)}")
        raise self.retry(exc=exc, countdown=2**self.request.retries * 60)


@celery_app.task(name="app.tasks.notifications.send_bulk_notifications", bind=True)
def send_bulk_notifications(
    self,
    device_tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict] = None,
    image_url: Optional[str] = None,
) -> Dict:
    """
    Send push notifications to multiple devices (batch)

    Args:
        device_tokens: List of FCM device tokens
        title: Notification title
        body: Notification body
        data: Optional custom data payload
        image_url: Optional image URL

    Returns:
        Dict with success/failure counts
    """
    if not firebase_admin or not messaging:
        return {"status": "error", "message": "Firebase not configured"}

    try:
        initialize_firebase()

        logger.info(f"Sending bulk notifications to {len(device_tokens)} devices")

        # Build notification
        notification = messaging.Notification(
            title=title, body=body, image=image_url if image_url else None
        )

        # Build messages for all tokens
        messages = [
            messaging.Message(
                notification=notification,
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        sound="default", color="#667eea"
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(sound="default", badge=1)
                    )
                ),
            )
            for token in device_tokens
        ]

        # Send batch (Firebase handles up to 500 messages per batch)
        batch_response = messaging.send_all(messages)

        logger.info(
            f"Bulk notifications sent: "
            f"{batch_response.success_count} success, "
            f"{batch_response.failure_count} failed"
        )

        # Collect failed tokens
        failed_tokens = []
        for idx, response in enumerate(batch_response.responses):
            if not response.success:
                failed_tokens.append(
                    {
                        "token": device_tokens[idx],
                        "error": (
                            str(response.exception)
                            if response.exception
                            else "Unknown error"
                        ),
                    }
                )

        return {
            "status": "completed",
            "total": len(device_tokens),
            "success_count": batch_response.success_count,
            "failure_count": batch_response.failure_count,
            "failed_tokens": failed_tokens,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Failed to send bulk notifications: {str(exc)}")
        return {"status": "error", "message": str(exc), "total": len(device_tokens)}


@celery_app.task(
    name="app.tasks.notifications.send_topic_notification",
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_topic_notification(
    self, topic: str, title: str, body: str, data: Optional[Dict] = None
) -> Dict:
    """
    Send notification to a topic (all subscribed devices)

    Args:
        topic: FCM topic name
        title: Notification title
        body: Notification body
        data: Optional custom data payload

    Returns:
        Dict with status and message_id
    """
    if not firebase_admin or not messaging:
        return {"status": "error", "message": "Firebase not configured"}

    try:
        initialize_firebase()

        logger.info(f"Sending notification to topic: {topic}")

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            topic=topic,
        )

        response = messaging.send(message)

        logger.info(f"Topic notification sent: {response}")

        return {
            "status": "sent",
            "topic": topic,
            "message_id": response,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Failed to send topic notification: {str(exc)}")
        raise self.retry(exc=exc)


@celery_app.task(name="app.tasks.notifications.subscribe_to_topic")
def subscribe_to_topic(device_tokens: List[str], topic: str) -> Dict:
    """
    Subscribe devices to a topic

    Args:
        device_tokens: List of device tokens
        topic: Topic name

    Returns:
        Dict with success/failure counts
    """
    if not firebase_admin or not messaging:
        return {"status": "error", "message": "Firebase not configured"}

    try:
        initialize_firebase()

        logger.info(f"Subscribing {len(device_tokens)} devices to topic: {topic}")

        response = messaging.subscribe_to_topic(device_tokens, topic)

        logger.info(
            f"Topic subscription: {response.success_count} success, "
            f"{response.failure_count} failed"
        )

        return {
            "status": "completed",
            "topic": topic,
            "success_count": response.success_count,
            "failure_count": response.failure_count,
            "errors": [str(e) for e in response.errors] if response.errors else [],
        }

    except Exception as exc:
        logger.error(f"Failed to subscribe to topic: {str(exc)}")
        return {"status": "error", "message": str(exc)}


@celery_app.task(name="app.tasks.notifications.unsubscribe_from_topic")
def unsubscribe_from_topic(device_tokens: List[str], topic: str) -> Dict:
    """
    Unsubscribe devices from a topic

    Args:
        device_tokens: List of device tokens
        topic: Topic name

    Returns:
        Dict with success/failure counts
    """
    if not firebase_admin or not messaging:
        return {"status": "error", "message": "Firebase not configured"}

    try:
        initialize_firebase()

        logger.info(f"Unsubscribing {len(device_tokens)} devices from topic: {topic}")

        response = messaging.unsubscribe_from_topic(device_tokens, topic)

        logger.info(
            f"Topic unsubscription: {response.success_count} success, "
            f"{response.failure_count} failed"
        )

        return {
            "status": "completed",
            "topic": topic,
            "success_count": response.success_count,
            "failure_count": response.failure_count,
            "errors": [str(e) for e in response.errors] if response.errors else [],
        }

    except Exception as exc:
        logger.error(f"Failed to unsubscribe from topic: {str(exc)}")
        return {"status": "error", "message": str(exc)}


@celery_app.task(name="app.tasks.notifications.send_scheduled_notification")
def send_scheduled_notification(
    device_token: str,
    title: str,
    body: str,
    schedule_time: str,  # ISO format datetime
    data: Optional[Dict] = None,
) -> Dict:
    """
    Schedule a notification to be sent at a specific time

    Args:
        device_token: FCM device token
        title: Notification title
        body: Notification body
        schedule_time: ISO format datetime when to send
        data: Optional custom data payload

    Returns:
        Dict with task_id and scheduled_time
    """
    from datetime import datetime

    # Parse schedule time
    schedule_dt = datetime.fromisoformat(schedule_time)
    delay_seconds = (schedule_dt - datetime.utcnow()).total_seconds()

    if delay_seconds < 0:
        return {"status": "error", "message": "Schedule time is in the past"}

    # Queue the notification with delay
    task = send_push_notification.apply_async(
        args=[device_token, title, body],
        kwargs={"data": data},
        countdown=int(delay_seconds),
    )

    logger.info(f"Notification scheduled for {schedule_time}, task_id: {task.id}")

    return {
        "status": "scheduled",
        "task_id": task.id,
        "scheduled_time": schedule_time,
        "delay_seconds": delay_seconds,
    }
