"""
Security Infrastructure Module
Contains JWT handling, password hashing, and permissions logic
"""

from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.security.password_hasher import (
    PasswordHasher,
    PasswordValidationError,
    get_password_hasher,
)
from app.infrastructure.security.permissions import (
    ROLE_HIERARCHY,
    can_access_branch,
    can_manage_department,
    can_modify_user_role,
    get_role_level,
    has_higher_or_equal_role,
    is_branch_coordinator,
    is_department_leader,
    is_super_admin,
    is_youth_member,
)

__all__ = [
    "JWTHandler",
    "PasswordHasher",
    "PasswordValidationError",
    "get_password_hasher",
    "ROLE_HIERARCHY",
    "can_access_branch",
    "can_manage_department",
    "can_modify_user_role",
    "get_role_level",
    "has_higher_or_equal_role",
    "is_branch_coordinator",
    "is_department_leader",
    "is_super_admin",
    "is_youth_member",
]
