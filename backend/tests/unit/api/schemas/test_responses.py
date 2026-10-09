"""
Unit tests for API response schemas.

Tests all response models including ApiResponse, ErrorResponse, and PaginatedResponse.
Validates generic typing, field validation, and business logic.
"""

from datetime import datetime, timezone

import pytest
from pydantic import BaseModel, ValidationError

from app.api.schemas.responses import (
    ApiResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
)


# ─── Test Fixtures ─────────────────────────────────────────────────────────────


class SampleUser(BaseModel):
    """Sample model for testing generic responses."""

    id: str
    name: str
    email: str


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return SampleUser(id="123", name="John Doe", email="john@example.com")


@pytest.fixture
def sample_users():
    """Create a list of sample users for testing pagination."""
    return [
        SampleUser(id="1", name="Alice", email="alice@example.com"),
        SampleUser(id="2", name="Bob", email="bob@example.com"),
        SampleUser(id="3", name="Charlie", email="charlie@example.com"),
    ]


# ─── ErrorDetail Tests ─────────────────────────────────────────────────────────


class TestErrorDetail:
    """Test suite for ErrorDetail model."""

    def test_create_error_detail_minimal(self):
        """Test creating ErrorDetail with only required fields."""
        error = ErrorDetail(code="NOT_FOUND", message="Resource not found")

        assert error.code == "NOT_FOUND"
        assert error.message == "Resource not found"
        assert error.details is None

    def test_create_error_detail_with_details(self):
        """Test creating ErrorDetail with optional details."""
        error = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Invalid input",
            details={"field": "email", "constraint": "format"},
        )

        assert error.code == "VALIDATION_ERROR"
        assert error.message == "Invalid input"
        assert error.details == {"field": "email", "constraint": "format"}

    def test_error_code_uppercase_conversion(self):
        """Test that error codes are automatically converted to uppercase."""
        error = ErrorDetail(code="validation_error", message="Invalid input")

        assert error.code == "VALIDATION_ERROR"

    def test_error_code_already_uppercase(self):
        """Test that uppercase codes remain unchanged."""
        error = ErrorDetail(code="NOT_FOUND", message="Resource not found")

        assert error.code == "NOT_FOUND"

    def test_error_code_mixed_case(self):
        """Test mixed case conversion."""
        error = ErrorDetail(code="Validation_Error", message="Invalid input")

        assert error.code == "VALIDATION_ERROR"

    def test_error_detail_validation_empty_code(self):
        """Test that empty code is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorDetail(code="", message="Invalid input")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("code",) for e in errors)

    def test_error_detail_validation_empty_message(self):
        """Test that empty message is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorDetail(code="ERROR", message="")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("message",) for e in errors)

    def test_error_detail_validation_code_too_long(self):
        """Test that code exceeding max length is rejected."""
        long_code = "A" * 101  # Max is 100

        with pytest.raises(ValidationError) as exc_info:
            ErrorDetail(code=long_code, message="Error")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("code",) for e in errors)

    def test_error_detail_validation_message_too_long(self):
        """Test that message exceeding max length is rejected."""
        long_message = "A" * 501  # Max is 500

        with pytest.raises(ValidationError) as exc_info:
            ErrorDetail(code="ERROR", message=long_message)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("message",) for e in errors)

    def test_error_detail_serialization(self):
        """Test ErrorDetail JSON serialization."""
        error = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Invalid email",
            details={"field": "email"},
        )

        json_data = error.model_dump()

        assert json_data["code"] == "VALIDATION_ERROR"
        assert json_data["message"] == "Invalid email"
        assert json_data["details"] == {"field": "email"}


# ─── ErrorResponse Tests ───────────────────────────────────────────────────────


class TestErrorResponse:
    """Test suite for ErrorResponse model."""

    def test_create_error_response(self):
        """Test creating ErrorResponse."""
        error_detail = ErrorDetail(code="NOT_FOUND", message="User not found")
        response = ErrorResponse(error=error_detail)

        assert response.success is False
        assert response.error.code == "NOT_FOUND"
        assert response.error.message == "User not found"
        assert isinstance(response.timestamp, datetime)

    def test_error_response_timestamp_utc(self):
        """Test that timestamp is in UTC timezone."""
        error_detail = ErrorDetail(code="ERROR", message="An error occurred")
        response = ErrorResponse(error=error_detail)

        assert response.timestamp.tzinfo == timezone.utc

    def test_error_response_success_always_false(self):
        """Test that success field is always False."""
        error_detail = ErrorDetail(code="ERROR", message="An error occurred")
        response = ErrorResponse(error=error_detail)

        assert response.success is False

    def test_error_response_with_details(self):
        """Test ErrorResponse with nested error details."""
        error_detail = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Multiple validation errors",
            details={
                "errors": [
                    {"field": "email", "message": "Invalid format"},
                    {"field": "password", "message": "Too short"},
                ]
            },
        )
        response = ErrorResponse(error=error_detail)

        assert response.error.details is not None
        assert "errors" in response.error.details
        assert len(response.error.details["errors"]) == 2

    def test_error_response_serialization(self):
        """Test ErrorResponse JSON serialization."""
        error_detail = ErrorDetail(
            code="UNAUTHORIZED", message="Invalid credentials"
        )
        response = ErrorResponse(error=error_detail)

        json_data = response.model_dump()

        assert json_data["success"] is False
        assert json_data["error"]["code"] == "UNAUTHORIZED"
        assert json_data["error"]["message"] == "Invalid credentials"
        assert "timestamp" in json_data


# ─── ApiResponse Tests ─────────────────────────────────────────────────────────


class TestApiResponse:
    """Test suite for ApiResponse generic model."""

    def test_create_api_response_with_dict(self):
        """Test creating ApiResponse with dictionary data."""
        data = {"id": "123", "name": "Test"}
        response = ApiResponse[dict](data=data)

        assert response.success is True
        assert response.data == data
        assert response.meta is None
        assert isinstance(response.timestamp, datetime)

    def test_create_api_response_with_pydantic_model(self, sample_user):
        """Test creating ApiResponse with Pydantic model."""
        response = ApiResponse[SampleUser](data=sample_user)

        assert response.success is True
        assert response.data.id == "123"
        assert response.data.name == "John Doe"
        assert response.data.email == "john@example.com"

    def test_api_response_with_meta(self, sample_user):
        """Test ApiResponse with metadata."""
        response = ApiResponse[SampleUser](
            data=sample_user, meta={"version": "1.0", "cached": True}
        )

        assert response.meta is not None
        assert response.meta["version"] == "1.0"
        assert response.meta["cached"] is True

    def test_api_response_timestamp_utc(self, sample_user):
        """Test that timestamp is in UTC timezone."""
        response = ApiResponse[SampleUser](data=sample_user)

        assert response.timestamp.tzinfo == timezone.utc

    def test_api_response_success_always_true(self, sample_user):
        """Test that success field is always True."""
        response = ApiResponse[SampleUser](data=sample_user)

        assert response.success is True

    def test_api_response_serialization(self, sample_user):
        """Test ApiResponse JSON serialization."""
        response = ApiResponse[SampleUser](data=sample_user)

        json_data = response.model_dump()

        assert json_data["success"] is True
        assert json_data["data"]["id"] == "123"
        assert json_data["data"]["name"] == "John Doe"
        assert "timestamp" in json_data

    def test_api_response_with_list_data(self, sample_users):
        """Test ApiResponse with list of items."""
        response = ApiResponse[list[SampleUser]](data=sample_users)

        assert response.success is True
        assert len(response.data) == 3
        assert response.data[0].name == "Alice"

    def test_api_response_with_primitive_types(self):
        """Test ApiResponse with primitive data types."""
        # String
        str_response = ApiResponse[str](data="Hello World")
        assert str_response.data == "Hello World"

        # Integer
        int_response = ApiResponse[int](data=42)
        assert int_response.data == 42

        # Boolean
        bool_response = ApiResponse[bool](data=True)
        assert bool_response.data is True


# ─── PaginatedResponse Tests ───────────────────────────────────────────────────


class TestPaginatedResponse:
    """Test suite for PaginatedResponse model."""

    def test_create_paginated_response(self, sample_users):
        """Test creating PaginatedResponse with all fields."""
        response = PaginatedResponse[SampleUser](
            items=sample_users, total=50, page=1, page_size=10, has_next=True
        )

        assert len(response.items) == 3
        assert response.total == 50
        assert response.page == 1
        assert response.page_size == 10
        assert response.has_next is True

    def test_paginated_response_total_pages_property(self, sample_users):
        """Test total_pages computed property."""
        response = PaginatedResponse[SampleUser](
            items=sample_users, total=50, page=1, page_size=10, has_next=True
        )

        assert response.total_pages == 5

    def test_paginated_response_total_pages_partial(self, sample_users):
        """Test total_pages with partial last page."""
        response = PaginatedResponse[SampleUser](
            items=sample_users, total=47, page=1, page_size=10, has_next=True
        )

        assert response.total_pages == 5  # Ceiling division

    def test_paginated_response_total_pages_zero_items(self):
        """Test total_pages when there are no items."""
        response = PaginatedResponse[SampleUser](
            items=[], total=0, page=1, page_size=10, has_next=False
        )

        assert response.total_pages == 0

    def test_paginated_response_auto_compute_has_next_true(self, sample_users):
        """Test auto-computation of has_next when there are more pages."""
        # Page 1 of 5 (50 total items, 10 per page)
        response = PaginatedResponse[SampleUser](
            items=sample_users,
            total=50,
            page=1,
            page_size=10,
            has_next=True,  # Explicitly provided
        )

        assert response.has_next is True

    def test_paginated_response_auto_compute_has_next_false(self, sample_users):
        """Test auto-computation of has_next on last page."""
        # Last page (page 5 of 5)
        response = PaginatedResponse[SampleUser](
            items=sample_users,
            total=50,
            page=5,
            page_size=10,
            has_next=False,  # Explicitly provided
        )

        assert response.has_next is False

    def test_paginated_response_first_page(self, sample_users):
        """Test first page response."""
        response = PaginatedResponse[SampleUser](
            items=sample_users, total=100, page=1, page_size=10, has_next=True
        )

        assert response.page == 1
        assert response.has_next is True

    def test_paginated_response_last_page(self, sample_users):
        """Test last page response."""
        response = PaginatedResponse[SampleUser](
            items=sample_users, total=23, page=3, page_size=10, has_next=False
        )

        assert response.page == 3
        assert response.has_next is False
        assert response.total_pages == 3

    def test_paginated_response_single_page(self, sample_users):
        """Test single page response (all items fit on one page)."""
        response = PaginatedResponse[SampleUser](
            items=sample_users, total=3, page=1, page_size=10, has_next=False
        )

        assert response.total_pages == 1
        assert response.has_next is False

    def test_paginated_response_empty_page(self):
        """Test empty page response."""
        response = PaginatedResponse[SampleUser](
            items=[], total=0, page=1, page_size=10, has_next=False
        )

        assert len(response.items) == 0
        assert response.total == 0
        assert response.total_pages == 0

    def test_paginated_response_validation_negative_total(self, sample_users):
        """Test that negative total is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PaginatedResponse[SampleUser](
                items=sample_users,
                total=-1,
                page=1,
                page_size=10,
                has_next=False,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("total",) for e in errors)

    def test_paginated_response_validation_page_zero(self, sample_users):
        """Test that page 0 is rejected (1-indexed)."""
        with pytest.raises(ValidationError) as exc_info:
            PaginatedResponse[SampleUser](
                items=sample_users,
                total=50,
                page=0,
                page_size=10,
                has_next=True,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("page",) for e in errors)

    def test_paginated_response_validation_page_size_zero(self, sample_users):
        """Test that page_size 0 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PaginatedResponse[SampleUser](
                items=sample_users,
                total=50,
                page=1,
                page_size=0,
                has_next=True,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("page_size",) for e in errors)

    def test_paginated_response_validation_page_size_too_large(
        self, sample_users
    ):
        """Test that page_size > 100 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PaginatedResponse[SampleUser](
                items=sample_users,
                total=1000,
                page=1,
                page_size=101,
                has_next=True,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("page_size",) for e in errors)

    def test_paginated_response_max_page_size(self, sample_users):
        """Test that page_size of exactly 100 is accepted."""
        response = PaginatedResponse[SampleUser](
            items=sample_users, total=1000, page=1, page_size=100, has_next=True
        )

        assert response.page_size == 100

    def test_paginated_response_serialization(self, sample_users):
        """Test PaginatedResponse JSON serialization."""
        response = PaginatedResponse[SampleUser](
            items=sample_users, total=50, page=1, page_size=10, has_next=True
        )

        json_data = response.model_dump()

        assert "items" in json_data
        assert len(json_data["items"]) == 3
        assert json_data["total"] == 50
        assert json_data["page"] == 1
        assert json_data["page_size"] == 10
        assert json_data["has_next"] is True
        # Note: total_pages is a property, not a field, so it won't be in model_dump


# ─── Integration Tests ─────────────────────────────────────────────────────────


class TestResponseIntegration:
    """Integration tests for response models."""

    def test_api_response_with_paginated_data(self, sample_users):
        """Test wrapping paginated response in ApiResponse."""
        paginated = PaginatedResponse[SampleUser](
            items=sample_users, total=50, page=1, page_size=10, has_next=True
        )
        response = ApiResponse[PaginatedResponse[SampleUser]](data=paginated)

        assert response.success is True
        assert response.data.total == 50
        assert response.data.page == 1
        assert len(response.data.items) == 3

    def test_complete_success_response_structure(self, sample_user):
        """Test complete success response structure matches spec."""
        response = ApiResponse[SampleUser](
            data=sample_user,
            meta={"cached": False, "query_time_ms": 45},
        )

        json_data = response.model_dump()

        # Verify structure matches spec
        assert "success" in json_data
        assert "data" in json_data
        assert "meta" in json_data
        assert "timestamp" in json_data

        assert json_data["success"] is True
        assert isinstance(json_data["data"], dict)
        assert isinstance(json_data["meta"], dict)

    def test_complete_error_response_structure(self):
        """Test complete error response structure matches spec."""
        error = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Invalid input data",
            details={"field": "email", "constraint": "format"},
        )
        response = ErrorResponse(error=error)

        json_data = response.model_dump()

        # Verify structure matches spec
        assert "success" in json_data
        assert "error" in json_data
        assert "timestamp" in json_data

        assert json_data["success"] is False
        assert "code" in json_data["error"]
        assert "message" in json_data["error"]
        assert "details" in json_data["error"]

    def test_response_timestamp_consistency(self, sample_user):
        """Test that timestamps are consistent across response types."""
        success_response = ApiResponse[SampleUser](data=sample_user)
        error_response = ErrorResponse(
            error=ErrorDetail(code="ERROR", message="Test")
        )

        # Both should have UTC timestamps
        assert success_response.timestamp.tzinfo == timezone.utc
        assert error_response.timestamp.tzinfo == timezone.utc

        # Timestamps should be close (within 1 second)
        time_diff = abs(
            (
                success_response.timestamp - error_response.timestamp
            ).total_seconds()
        )
        assert time_diff < 1.0
