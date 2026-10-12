"""
API Dependencies Module

Provides reusable FastAPI dependencies for authentication, authorization,
request context, and database session management.

Implements: FR-AUTH-008, FR-AUTH-010, FR-SEC-003
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.domain.value_objects.enums import Role
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.security.permissions import (
    can_access_branch,
    can_manage_department,
)


# ─── Security Scheme ────────────────────────────────────────────────────────

security = HTTPBearer()


# ─── Models ─────────────────────────────────────────────────────────────────


class CurrentUser(BaseModel):
    """Current authenticated user context."""

    id: str
    email: str
    name: str
    role: Role
    branch_id: str | None
    department_id: str | None
    is_active: bool
    is_email_verified: bool

    class Config:
        from_attributes = True


class RequestContext(BaseModel):
    """Complete request context for audit logging."""

    user_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    timestamp: datetime = datetime.now(timezone.utc)


# ─── Authentication Dependencies ────────────────────────────────────────────


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials

    try:
        payload = JWTHandler.verify_token(token, settings.JWT_SECRET_KEY)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return CurrentUser(
        id=user.id,
        email=user.email,
        name=user.name,
        role=Role(user.role),
        branch_id=user.branch_id,
        department_id=user.department_id,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
    )


def require_role(allowed_roles: list[Role]):
    """Dependency factory for role-based access control."""

    async def role_checker(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions",
            )
        return current_user

    return role_checker


def require_branch_access(target_branch_id: str | None = None):
    """Dependency factory for branch isolation enforcement."""

    async def branch_access_checker(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role == Role.SUPER_ADMIN:
            return current_user
        if not can_access_branch(
            current_user.role,
            current_user.branch_id,
            target_branch_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access this branch",
            )
        return current_user

    return branch_access_checker


def require_department_access(target_dept_id: str | None = None):
    """Dependency factory for department access enforcement."""

    async def department_access_checker(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if not can_manage_department(
            current_user.role,
            current_user.department_id,
            target_dept_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot manage this department",
            )
        return current_user

    return department_access_checker


# ─── Request Context Dependencies ───────────────────────────────────────────


async def get_client_ip(request: Request) -> str | None:
    """Extract client IP address from request."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    if request.client:
        return request.client.host

    return None


async def get_user_agent(request: Request) -> str | None:
    """Extract user agent string from request headers."""
    return request.headers.get("User-Agent")


async def get_request_context(
    request: Request,
    current_user: CurrentUser | None = None,
) -> RequestContext:
    """Build complete request context for audit logging."""
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)

    return RequestContext(
        user_id=current_user.id if current_user else None,
        ip_address=ip_address,
        user_agent=user_agent,
        timestamp=datetime.now(timezone.utc),
    )


# ─── Type Aliases ───────────────────────────────────────────────────────────

CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
ClientIpDep = Annotated[str | None, Depends(get_client_ip)]
UserAgentDep = Annotated[str | None, Depends(get_user_agent)]
RequestContextDep = Annotated[RequestContext, Depends(get_request_context)]
