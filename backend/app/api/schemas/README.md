# API Response Schemas

## Overview

This module provides enterprise-grade standardized response schemas for all API endpoints in the Abundance Zone Platform. All API responses follow a consistent envelope structure for predictable client integration.

**Implements:** FR-API-001, FR-API-002

## Response Models

### 1. ApiResponse[T]

Generic success response envelope for all successful API operations.

**Structure:**
```json
{
  "success": true,
  "data": {...},
  "meta": {...},
  "timestamp": "2026-10-08T10:30:00Z"
}
```

**Fields:**
- `success`: Always `true` for successful responses
- `data`: Response payload of generic type T
- `meta`: Optional metadata (pagination info, warnings, cache status, etc.)
- `timestamp`: UTC timestamp when the response was generated

**Usage:**
```python
from app.api.schemas.responses import ApiResponse
from pydantic import BaseModel

class User(BaseModel):
    id: str
    name: str

user = User(id="123", name="John")
response = ApiResponse[User](
    data=user,
    meta={"cached": True}
)
```

### 2. ErrorResponse

Standardized error response envelope.

**Structure:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {...}
  },
  "timestamp": "2026-10-08T10:30:00Z"
}
```

**Fields:**
- `success`: Always `false` for error responses
- `error`: ErrorDetail object containing error information
- `timestamp`: UTC timestamp when the error occurred

**Usage:**
```python
from app.api.schemas.responses import ErrorResponse, ErrorDetail

error = ErrorDetail(
    code="NOT_FOUND",
    message="User not found",
    details={"user_id": "123"}
)
response = ErrorResponse(error=error)
```

### 3. ErrorDetail

Error detail model with structured error information.

**Fields:**
- `code`: Machine-readable error code (uppercase, e.g., "VALIDATION_ERROR")
- `message`: Human-readable error message for client display
- `details`: Optional dictionary with additional error context

**Common Error Codes:**
- `VALIDATION_ERROR`: Input validation failed
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `CONFLICT`: Resource conflict (e.g., duplicate email)
- `INTERNAL_ERROR`: Unexpected server error

### 4. PaginatedResponse[T]

Paginated list response with metadata.

**Structure:**
```json
{
  "items": [...],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "has_next": true
}
```

**Fields:**
- `items`: List of items for the current page
- `total`: Total number of items across all pages
- `page`: Current page number (1-indexed)
- `page_size`: Number of items per page (max: 100)
- `has_next`: Whether there are more pages available

**Computed Properties:**
- `total_pages`: Total number of pages (calculated from total and page_size)

**Usage:**
```python
from app.api.schemas.responses import PaginatedResponse

users = [User(id="1", name="Alice"), User(id="2", name="Bob")]
paginated = PaginatedResponse[User](
    items=users,
    total=50,
    page=1,
    page_size=10,
    has_next=True
)

# Access computed property
print(f"Total pages: {paginated.total_pages}")  # Output: 5
```

## Response Patterns

### Single Resource

```python
@router.get("/users/{user_id}")
async def get_user(user_id: str) -> ApiResponse[User]:
    user = await user_service.get_by_id(user_id)
    return ApiResponse[User](data=user)
```

### List of Resources (with pagination)

```python
@router.get("/users")
async def list_users(
    page: int = 1,
    page_size: int = 10
) -> ApiResponse[PaginatedResponse[User]]:
    paginated = await user_service.list_users(page, page_size)
    return ApiResponse[PaginatedResponse[User]](data=paginated)
```

### Error Handling

```python
from fastapi import HTTPException

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await user_service.get_by_id(user_id)
    if not user:
        error = ErrorDetail(
            code="NOT_FOUND",
            message=f"User with ID {user_id} not found"
        )
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error=error).model_dump()
        )
    return ApiResponse[User](data=user)
```

## Validation Rules

### ApiResponse
- `success` field is always `true` (enforced by Literal type)
- `data` field is required and strongly typed
- `meta` field is optional
- `timestamp` is auto-generated in UTC

### ErrorResponse
- `success` field is always `false` (enforced by Literal type)
- `error` field is required
- `timestamp` is auto-generated in UTC

### ErrorDetail
- `code` is automatically converted to uppercase
- `code` must be 1-100 characters
- `message` must be 1-500 characters
- `details` is optional

### PaginatedResponse
- `total` must be ≥ 0
- `page` must be ≥ 1 (1-indexed)
- `page_size` must be 1-100
- `has_next` is auto-computed if not provided

## Type Safety

All response models use Python generics and Pydantic v2 for full type safety:

```python
# Type checker understands User type
response: ApiResponse[User] = ApiResponse[User](data=user)
user_name: str = response.data.name  # ✓ Type safe

# Type checker understands list of Users
paginated: PaginatedResponse[User] = PaginatedResponse[User](...)
first_user: User = paginated.items[0]  # ✓ Type safe
```

## Testing

Comprehensive unit tests are available in `tests/unit/api/schemas/test_responses.py`:

- 43 test cases covering all models and edge cases
- 89% test coverage (exceeds 80% requirement)
- Tests for validation, serialization, and business logic

Run tests:
```bash
pytest tests/unit/api/schemas/test_responses.py -v
```

## Examples

See `app/api/schemas/examples.py` for complete working examples of all response types.

Run examples:
```bash
python -m app.api.schemas.examples
```

## Best Practices

1. **Always use response envelopes**: Never return raw data from endpoints
2. **Use appropriate HTTP status codes**: Match status codes to response types (200 for success, 404 for NOT_FOUND, etc.)
3. **Include metadata when relevant**: Use `meta` field for cache status, warnings, query performance metrics
4. **Provide detailed error information**: Use `details` field to help clients understand and fix errors
5. **Paginate large lists**: Always use `PaginatedResponse` for list endpoints that could return many items
6. **Use typed responses**: Specify the data type when creating responses for full type safety

## Related Documentation

- Requirements: `.kiro/requirements.md` (FR-API-001, FR-API-002)
- Design: `.kiro/design.md` (Section 2: Directory Structure)
- API Documentation: Available at `/docs` when server is running
