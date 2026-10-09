"""
Standardized API Response Schemas

This module provides enterprise-grade standardized response models for all API endpoints.
All responses follow a consistent envelope structure with proper typing and validation.

Response Format:
    Success:
        {
            "success": true,
            "data": {...},
            "meta": {...},
            "timestamp": "2026-10-08T10:30:00Z"
        }
    
    Error:
        {
            "success": false,
            "error": {
                "code": "ERROR_CODE",
                "message": "Human-readable message",
                "details": {...}
            },
            "timestamp": "2026-10-08T10:30:00Z"
        }

Implements: FR-API-001, FR-API-002
"""

from datetime import datetime, timezone
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Generic type variable for data payload
T = TypeVar("T")


class ErrorDetail(BaseModel):
    """
    Error detail model for standardized error responses.
    
    Attributes:
        code: Machine-readable error code (e.g., "VALIDATION_ERROR", "NOT_FOUND")
        message: Human-readable error message for client display
        details: Optional dictionary with additional error context (field errors, stack traces, etc.)
    
    Examples:
        >>> error = ErrorDetail(
        ...     code="VALIDATION_ERROR",
        ...     message="Invalid email format",
        ...     details={"field": "email", "value": "invalid-email"}
        ... )
    """
    
    code: str = Field(
        ...,
        description="Machine-readable error code",
        min_length=1,
        max_length=100,
        examples=["VALIDATION_ERROR", "NOT_FOUND", "UNAUTHORIZED"],
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        min_length=1,
        max_length=500,
        examples=["Invalid email format", "Resource not found"],
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Optional additional error context",
        examples=[{"field": "email", "constraint": "format"}],
    )

    @field_validator("code")
    @classmethod
    def code_must_be_uppercase(cls, v: str) -> str:
        """Ensure error codes follow uppercase snake_case convention."""
        return v.upper()


class ErrorResponse(BaseModel):
    """
    Standardized error response envelope.
    
    Attributes:
        success: Always false for error responses
        error: Error detail object with code, message, and optional details
        timestamp: UTC timestamp when the error occurred
    
    Examples:
        >>> response = ErrorResponse(
        ...     error=ErrorDetail(
        ...         code="NOT_FOUND",
        ...         message="User not found"
        ...     )
        ... )
    """
    
    success: Literal[False] = Field(
        default=False,
        description="Success flag, always false for errors",
    )
    error: ErrorDetail = Field(
        ...,
        description="Error details",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the error occurred",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                    "details": {
                        "field": "email",
                        "constraint": "format",
                    },
                },
                "timestamp": "2026-10-08T10:30:00Z",
            }
        }
    )


class ApiResponse(BaseModel, Generic[T]):
    """
    Generic success response envelope.
    
    Type Parameters:
        T: Type of the data payload
    
    Attributes:
        success: Always true for success responses
        data: Response payload of type T
        meta: Optional metadata (pagination info, warnings, etc.)
        timestamp: UTC timestamp when the response was generated
    
    Examples:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     id: str
        ...     name: str
        >>> response = ApiResponse[User](
        ...     data=User(id="123", name="John Doe")
        ... )
    """
    
    success: Literal[True] = Field(
        default=True,
        description="Success flag, always true for successful responses",
    )
    data: T = Field(
        ...,
        description="Response payload",
    )
    meta: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata (pagination, warnings, etc.)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the response was generated",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {"id": "123", "name": "John Doe"},
                "meta": None,
                "timestamp": "2026-10-08T10:30:00Z",
            }
        }
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated list response with metadata.
    
    Type Parameters:
        T: Type of items in the list
    
    Attributes:
        items: List of items of type T for the current page
        total: Total number of items across all pages
        page: Current page number (1-indexed)
        page_size: Number of items per page
        has_next: Whether there are more pages available
    
    Computed Properties:
        total_pages: Total number of pages (computed from total and page_size)
    
    Examples:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     id: str
        ...     name: str
        >>> response = PaginatedResponse[User](
        ...     items=[User(id="1", name="Alice"), User(id="2", name="Bob")],
        ...     total=50,
        ...     page=1,
        ...     page_size=10
        ... )
        >>> response.has_next
        True
        >>> response.total_pages
        5
    """
    
    items: list[T] = Field(
        ...,
        description="List of items for the current page",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of items across all pages",
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number (1-indexed)",
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page",
    )
    has_next: bool = Field(
        ...,
        description="Whether there are more pages available",
    )

    @property
    def total_pages(self) -> int:
        """
        Calculate total number of pages.
        
        Returns:
            Total number of pages based on total items and page size
        """
        if self.total == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @field_validator("has_next", mode="before")
    @classmethod
    def compute_has_next(cls, v: bool | None, info) -> bool:
        """
        Auto-compute has_next if not provided.
        
        If has_next is not explicitly set, compute it based on page, page_size, and total.
        """
        if v is not None:
            return v
        
        # Get other field values from validation context
        data = info.data
        page = data.get("page", 1)
        page_size = data.get("page_size", 10)
        total = data.get("total", 0)
        
        # Compute has_next: true if there are more items beyond current page
        return (page * page_size) < total

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {"id": "1", "name": "Alice"},
                    {"id": "2", "name": "Bob"},
                ],
                "total": 50,
                "page": 1,
                "page_size": 10,
                "has_next": True,
            }
        }
    )
