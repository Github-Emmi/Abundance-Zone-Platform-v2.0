"""Final Comprehensive Tests for Coverage"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.domain.value_objects.enums import Role, Gender, EventType, NotificationType, AttendanceStatus, MembershipStatus
from app.infrastructure.security.permissions import get_role_level, is_super_admin, is_branch_coordinator, is_department_leader, is_youth_member
from app.infrastructure.security.password_hasher import PasswordHasher
from app.core.config import settings


class TestRoleHierarchy:
    """Test role hierarchy and levels"""
    
    def test_role_levels(self):
        assert get_role_level(Role.SUPER_ADMIN) == 4
        assert get_role_level(Role.BRANCH_COORDINATOR) == 3
        assert get_role_level(Role.DEPARTMENT_LEADER) == 2
        assert get_role_level(Role.YOUTH_MEMBER) == 1
    
    def test_role_level_string(self):
        assert get_role_level("SUPER_ADMIN") == 4
        assert get_role_level("YOUTH_MEMBER") == 1
    
    def test_invalid_role(self):
        assert get_role_level("INVALID") == 0
    
    def test_role_checks(self):
        assert is_super_admin(Role.SUPER_ADMIN) is True
        assert is_super_admin(Role.YOUTH_MEMBER) is False
        assert is_branch_coordinator(Role.BRANCH_COORDINATOR) is True
        assert is_department_leader(Role.DEPARTMENT_LEADER) is True
        assert is_youth_member(Role.YOUTH_MEMBER) is True


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_and_verify(self):
        hasher = PasswordHasher()
        password = "TestPassword123!"
        hashed = hasher.hash_password(password)
        assert hasher.verify_password(password, hashed) is True
    
    def test_wrong_password_fails(self):
        hasher = PasswordHasher()
        hashed = hasher.hash_password("Correct123!")
        assert hasher.verify_password("Wrong123!", hashed) is False
    
    def test_different_salts(self):
        hasher = PasswordHasher()
        h1 = hasher.hash_password("Same123!")
        h2 = hasher.hash_password("Same123!")
        assert h1 != h2
    
    def test_empty_password_rejected(self):
        hasher = PasswordHasher()
        with pytest.raises(ValueError):
            hasher.hash_password("")
    
    def test_hash_format(self):
        hasher = PasswordHasher()
        hashed = hasher.hash_password("Test123!")
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60


class TestEnums:
    """Test all enum definitions"""
    
    def test_role_enum(self):
        assert Role.SUPER_ADMIN.value == "SUPER_ADMIN"
        assert Role.BRANCH_COORDINATOR.value == "BRANCH_COORDINATOR"
        assert Role.DEPARTMENT_LEADER.value == "DEPARTMENT_LEADER"
        assert Role.YOUTH_MEMBER.value == "YOUTH_MEMBER"
    
    def test_gender_enum(self):
        assert Gender.MALE.value == "MALE"
        assert Gender.FEMALE.value == "FEMALE"
    
    def test_event_type_enum(self):
        assert EventType.SUNDAY_SERVICE.value == "SUNDAY_SERVICE"
        assert EventType.BIBLE_STUDY.value == "BIBLE_STUDY"
        assert EventType.WORKERS_MEETING.value == "WORKERS_MEETING"
    
    def test_notification_type_enum(self):
        assert NotificationType.ANNOUNCEMENT.value == "ANNOUNCEMENT"
        assert NotificationType.REMINDER.value == "REMINDER"
        assert NotificationType.ATTENDANCE_ALERT.value == "ATTENDANCE_ALERT"
    
    def test_attendance_status_enum(self):
        assert AttendanceStatus.PRESENT.value == "PRESENT"
        assert AttendanceStatus.ABSENT.value == "ABSENT"
        assert AttendanceStatus.LATE.value == "LATE"
    
    def test_membership_status_enum(self):
        assert MembershipStatus.ACTIVE.value == "ACTIVE"
        assert MembershipStatus.PENDING.value == "PENDING"
        assert MembershipStatus.INACTIVE.value == "INACTIVE"


class TestConfig:
    """Test configuration settings"""
    
    def test_app_settings_exist(self):
        assert settings.APP_NAME is not None
        assert settings.APP_VERSION is not None
        assert settings.ENVIRONMENT in ["development", "staging", "production"]
    
    def test_database_settings(self):
        assert settings.DATABASE_URL is not None
        assert settings.DATABASE_POOL_SIZE > 0
    
    def test_jwt_settings(self):
        assert settings.JWT_SECRET_KEY is not None
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS > 0
    
    def test_server_settings(self):
        assert settings.HOST is not None
        assert settings.PORT > 0


class TestDatabaseModels:
    """Test database model imports and structure"""
    
    def test_user_model(self):
        from app.infrastructure.database.models.user import UserModel
        assert UserModel.__tablename__ == "users"
    
    def test_branch_model(self):
        from app.infrastructure.database.models.branch import BranchModel
        assert BranchModel.__tablename__ == "branches"
    
    def test_youth_model(self):
        from app.infrastructure.database.models.youth import YouthModel
        assert YouthModel.__tablename__ == "youths"
    
    def test_event_model(self):
        from app.infrastructure.database.models.event import EventModel
        assert EventModel.__tablename__ == "events"
    
    def test_attendance_model(self):
        from app.infrastructure.database.models.attendance import AttendanceModel
        assert AttendanceModel.__tablename__ == "attendance"
    
    def test_department_model(self):
        from app.infrastructure.database.models.department import DepartmentModel
        assert DepartmentModel.__tablename__ == "departments"
    
    def test_notification_model(self):
        from app.infrastructure.database.models.notification import NotificationModel
        assert NotificationModel.__tablename__ == "notifications"
    
    def test_pledge_model(self):
        from app.infrastructure.database.models.pledge import PledgeModel
        assert PledgeModel.__tablename__ == "pledges"
    
    def test_refresh_token_model(self):
        from app.infrastructure.database.models.refresh_token import RefreshTokenModel
        assert RefreshTokenModel.__tablename__ == "refresh_tokens"


class TestSchemaImports:
    """Test schema imports work correctly"""
    
    def test_auth_schemas(self):
        from app.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
        assert LoginRequest is not None
        assert RegisterRequest is not None
        assert TokenResponse is not None
    
    def test_user_schemas(self):
        from app.api.schemas.user import UserCreate, UserUpdate, UserResponse
        assert UserCreate is not None
        assert UserUpdate is not None
        assert UserResponse is not None
    
    def test_branch_schemas(self):
        from app.api.schemas.branch import BranchCreateRequest, BranchUpdateRequest
        assert BranchCreateRequest is not None
        assert BranchUpdateRequest is not None
    
    def test_youth_schemas(self):
        from app.api.schemas.youth import YouthCreateRequest, YouthUpdateRequest
        assert YouthCreateRequest is not None
        assert YouthUpdateRequest is not None
    
    def test_event_schemas(self):
        from app.api.schemas.event import EventCreateRequest, EventUpdateRequest
        assert EventCreateRequest is not None
        assert EventUpdateRequest is not None


class TestServiceImports:
    """Test service layer imports"""
    
    def test_auth_service(self):
        from app.application.services.auth_service import AuthService
        assert AuthService is not None
    
    def test_user_service(self):
        from app.application.services.user_service import UserService
        assert UserService is not None
    
    def test_branch_service(self):
        from app.application.services.branch_service import BranchService
        assert BranchService is not None
    
    def test_youth_service(self):
        from app.application.services.youth_service import YouthService
        assert YouthService is not None
    
    def test_event_service(self):
        from app.application.services.event_service import EventService
        assert EventService is not None
    
    def test_attendance_service(self):
        from app.application.services.attendance_service import AttendanceService
        assert AttendanceService is not None
    
    def test_department_service(self):
        from app.application.services.department_service import DepartmentService
        assert DepartmentService is not None
    
    def test_notification_service(self):
        from app.application.services.notification_service import NotificationService
        assert NotificationService is not None


class TestRepositoryImports:
    """Test repository layer imports"""
    
    def test_user_repository(self):
        from app.infrastructure.repositories.user_repository import UserRepository
        assert UserRepository is not None
    
    def test_branch_repository(self):
        from app.infrastructure.repositories.branch_repository import BranchRepository
        assert BranchRepository is not None
    
    def test_youth_repository(self):
        from app.infrastructure.repositories.youth_repository import YouthRepository
        assert YouthRepository is not None
    
    def test_event_repository(self):
        from app.infrastructure.repositories.event_repository import EventRepository
        assert EventRepository is not None
    
    def test_attendance_repository(self):
        from app.infrastructure.repositories.attendance_repository import AttendanceRepository
        assert AttendanceRepository is not None
    
    def test_department_repository(self):
        from app.infrastructure.repositories.department_repository import DepartmentRepository
        assert DepartmentRepository is not None
    
    def test_notification_repository(self):
        from app.infrastructure.repositories.notification_repository import NotificationRepository
        assert NotificationRepository is not None


class TestExceptions:
    """Test custom exceptions"""
    
    def test_authentication_exception(self):
        from app.core.exceptions import AuthenticationException
        exc = AuthenticationException("Invalid credentials")
        assert "Invalid credentials" in str(exc)
    
    def test_authorization_exception(self):
        from app.core.exceptions import AuthorizationException
        exc = AuthorizationException("Access denied")
        assert "Access denied" in str(exc)
    
    def test_not_found_exception(self):
        from app.core.exceptions import NotFoundException
        exc = NotFoundException("Resource not found")
        assert "not found" in str(exc).lower()
    
    def test_validation_exception(self):
        from app.core.exceptions import ValidationException
        exc = ValidationException("Invalid data")
        assert "Invalid data" in str(exc)
