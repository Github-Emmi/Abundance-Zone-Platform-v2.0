"""
User Repository Implementation (Infrastructure Layer)
SQLAlchemy implementation of IUserRepository
"""

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.infrastructure.database.models.user import UserModel


class UserRepository:
    """SQLAlchemy implementation of user repository."""
    
    async def create(self, user_data: dict, db: AsyncSession) -> UserModel:
        """Create a new user."""
        user = UserModel(**user_data)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: str, db: AsyncSession) -> UserModel | None:
        """Get user by ID with branch and department loaded."""
        result = await db.execute(
            select(UserModel)
            .options(
                selectinload(UserModel.branch),
                selectinload(UserModel.department)
            )
            .where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str, db: AsyncSession) -> UserModel | None:
        """Get user by email address."""
        result = await db.execute(
            select(UserModel)
            .options(
                selectinload(UserModel.branch),
                selectinload(UserModel.department)
            )
            .where(UserModel.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str, db: AsyncSession) -> UserModel | None:
        """Get user by phone number."""
        result = await db.execute(
            select(UserModel).where(UserModel.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def list_by_branch(
        self, 
        branch_id: str,
        offset: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[UserModel], int]:
        """List users in a specific branch with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(UserModel).where(UserModel.branch_id == branch_id)
        )
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            select(UserModel)
            .options(
                selectinload(UserModel.branch),
                selectinload(UserModel.department)
            )
            .where(UserModel.branch_id == branch_id)
            .offset(offset)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        users = result.scalars().all()
        
        return list(users), total
    
    async def list_by_role(
        self, 
        role: str,
        offset: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[UserModel], int]:
        """List users by role with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(UserModel).where(UserModel.role == role)
        )
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            select(UserModel)
            .options(
                selectinload(UserModel.branch),
                selectinload(UserModel.department)
            )
            .where(UserModel.role == role)
            .offset(offset)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        users = result.scalars().all()
        
        return list(users), total
    
    async def update(self, user_id: str, updates: dict, db: AsyncSession) -> UserModel:
        """Update user fields."""
        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        
        for key, value in updates.items():
            setattr(user, key, value)
        
        await db.flush()
        await db.refresh(user)
        return user
    
    async def update_password(self, user_id: str, hashed_password: str, db: AsyncSession) -> bool:
        """Update user password."""
        result = await db.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(password=hashed_password)
        )
        return result.rowcount > 0
    
    async def update_email_verified(self, user_id: str, verified: bool, db: AsyncSession) -> bool:
        """Update email verification status."""
        result = await db.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_email_verified=verified)
        )
        return result.rowcount > 0
    
    async def delete(self, user_id: str, db: AsyncSession) -> bool:
        """Soft delete user (set is_active = False)."""
        result = await db.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=False)
        )
        return result.rowcount > 0
    
    async def count_by_branch(self, branch_id: str, db: AsyncSession) -> int:
        """Count users in a branch."""
        result = await db.execute(
            select(func.count()).select_from(UserModel).where(UserModel.branch_id == branch_id)
        )
        return result.scalar()


# Dependency injection helper
def get_user_repository() -> UserRepository:
    """Get user repository instance for dependency injection."""
    return UserRepository()
