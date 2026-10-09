"""Smoke Tests - Verify application loads and basic functionality"""
import pytest
from app.main import app
from app.infrastructure.security.password_hasher import PasswordHasher
from app.infrastructure.security.permissions import (
    can_access_branch,
    can_modify_user_role,
    get_role_level
)
from app.domain.value_objects.enums import Role


def test_app_loads():
    """Test that FastAPI app loads successfully"""
    assert app is not None
    assert app.title == "Abundance Zone Youth Platform"
    assert len(app.routes) > 40


def test_password_hasher():
    """Test password hashing functionality"""
    hasher = PasswordHasher()
    password = "SecurePass123!"
    
    # Test hashing
    hashed = hasher.hash_password(password)
    assert hashed is not None
    assert len(hashed) == 60  # bcrypt hash length
    
    # Test verification
    assert hasher.verify_password(password, hashed) is True
    assert hasher.verify_password("WrongPassword", hashed) is False


def test_password_complexity_validation():
    """Test password complexity requirements"""
    hasher = PasswordHasher()
    
    # Too short
    with pytest.raises(Exception):
        hasher.hash_password("Short1!")
    
    # No uppercase
    with pytest.raises(Exception):
        hasher.hash_password("lowercase123!")
    
    # No digit
    with pytest.raises(Exception):
        hasher.hash_password("NoDigits!")
    
    # No special char
    with pytest.raises(Exception):
        hasher.hash_password("NoSpecial123")


def test_role_hierarchy():
    """Test role hierarchy levels"""
    assert get_role_level(Role.SUPER_ADMIN) == 4
    assert get_role_level(Role.BRANCH_COORDINATOR) == 3
    assert get_role_level(Role.DEPARTMENT_LEADER) == 2
    assert get_role_level(Role.YOUTH_MEMBER) == 1


def test_branch_access_permissions():
    """Test branch access control"""
    # SUPER_ADMIN can access any branch
    assert can_access_branch(Role.SUPER_ADMIN, None, "branch-123") is True
    
    # BRANCH_COORDINATOR can only access own branch
    assert can_access_branch(
        Role.BRANCH_COORDINATOR, "branch-123", "branch-123"
    ) is True
    assert can_access_branch(
        Role.BRANCH_COORDINATOR, "branch-123", "branch-456"
    ) is False


def test_role_modification_permissions():
    """Test role assignment permissions"""
    # SUPER_ADMIN can assign any role
    assert can_modify_user_role(
        Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR
    ) is True
    
    # BRANCH_COORDINATOR can only assign lower roles
    assert can_modify_user_role(
        Role.BRANCH_COORDINATOR, Role.DEPARTMENT_LEADER
    ) is True
    assert can_modify_user_role(
        Role.BRANCH_COORDINATOR, Role.BRANCH_COORDINATOR
    ) is False
    
    # DEPARTMENT_LEADER cannot assign any roles
    assert can_modify_user_role(
        Role.DEPARTMENT_LEADER, Role.YOUTH_MEMBER
    ) is False


def test_api_routes_registered():
    """Test that all expected routes are registered"""
    route_paths = [route.path for route in app.routes]
    
    # Auth routes
    assert "/api/v1/auth/register" in route_paths
    assert "/api/v1/auth/login" in route_paths
    assert "/api/v1/auth/me" in route_paths
    
    # User routes
    assert "/api/v1/users" in route_paths
    
    # Branch routes
    assert "/api/v1/branches" in route_paths
    
    # Youth routes
    assert "/api/v1/youths" in route_paths
    
    # Event routes
    assert "/api/v1/events" in route_paths
    
    # Attendance routes
    assert "/api/v1/attendance" in route_paths
    
    # Notification routes
    assert "/api/v1/notifications" in route_paths


def test_pagination_params():
    """Test pagination parameter validation"""
    from app.api.schemas.pagination import PaginationParams
    
    # Valid params
    params = PaginationParams(page=1, page_size=20)
    assert params.offset == 0
    assert params.limit == 20
    
    params = PaginationParams(page=3, page_size=10)
    assert params.offset == 20
    assert params.limit == 10
    
    # Invalid params
    with pytest.raises(Exception):
        PaginationParams(page=0, page_size=20)  # page < 1
    
    with pytest.raises(Exception):
        PaginationParams(page=1, page_size=101)  # page_size > 100


def test_response_schemas():
    """Test response schema structures"""
    from app.api.schemas.responses import ApiResponse, ErrorResponse, ErrorDetail
    
    # Success response
    response = ApiResponse(data={"test": "data"})
    assert response.success is True
    assert response.data == {"test": "data"}
    
    # Error response
    error = ErrorDetail(code="TEST_ERROR", message="Test error message")
    error_response = ErrorResponse(error=error)
    assert error_response.success is False
    assert error_response.error.code == "TEST_ERROR"
