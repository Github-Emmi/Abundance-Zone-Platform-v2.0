"""
Custom Exception Classes
Domain-specific exceptions for clean error handling
"""

from typing import Any


class DomainException(Exception):
    """Base exception for all domain-level errors"""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.details = details or {}
        super().__init__(self.message)


# ─── Authentication & Authorization Exceptions ───────────────────────────────
class AuthenticationException(DomainException):
    """Raised when authentication fails"""

    pass


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid"""

    def __init__(self):
        super().__init__(
            message="Invalid email or password", code="INVALID_CREDENTIALS"
        )


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired"""

    def __init__(self):
        super().__init__(
            message="Authentication token has expired", code="TOKEN_EXPIRED"
        )


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is malformed or invalid"""

    def __init__(self):
        super().__init__(message="Invalid authentication token", code="INVALID_TOKEN")


class AuthorizationException(DomainException):
    """Raised when user lacks required permissions"""

    def __init__(self, required_role: str | None = None):
        message = "You do not have permission to perform this action"
        if required_role:
            message = f"This action requires {required_role} role"
        super().__init__(
            message=message,
            code="INSUFFICIENT_PERMISSIONS",
            details={"required_role": required_role} if required_role else {},
        )


# ─── Resource Exceptions ─────────────────────────────────────────────────────
class ResourceNotFoundException(DomainException):
    """Raised when a requested resource is not found"""

    def __init__(self, resource_type: str, resource_id: str | None = None):
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(
            message=message,
            code=f"{resource_type.upper()}_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class DuplicateResourceException(DomainException):
    """Raised when attempting to create a duplicate resource"""

    def __init__(self, resource_type: str, field: str, value: str):
        super().__init__(
            message=f"{resource_type} with {field} '{value}' already exists",
            code=f"DUPLICATE_{resource_type.upper()}",
            details={"resource_type": resource_type, "field": field, "value": value},
        )


# ─── Validation Exceptions ───────────────────────────────────────────────────
class ValidationException(DomainException):
    """Raised when input validation fails"""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field} if field else {},
        )


class InvalidPhoneNumberException(ValidationException):
    """Raised when phone number format is invalid"""

    def __init__(self, phone: str):
        super().__init__(message=f"Invalid phone number format: {phone}", field="phone")


class InvalidEmailException(ValidationException):
    """Raised when email format is invalid"""

    def __init__(self, email: str):
        super().__init__(message=f"Invalid email format: {email}", field="email")


# ─── Business Logic Exceptions ───────────────────────────────────────────────
class BusinessRuleViolationException(DomainException):
    """Raised when a business rule is violated"""

    pass


class InsufficientBalanceException(BusinessRuleViolationException):
    """Raised when pledge payment exceeds remaining balance"""

    def __init__(
        self, pledge_amount: float, paid_amount: float, payment_attempt: float
    ):
        remaining = pledge_amount - paid_amount
        super().__init__(
            message=f"Payment amount ({payment_attempt}) exceeds remaining balance ({remaining})",
            code="INSUFFICIENT_BALANCE",
            details={
                "pledge_amount": pledge_amount,
                "paid_amount": paid_amount,
                "remaining_balance": remaining,
                "payment_attempt": payment_attempt,
            },
        )


class AttendanceAlreadyRecordedException(BusinessRuleViolationException):
    """Raised when attempting to record duplicate attendance"""

    def __init__(self, youth_id: str, event_id: str):
        super().__init__(
            message="Attendance already recorded for this youth at this event",
            code="DUPLICATE_ATTENDANCE",
            details={"youth_id": youth_id, "event_id": event_id},
        )


# ─── External Service Exceptions ─────────────────────────────────────────────
class ExternalServiceException(DomainException):
    """Raised when external API call fails"""

    def __init__(self, service_name: str, error_message: str):
        super().__init__(
            message=f"{service_name} service error: {error_message}",
            code=f"{service_name.upper()}_SERVICE_ERROR",
            details={"service": service_name, "error": error_message},
        )


class AIServiceException(ExternalServiceException):
    """Raised when AI service (Gemini/OpenAI) fails"""

    def __init__(self, error_message: str):
        super().__init__("AI", error_message)


class StorageServiceException(ExternalServiceException):
    """Raised when file storage (Cloudinary) fails"""

    def __init__(self, error_message: str):
        super().__init__("Storage", error_message)


class NotificationServiceException(ExternalServiceException):
    """Raised when notification service (Email/WhatsApp/FCM) fails"""

    def __init__(self, channel: str, error_message: str):
        super().__init__(f"Notification ({channel})", error_message)


# ─── Rate Limiting Exceptions ────────────────────────────────────────────────
class RateLimitExceededException(DomainException):
    """Raised when API rate limit is exceeded"""

    def __init__(self, limit: int, retry_after: int):
        super().__init__(
            message=f"Rate limit exceeded. Maximum {limit} requests per minute allowed.",
            code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit, "retry_after_seconds": retry_after},
        )


# ─── Backward Compatibility Aliases ──────────────────────────────────────────
NotFoundException = ResourceNotFoundException
