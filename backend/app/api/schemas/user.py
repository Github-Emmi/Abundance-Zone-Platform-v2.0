"""
User Schemas
Request/Response models for user management endpoints
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.domain.value_objects.enums import Role


class UserCreate(BaseModel):
    """Create user request payload (admin only)."""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: str | None = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    role: Role = Field(default=Role.YOUTH_MEMBER)
    branch_id: str | None = Field(None, description="UUID of assigned branch")
    department_id: str | None = Field(None, description="UUID of assigned department")


class UserUpdate(BaseModel):
    """Update user request payload (partial update)."""

    name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    profile_image_url: str | None = None
    branch_id: str | None = None
    department_id: str | None = None


class RoleAssignmentRequest(BaseModel):
    """Role assignment request payload."""

    role: Role = Field(..., description="New role to assign")


class BranchAssignmentRequest(BaseModel):
    """Branch assignment request payload."""

    branch_id: str = Field(..., description="UUID of branch to assign")


class UserResponse(BaseModel):
    """User list item response."""

    id: str
    name: str
    email: str
    phone: str | None
    role: Role
    branch_id: str | None
    department_id: str | None
    profile_image_url: str | None
    is_email_verified: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BranchInfo(BaseModel):
    """Branch information in user detail."""

    id: str
    name: str
    location: str | None

    class Config:
        from_attributes = True


class DepartmentInfo(BaseModel):
    """Department information in user detail."""

    id: str
    name: str

    class Config:
        from_attributes = True


class UserDetail(BaseModel):
    """User detail response with relationships."""

    id: str
    name: str
    email: str
    phone: str | None
    role: Role
    branch: BranchInfo | None
    department: DepartmentInfo | None
    profile_image_url: str | None
    is_email_verified: bool
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
