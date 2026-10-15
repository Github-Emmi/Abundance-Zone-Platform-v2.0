"""
Authentication Service
Business logic for user authentication and authorization
"""

import logging
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.core.config import settings
from app.domain.value_objects.enums import Role
from app.infrastructure.repositories.user_repository import (
    UserRepository,
    get_user_repository,
)
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.security.password_hasher import (
    PasswordHasher,
    get_password_hasher,
)
from app.tasks.emails import (
    send_email_verification,
    send_password_reset_email,
    send_welcome_email,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service handling login, registration, token management."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repo = user_repository
        self.password_hasher = password_hasher

    async def register(self, payload: RegisterRequest, db: AsyncSession) -> dict:
        """Register a new user."""
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(payload.email, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash password
        hashed_password = self.password_hasher.hash_password(payload.password)

        # Create user
        user_data = {
            "name": payload.name,
            "email": payload.email,
            "password": hashed_password,
            "phone": payload.phone,
            "role": Role.YOUTH_MEMBER,
            "branch_id": payload.branch_id,
            "is_email_verified": False,
            "is_active": True,
        }

        user = await self.user_repo.create(user_data, db)

        # Generate email verification token
        verification_token = JWTHandler.create_access_token(
            {
                "sub": user.id,
                "email": user.email,
                "purpose": "email_verification",
            }
        )

        # Dispatch background email tasks (non-blocking)
        task_ids = {}
        try:
            welcome_task = send_welcome_email.delay(
                user_email=user.email, user_name=user.name, user_id=user.id
            )
            task_ids["welcome_email"] = welcome_task.id
            logger.info(
                f"Dispatched welcome email task {welcome_task.id} for user {user.id}"
            )
        except Exception as e:
            logger.warning(f"Failed to dispatch welcome email task: {e}")

        try:
            verification_task = send_email_verification.delay(
                user_email=user.email,
                user_name=user.name,
                verification_token=verification_token,
            )
            task_ids["verification_email"] = verification_task.id
            logger.info(
                f"Dispatched verification email task {verification_task.id} for user {user.id}"
            )
        except Exception as e:
            logger.warning(f"Failed to dispatch verification email task: {e}")

        return {
            "user_id": user.id,
            "email": user.email,
            "message": "Registration successful. Check your email for verification instructions.",
            "task_ids": task_ids,
        }

    async def login(self, payload: LoginRequest, db: AsyncSession) -> LoginResponse:
        """Authenticate user and issue tokens."""
        user = await self.user_repo.get_by_email(payload.email, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated",
            )

        if not self.password_hasher.verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Generate tokens
        token_pair = JWTHandler.create_token_pair(
            {
                "sub": user.id,
                "email": user.email,
                "role": user.role,
                "branch_id": user.branch_id,
            }
        )

        # Update last login
        await self.user_repo.update(
            user.id, {"last_login_at": datetime.now(timezone.utc)}, db
        )

        from app.api.schemas.auth import UserInfo

        return LoginResponse(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            token_type="Bearer",
            expires_in=token_pair.expires_in,
            user=UserInfo.model_validate(user),
        )

    async def refresh_tokens(self, refresh_token: str, db: AsyncSession) -> dict:
        """Refresh access token."""
        try:
            payload = JWTHandler.verify_refresh_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id, db)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        new_token_pair = JWTHandler.create_token_pair(
            {
                "sub": user.id,
                "email": user.email,
                "role": user.role,
                "branch_id": user.branch_id,
            }
        )

        return {
            "access_token": new_token_pair.access_token,
            "refresh_token": new_token_pair.refresh_token,
            "token_type": "Bearer",
            "expires_in": new_token_pair.expires_in,
        }

    async def verify_email(self, token: str, db: AsyncSession) -> dict:
        """Verify user email."""
        payload = JWTHandler.decode_token_unsafe(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )

        user_id = payload.get("sub")
        success = await self.user_repo.update_email_verified(user_id, True, db)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
            )

        return {"message": "Email verified successfully"}

    async def request_password_reset(self, email: str, db: AsyncSession) -> dict:
        """Request password reset email."""
        user = await self.user_repo.get_by_email(email, db)

        task_id = None
        if user and user.is_active:
            # Generate password reset token
            reset_token = JWTHandler.create_access_token(
                {"sub": user.id, "email": user.email, "purpose": "password_reset"}
            )

            # Dispatch password reset email task (non-blocking)
            try:
                reset_task = send_password_reset_email.delay(
                    user_email=user.email, user_name=user.name, reset_token=reset_token
                )
                task_id = reset_task.id
                logger.info(
                    f"Dispatched password reset email task {reset_task.id} for user {user.id}"
                )
            except Exception as e:
                logger.warning(f"Failed to dispatch password reset email task: {e}")

        # Always return success message (security - prevent email enumeration)
        return {
            "message": "If your email is registered, you will receive password reset instructions.",
            "task_id": task_id,
        }

    async def reset_password(
        self, token: str, new_password: str, db: AsyncSession
    ) -> dict:
        """Reset password."""
        try:
            payload = JWTHandler.verify_token(token, settings.JWT_SECRET_KEY)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        if payload.get("purpose") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
            )

        user_id = payload.get("sub")
        hashed_password = self.password_hasher.hash_password(new_password)
        success = await self.user_repo.update_password(user_id, hashed_password, db)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password",
            )

        return {"message": "Password reset successfully"}

    async def resend_verification_email(self, user_id: str, db: AsyncSession) -> dict:
        """Resend email verification link."""
        user = await self.user_repo.get_by_id(user_id, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified",
            )

        # Generate new verification token
        verification_token = JWTHandler.create_access_token(
            {
                "sub": user.id,
                "email": user.email,
                "purpose": "email_verification",
            }
        )

        # Dispatch verification email task (non-blocking)
        task_id = None
        try:
            verification_task = send_email_verification.delay(
                user_email=user.email,
                user_name=user.name,
                verification_token=verification_token,
            )
            task_id = verification_task.id
            logger.info(
                f"Dispatched resend verification email task {verification_task.id} for user {user.id}"
            )
        except Exception as e:
            logger.warning(f"Failed to dispatch verification email task: {e}")

        return {
            "message": "Verification email sent. Please check your inbox.",
            "task_id": task_id,
        }


# Dependency
def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> AuthService:
    """Get auth service for dependency injection."""
    return AuthService(user_repo, password_hasher)
