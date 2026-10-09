"""
User Management Service
Business logic for user CRUD operations
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.api.schemas.user import UserCreate, UserUpdate
from app.domain.value_objects.enums import Role
from app.infrastructure.repositories.user_repository import UserRepository, get_user_repository
from app.infrastructure.security.password_hasher import PasswordHasher, get_password_hasher
from app.infrastructure.security.permissions import can_modify_user_role


class UserService:
    """User management service."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repo = user_repository
        self.password_hasher = password_hasher
    
    async def create_user(
        self,
        payload: UserCreate,
        current_user: CurrentUser,
        db: AsyncSession
    ):
        """Create a new user."""
        existing = await self.user_repo.get_by_email(payload.email, db)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if not can_modify_user_role(current_user.role, payload.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot assign {payload.role.value} role"
            )
        
        hashed_password = self.password_hasher.hash_password(payload.password)
        
        user_data = payload.model_dump()
        user_data["password"] = hashed_password
        user_data["is_email_verified"] = True
        user_data["is_active"] = True
        
        user = await self.user_repo.create(user_data, db)
        return user
    
    async def get_user(self, user_id: str, current_user: CurrentUser, db: AsyncSession):
        """Get user by ID."""
        user = await self.user_repo.get_by_id(user_id, db)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if current_user.role == Role.SUPER_ADMIN:
            return user
        
        if current_user.role == Role.BRANCH_COORDINATOR:
            if user.branch_id != current_user.branch_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot view users from other branches"
                )
            return user
        
        if user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users"
            )
        
        return user
    
    async def list_users(
        self,
        branch_id: str | None,
        role: str | None,
        page: int,
        page_size: int,
        current_user: CurrentUser,
        db: AsyncSession
    ):
        """List users with pagination."""
        if current_user.role == Role.BRANCH_COORDINATOR:
            branch_id = current_user.branch_id
        
        offset = (page - 1) * page_size
        
        if role:
            return await self.user_repo.list_by_role(role, offset, page_size, db)
        elif branch_id:
            return await self.user_repo.list_by_branch(branch_id, offset, page_size, db)
        else:
            return [], 0
    
    async def update_user(
        self,
        user_id: str,
        payload: UserUpdate,
        current_user: CurrentUser,
        db: AsyncSession
    ):
        """Update user."""
        user = await self.user_repo.get_by_id(user_id, db)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        is_self = user_id == current_user.id
        is_admin = current_user.role in [Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]
        
        if not is_self and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update other users"
            )
        
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        updated_user = await self.user_repo.update(user_id, updates, db)
        
        return updated_user
    
    async def delete_user(self, user_id: str, current_user: CurrentUser, db: AsyncSession):
        """Soft delete user."""
        if current_user.role != Role.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only SUPER_ADMIN can delete users"
            )
        
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself"
            )
        
        success = await self.user_repo.delete(user_id, db)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deleted successfully"}
    
    async def assign_role(
        self,
        user_id: str,
        new_role: Role,
        current_user: CurrentUser,
        db: AsyncSession
    ):
        """Assign role to user."""
        if not can_modify_user_role(current_user.role, new_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot assign {new_role.value} role"
            )
        
        user = await self.user_repo.update(user_id, {"role": new_role}, db)
        return user
    
    async def assign_branch(
        self,
        user_id: str,
        branch_id: str,
        current_user: CurrentUser,
        db: AsyncSession
    ):
        """Assign user to branch."""
        if current_user.role != Role.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only SUPER_ADMIN can assign branches"
            )
        
        user = await self.user_repo.update(user_id, {"branch_id": branch_id}, db)
        return user


# Dependency
def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> UserService:
    """Get user service for dependency injection."""
    return UserService(user_repo, password_hasher)
