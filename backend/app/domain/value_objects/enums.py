"""
Domain Enums
Immutable value objects representing system enumerations
"""

from enum import Enum


class Role(str, Enum):
    """User roles in the system (4-tier RBAC)"""

    SUPER_ADMIN = "SUPER_ADMIN"
    BRANCH_COORDINATOR = "BRANCH_COORDINATOR"
    DEPARTMENT_LEADER = "DEPARTMENT_LEADER"
    YOUTH_MEMBER = "YOUTH_MEMBER"


class Gender(str, Enum):
    """Gender options"""

    MALE = "MALE"
    FEMALE = "FEMALE"


class MembershipStatus(str, Enum):
    """Youth membership status"""

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    AT_RISK = "AT_RISK"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"
    REJECTED = "REJECTED"
    TERMINATED = "TERMINATED"


class AttendanceStatus(str, Enum):
    """Attendance record status"""

    PENDING_CHECK_IN = "PENDING_CHECK_IN"
    CHECKED_IN = "CHECKED_IN"
    PRESENT = "PRESENT"
    EARLY_DEPARTURE = "EARLY_DEPARTURE"
    ABSENT = "ABSENT"
    EXCUSED = "EXCUSED"
    LATE = "LATE"


class EventType(str, Enum):
    """Event types for recurring services"""

    SUNDAY_SERVICE = "SUNDAY_SERVICE"
    BIBLE_STUDY = "BIBLE_STUDY"
    WORKERS_MEETING = "WORKERS_MEETING"
    REVIVAL_HOUR = "REVIVAL_HOUR"
    YOUTH_VIGIL = "YOUTH_VIGIL"
    SPECIAL_EVENT = "SPECIAL_EVENT"
    REGIONAL_MEETING = "REGIONAL_MEETING"


class EventStatus(str, Enum):
    """Event lifecycle status"""

    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    RESCHEDULED = "RESCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class PledgeType(str, Enum):
    """Pledge/financial commitment types"""

    MONTHLY = "MONTHLY"
    PROJECT = "PROJECT"
    PROGRAM = "PROGRAM"
    SPECIAL = "SPECIAL"


class PledgeStatus(str, Enum):
    """Pledge payment status"""

    PLEDGED = "PLEDGED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    FULLY_PAID = "FULLY_PAID"
    OVERDUE = "OVERDUE"
    DEFAULTED = "DEFAULTED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""

    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    PUSH = "PUSH"


class NotificationType(str, Enum):
    """Notification type categories"""

    ANNOUNCEMENT = "ANNOUNCEMENT"
    REMINDER = "REMINDER"
    ATTENDANCE_ALERT = "ATTENDANCE_ALERT"
    PLEDGE_REMINDER = "PLEDGE_REMINDER"
    EVENT_INVITE = "EVENT_INVITE"
    PAYMENT_CONFIRMATION = "PAYMENT_CONFIRMATION"
    SYSTEM = "SYSTEM"


class NotificationPriority(str, Enum):
    """Notification priority levels"""

    CRITICAL = "CRITICAL"  # Security alerts, payment confirmations
    HIGH = "HIGH"  # Event reminders, attendance alerts
    NORMAL = "NORMAL"  # General announcements
    LOW = "LOW"  # Monthly summaries


class NotificationStatus(str, Enum):
    """Notification delivery status"""

    QUEUED = "QUEUED"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    PARTIALLY_DELIVERED = "PARTIALLY_DELIVERED"
    PERMANENT_FAILURE = "PERMANENT_FAILURE"


class AuditAction(str, Enum):
    """Audit log action types"""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    ROLE_CHANGE = "ROLE_CHANGE"
    PASSWORD_RESET = "PASSWORD_RESET"
