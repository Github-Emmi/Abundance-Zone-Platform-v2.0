"""
Pagination Utilities

Provides reusable pagination parameters and dependency functions for list endpoints.
Implements FR-API-003: Pagination Standard.
"""

from typing import Literal

from fastapi import Query
from pydantic import BaseModel, Field, field_validator


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.

    Attributes:
        page: Current page number (1-indexed, minimum 1)
        page_size: Number of items per page (1-100)
        sort: Optional field name to sort by
        order: Sort order - "asc" (ascending) or "desc" (descending)

    Example:
        >>> params = PaginationParams(page=2, page_size=50)
        >>> params.offset  # Returns 50
        >>> params.limit   # Returns 50
    """

    page: int = Field(default=1, description="Page number (1-indexed)", ge=1)

    page_size: int = Field(
        default=20, description="Number of items per page", ge=1, le=100
    )

    sort: str | None = Field(
        default=None,
        description="Field name to sort by",
        examples=["created_at", "name", "email"],
    )

    order: Literal["asc", "desc"] = Field(
        default="desc", description="Sort order: ascending or descending"
    )

    @field_validator("page")
    @classmethod
    def validate_page(cls, v: int) -> int:
        """Validate page number is at least 1."""
        if v < 1:
            raise ValueError("Page number must be greater than or equal to 1")
        return v

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        """Validate page_size is between 1 and 100."""
        if v < 1:
            raise ValueError("Page size must be at least 1")
        if v > 100:
            raise ValueError("Page size cannot exceed 100")
        return v

    @property
    def offset(self) -> int:
        """
        Calculate the database offset based on page and page_size.

        Returns:
            The number of records to skip for the current page.

        Example:
            >>> PaginationParams(page=1, page_size=20).offset
            0
            >>> PaginationParams(page=3, page_size=20).offset
            40
        """
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """
        Get the maximum number of records to return.

        Returns:
            The page_size value to use as LIMIT in database queries.
        """
        return self.page_size

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"page": 1, "page_size": 20, "sort": "created_at", "order": "desc"},
                {"page": 2, "page_size": 50, "sort": "name", "order": "asc"},
            ]
        }
    }


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        20, ge=1, le=100, description="Number of items per page (max 100)"
    ),
    sort: str | None = Query(None, description="Field name to sort by"),
    order: Literal["asc", "desc"] = Query(
        "desc", description="Sort order: 'asc' or 'desc'"
    ),
) -> PaginationParams:
    """
    FastAPI dependency function for extracting pagination parameters from query string.

    This dependency can be injected into any list endpoint to provide standardized
    pagination functionality.

    Args:
        page: Page number (1-indexed), minimum 1
        page_size: Number of items per page, between 1 and 100
        sort: Optional field name to sort results by
        order: Sort order, either "asc" (ascending) or "desc" (descending)

    Returns:
        PaginationParams instance with validated pagination parameters

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from app.api.schemas.pagination import PaginationParams, get_pagination_params

        router = APIRouter()

        @router.get("/users")
        async def list_users(
            pagination: PaginationParams = Depends(get_pagination_params)
        ):
            # Use pagination.offset and pagination.limit in database query
            users = await db.query(User).offset(pagination.offset).limit(pagination.limit)
            return {"users": users, "page": pagination.page}
        ```

    Query Parameters:
        - ?page=2&page_size=50&sort=name&order=asc

    Validation:
        - Returns 422 if page < 1
        - Returns 422 if page_size < 1 or page_size > 100
        - Returns 422 if order not in ["asc", "desc"]
    """
    return PaginationParams(page=page, page_size=page_size, sort=sort, order=order)
