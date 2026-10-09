"""
Example usage of standardized API response schemas.

This module demonstrates how to use the response schemas in actual API endpoints.
"""

from pydantic import BaseModel

from app.api.schemas.responses import (
    ApiResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
)


# Example domain model
class User(BaseModel):
    """Example user model."""

    id: str
    name: str
    email: str


def example_success_response():
    """Example: Create a success response with user data."""
    user = User(id="123", name="John Doe", email="john@example.com")
    response = ApiResponse[User](data=user)
    return response


def example_success_response_with_meta():
    """Example: Create a success response with metadata."""
    user = User(id="123", name="John Doe", email="john@example.com")
    response = ApiResponse[User](
        data=user,
        meta={
            "cached": True,
            "cache_ttl": 300,
            "query_time_ms": 45,
        },
    )
    return response


def example_error_response():
    """Example: Create an error response."""
    error = ErrorDetail(
        code="NOT_FOUND",
        message="User not found",
        details={"user_id": "123"},
    )
    response = ErrorResponse(error=error)
    return response


def example_validation_error_response():
    """Example: Create a validation error response."""
    error = ErrorDetail(
        code="VALIDATION_ERROR",
        message="Invalid input data",
        details={
            "errors": [
                {"field": "email", "message": "Invalid email format"},
                {"field": "password", "message": "Password too short"},
            ]
        },
    )
    response = ErrorResponse(error=error)
    return response


def example_paginated_response():
    """Example: Create a paginated response."""
    users = [
        User(id="1", name="Alice", email="alice@example.com"),
        User(id="2", name="Bob", email="bob@example.com"),
        User(id="3", name="Charlie", email="charlie@example.com"),
    ]

    paginated = PaginatedResponse[User](
        items=users,
        total=50,
        page=1,
        page_size=10,
        has_next=True,
    )

    return paginated


def example_wrapped_paginated_response():
    """Example: Wrap paginated data in ApiResponse."""
    users = [
        User(id="1", name="Alice", email="alice@example.com"),
        User(id="2", name="Bob", email="bob@example.com"),
    ]

    paginated = PaginatedResponse[User](
        items=users,
        total=50,
        page=1,
        page_size=10,
        has_next=True,
    )

    response = ApiResponse[PaginatedResponse[User]](
        data=paginated,
        meta={"cached": False},
    )

    return response


if __name__ == "__main__":
    """Demonstrate schema usage."""
    import json

    # Success response
    print("=== Success Response ===")
    success = example_success_response()
    print(json.dumps(success.model_dump(), indent=2, default=str))
    print()

    # Error response
    print("=== Error Response ===")
    error = example_error_response()
    print(json.dumps(error.model_dump(), indent=2, default=str))
    print()

    # Paginated response
    print("=== Paginated Response ===")
    paginated = example_paginated_response()
    print(json.dumps(paginated.model_dump(), indent=2, default=str))
    print(f"Total pages: {paginated.total_pages}")
    print()

    # Wrapped paginated response
    print("=== Wrapped Paginated Response ===")
    wrapped = example_wrapped_paginated_response()
    print(json.dumps(wrapped.model_dump(), indent=2, default=str))
