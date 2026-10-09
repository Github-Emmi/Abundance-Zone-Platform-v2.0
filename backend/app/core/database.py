"""
Database Configuration Module
Async SQLAlchemy setup for Neon PostgreSQL with connection pooling
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Import Base from models (not duplicate definition)
from app.infrastructure.database.models.base import Base

# Import all models so Alembic can detect them
from app.infrastructure.database.models import (
    UserModel,
    BranchModel,
    DepartmentModel,
    YouthModel,
    EventModel,
    AttendanceModel,
    PledgeModel,
    PaymentModel,
    NotificationModel,
    RefreshTokenModel,
)


# ─── Create Async Engine for Neon ───────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in development
    pool_size=settings.DATABASE_POOL_SIZE,  # Connection pool size
    max_overflow=settings.DATABASE_MAX_OVERFLOW,  # Max extra connections
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    # Neon-specific: Use NullPool for serverless if needed
    # poolclass=NullPool if settings.is_production else None,
)

# ─── Create Async Session Factory ───────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autoflush=False,  # Manual flush control
    autocommit=False,  # Explicit transaction control
)


# ─── Database Session Dependency ─────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.
    Automatically commits on success, rolls back on error.
    
    Usage:
        @router.get("/youths")
        async def list_youths(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─── Database Lifecycle Functions ────────────────────────────────────────────
async def create_tables() -> None:
    """
    Create all database tables.
    Used during app startup in development only.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """
    Drop all database tables.
    WARNING: Use only in development/testing!
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db_connections() -> None:
    """
    Close all database connections.
    Called during app shutdown.
    """
    await engine.dispose()
