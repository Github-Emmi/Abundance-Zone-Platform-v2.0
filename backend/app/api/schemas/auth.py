"""
Authentication Schemas
Request/Response models for authentication endpoints
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.value_objects.enums import Role


class LoginRequest(BaseModel):
    """Login request payload."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class RegisterRequest(BaseModel):
    """User registration request payload."""
    
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(
        ..., 
        min_length=8,
        description="Password (min 8 chars, 1 uppercase, 1 number, 1 special char)"
    )
    phone: str | None = Field(None, pattern=r'^\+?[1-9]\d{1,14}$', description="Phone number (E.164 format)")
    branch_id: str = Field(..., description="UUID of assigned branch")
    
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password complexity requirements."""
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least 1 uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least 1 number')
        if not re.search(r'[!@#$%^&*]', v):
            raise ValueError('Password must contain at least 1 special character (!@#$%^&*)')
        return v


class TokenResponse(BaseModel):
    """Token pair response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds


class UserInfo(BaseModel):
    """Basic user information in auth responses."""
    
    id: str
    name: str
    email: str
    role: Role
    branch_id: str | None
    department_id: str | None
    profile_image_url: str | None
    is_email_verified: bool
    is_active: bool
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login success response with tokens and user info."""
    
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserInfo


class RefreshRequest(BaseModel):
    """Token refresh request."""
    
    refresh_token: str = Field(..., description="Refresh token")


class ForgotPasswordRequest(BaseModel):
    """Password reset request."""
    
    email: EmailStr = Field(..., description="Email address")


class ResetPasswordRequest(BaseModel):
    """Password reset confirmation."""
    
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(
        ..., 
        min_length=8,
        description="New password"
    )
    
    @field_validator('new_password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password complexity requirements."""
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least 1 uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least 1 number')
        if not re.search(r'[!@#$%^&*]', v):
            raise ValueError('Password must contain at least 1 special character (!@#$%^&*)')
        return v
