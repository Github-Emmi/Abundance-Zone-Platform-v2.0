"""
Email Background Tasks - Resend Integration
Production-ready email service with retry logic and error handling
"""

from typing import Optional, Dict, List
from datetime import datetime
import logging

try:
    import resend
except ImportError:
    resend = None

from app.tasks.celery_app import celery_app
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Resend
if resend:
    resend.api_key = settings.RESEND_API_KEY


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════

def get_welcome_email_html(user_name: str, login_url: str) -> str:
    """Welcome email HTML template"""
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
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">🎉 Welcome to Abundance Zone!</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="color: #333333; margin: 0 0 20px 0;">Hello {user_name}!</h2>
                            <p style="color: #666666; line-height: 1.6; margin: 0 0 15px 0;">We're excited to have you join our youth management platform.</p>
                            <p style="color: #666666; line-height: 1.6; margin: 0 0 15px 0;">Your account has been successfully created. You can now:</p>
                            <ul style="color: #666666; line-height: 1.8; margin: 0 0 25px 0;">
                                <li>✅ Manage your profile</li>
                                <li>✅ Track attendance</li>
                                <li>✅ Register for events</li>
                                <li>✅ View reports and analytics</li>
                            </ul>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <a href="{login_url}" style="background-color: #667eea; color: #ffffff; padding: 14px 35px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Get Started →</a>
                                    </td>
                                </tr>
                            </table>
                            <p style="color: #666666; line-height: 1.6; margin: 0;">If you have any questions, feel free to reach out to your branch coordinator.</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f9f9f9; padding: 20px; text-align: center;">
                            <p style="color: #999999; font-size: 12px; margin: 0;">© {datetime.now().year} Abundance Zone Youth Platform. All rights reserved.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """


def get_password_reset_email_html(user_name: str, reset_url: str, expires_in: int) -> str:
    """Password reset email HTML template"""
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
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden;">
                    <tr>
                        <td style="background-color: #f44336; padding: 40px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">🔑 Password Reset Request</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="color: #333333; margin: 0 0 20px 0;">Hello {user_name},</h2>
                            <p style="color: #666666; line-height: 1.6;">We received a request to reset your password.</p>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <a href="{reset_url}" style="background-color: #f44336; color: #ffffff; padding: 14px 35px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Reset Password →</a>
                                    </td>
                                </tr>
                            </table>
                            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                                <p style="margin: 0; color: #856404;"><strong>⚠️ Security Notice:</strong></p>
                                <p style="margin: 5px 0 0 0; color: #856404; font-size: 14px;">This link expires in {expires_in} hours. If you didn't request this, please ignore this email.</p>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f9f9f9; padding: 20px; text-align: center;">
                            <p style="color: #999999; font-size: 12px; margin: 0;">© {datetime.now().year} Abundance Zone Youth Platform</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """


def get_email_verification_html(user_name: str, verification_url: str, expires_in: int) -> str:
    """Email verification HTML template"""
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
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden;">
                    <tr>
                        <td style="background-color: #4caf50; padding: 40px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">✉️ Verify Your Email</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="color: #333333; margin: 0 0 20px 0;">Hello {user_name},</h2>
                            <p style="color: #666666; line-height: 1.6;">Thanks for signing up! Please verify your email address to activate your account.</p>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <a href="{verification_url}" style="background-color: #4caf50; color: #ffffff; padding: 14px 35px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Verify Email →</a>
                                    </td>
                                </tr>
                            </table>
                            <p style="color: #666666; line-height: 1.6; font-size: 14px;">This link will expire in {expires_in} hours.</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f9f9f9; padding: 20px; text-align: center;">
                            <p style="color: #999999; font-size: 12px; margin: 0;">© {datetime.now().year} Abundance Zone Youth Platform</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """


def get_event_reminder_html(
    user_name: str, 
    event_name: str, 
    event_date: str, 
    event_time: str, 
    event_location: str
) -> str:
    """Event reminder email HTML template"""
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
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden;">
                    <tr>
                        <td style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 40px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">⏰ Event Reminder</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="color: #333333; margin: 0 0 20px 0;">Hello {user_name},</h2>
                            <p style="color: #666666; line-height: 1.6;">This is a friendly reminder about the upcoming event:</p>
                            <div style="background-color: #ffffff; border: 2px solid #f5576c; border-radius: 8px; padding: 20px; margin: 20px 0;">
                                <h3 style="color: #f5576c; margin: 0 0 15px 0;">📅 {event_name}</h3>
                                <p style="color: #666666; margin: 5px 0;"><strong>Date:</strong> {event_date}</p>
                                <p style="color: #666666; margin: 5px 0;"><strong>Time:</strong> {event_time}</p>
                                <p style="color: #666666; margin: 5px 0;"><strong>Location:</strong> {event_location}</p>
                            </div>
                            <p style="color: #666666; line-height: 1.6;">We look forward to seeing you there!</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f9f9f9; padding: 20px; text-align: center;">
                            <p style="color: #999999; font-size: 12px; margin: 0;">© {datetime.now().year} Abundance Zone Youth Platform</p>
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
# CELERY EMAIL TASKS
# ═══════════════════════════════════════════════════════════════════════════

@celery_app.task(
    name="app.tasks.emails.send_welcome_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def send_welcome_email(
    self, 
    user_email: str, 
    user_name: str, 
    user_id: Optional[str] = None
) -> Dict:
    """
    Send welcome email to new user with retry logic
    
    Args:
        user_email: Recipient email address
        user_name: User's full name
        user_id: Optional user ID for tracking
        
    Returns:
        Dict with status, email, and message_id
    """
    if not resend:
        logger.error("Resend library not installed")
        return {"status": "error", "message": "Resend not configured"}
    
    try:
        logger.info(f"Sending welcome email to {user_email}")
        
        frontend_url = settings.FRONTEND_URL
        login_url = f"{frontend_url}/login"
        html_content = get_welcome_email_html(user_name, login_url)
        
        response = resend.Emails.send({
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [user_email],
            "subject": "Welcome to Abundance Zone! 🎉",
            "html": html_content,
        })
        
        logger.info(f"Welcome email sent successfully to {user_email}")
        
        return {
            "status": "sent",
            "email": user_email,
            "message_id": response.get("id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Failed to send welcome email to {user_email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)


@celery_app.task(
    name="app.tasks.emails.send_password_reset_email",
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_password_reset_email(
    self, 
    user_email: str, 
    user_name: str, 
    reset_token: str
) -> Dict:
    """Send password reset email"""
    if not resend:
        return {"status": "error", "message": "Resend not configured"}
    
    try:
        logger.info(f"Sending password reset email to {user_email}")
        
        frontend_url = settings.FRONTEND_URL
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        expires_in = settings.PASSWORD_RESET_EXPIRE_HOURS
        html_content = get_password_reset_email_html(user_name, reset_url, expires_in)
        
        response = resend.Emails.send({
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [user_email],
            "subject": "Reset Your Password 🔑",
            "html": html_content,
        })
        
        logger.info(f"Password reset email sent to {user_email}")
        
        return {
            "status": "sent",
            "email": user_email,
            "message_id": response.get("id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Failed to send password reset to {user_email}: {str(exc)}")
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.emails.send_email_verification",
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_email_verification(
    self, 
    user_email: str, 
    user_name: str, 
    verification_token: str
) -> Dict:
    """Send email verification link"""
    if not resend:
        return {"status": "error", "message": "Resend not configured"}
    
    try:
        logger.info(f"Sending email verification to {user_email}")
        
        frontend_url = settings.FRONTEND_URL
        verification_url = f"{frontend_url}/verify-email?token={verification_token}"
        expires_in = settings.EMAIL_VERIFICATION_EXPIRE_HOURS
        html_content = get_email_verification_html(user_name, verification_url, expires_in)
        
        response = resend.Emails.send({
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [user_email],
            "subject": "Verify Your Email Address ✉️",
            "html": html_content,
        })
        
        logger.info(f"Email verification sent to {user_email}")
        
        return {
            "status": "sent",
            "email": user_email,
            "message_id": response.get("id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Failed to send verification to {user_email}: {str(exc)}")
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.emails.send_event_reminder",
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_event_reminder(
    self,
    user_email: str,
    user_name: str,
    event_name: str,
    event_date: str,
    event_time: str,
    event_location: str
) -> Dict:
    """Send event reminder email"""
    if not resend:
        return {"status": "error", "message": "Resend not configured"}
    
    try:
        logger.info(f"Sending event reminder to {user_email} for {event_name}")
        
        html_content = get_event_reminder_html(
            user_name, event_name, event_date, event_time, event_location
        )
        
        response = resend.Emails.send({
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [user_email],
            "subject": f"Reminder: {event_name} ⏰",
            "html": html_content,
        })
        
        logger.info(f"Event reminder sent to {user_email}")
        
        return {
            "status": "sent",
            "email": user_email,
            "event": event_name,
            "message_id": response.get("id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Failed to send event reminder to {user_email}: {str(exc)}")
        raise self.retry(exc=exc)


@celery_app.task(name="app.tasks.emails.send_bulk_emails")
def send_bulk_emails(
    email_list: List[str], 
    subject: str, 
    html_content: str
) -> Dict:
    """
    Send bulk emails to multiple recipients
    
    Args:
        email_list: List of recipient email addresses
        subject: Email subject line
        html_content: HTML email body
        
    Returns:
        Dict with summary of sent/failed emails
    """
    if not resend:
        return {"status": "error", "message": "Resend not configured"}
    
    sent_count = 0
    failed_count = 0
    results = []
    
    logger.info(f"Starting bulk email send to {len(email_list)} recipients")
    
    for email in email_list:
        try:
            response = resend.Emails.send({
                "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
                "to": [email],
                "subject": subject,
                "html": html_content,
            })
            sent_count += 1
            results.append({
                "email": email,
                "status": "sent",
                "message_id": response.get("id")
            })
            logger.debug(f"Bulk email sent to {email}")
        except Exception as e:
            failed_count += 1
            results.append({
                "email": email,
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"Failed to send bulk email to {email}: {str(e)}")
    
    logger.info(f"Bulk email completed: {sent_count} sent, {failed_count} failed")
    
    return {
        "total": len(email_list),
        "sent": sent_count,
        "failed": failed_count,
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }
