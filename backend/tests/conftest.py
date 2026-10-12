"""
Test Fixtures and Configuration
Provides shared fixtures for integration tests
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.models.branch import BranchModel
from app.infrastructure.database.models.department import DepartmentModel
from app.infrastructure.database.models.youth import YouthModel
from app.infrastructure.database.models.event import EventModel
from app.infrastructure.security.password_hasher import PasswordHasher
from app.domain.value_objects.enums import (
    Role,
    Gender,
    MembershipStatus,
    EventType,
    EventStatus,
)


# Use DATABASE_URL from environment (set by CI)
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:test_password@localhost:5432/test_db"
)

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database override"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def password_hasher() -> PasswordHasher:
    """Create password hasher instance"""
    return PasswordHasher()


# ─── User Fixtures ───────────────────────────────────────────────────────────


@pytest.fixture
async def super_admin_user(
    db_session: AsyncSession, password_hasher: PasswordHasher
) -> UserModel:
    """Create super admin user"""
    from uuid import uuid4

    user = UserModel(
        id=str(uuid4()),
        name="Super Admin",
        email="admin@test.com",
        password=password_hasher.hash_password("Admin123!"),
        role=Role.SUPER_ADMIN.value,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def branch_coordinator_user(
    db_session: AsyncSession, password_hasher: PasswordHasher, test_branch: BranchModel
) -> UserModel:
    """Create branch coordinator user"""
    from uuid import uuid4

    user = UserModel(
        id=str(uuid4()),
        name="Branch Coordinator",
        email="coordinator@test.com",
        password=password_hasher.hash_password("Coord123!"),
        role=Role.BRANCH_COORDINATOR.value,
        branch_id=test_branch.id,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def department_leader_user(
    db_session: AsyncSession,
    password_hasher: PasswordHasher,
    test_branch: BranchModel,
    test_department: DepartmentModel,
) -> UserModel:
    """Create department leader user"""
    from uuid import uuid4

    user = UserModel(
        id=str(uuid4()),
        name="Department Leader",
        email="leader@test.com",
        password=password_hasher.hash_password("Leader123!"),
        role=Role.DEPARTMENT_LEADER.value,
        branch_id=test_branch.id,
        department_id=test_department.id,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ─── Authentication Fixtures ─────────────────────────────────────────────────


@pytest.fixture
async def super_admin_token(client: AsyncClient) -> str:
    """Get JWT token for super admin"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "Admin123!"},
    )
    assert response.status_code == 200
    data = response.json()
    return data["data"]["access_token"]


@pytest.fixture
async def coordinator_token(client: AsyncClient) -> str:
    """Get JWT token for branch coordinator"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "coordinator@test.com", "password": "Coord123!"},
    )
    assert response.status_code == 200
    data = response.json()
    return data["data"]["access_token"]


@pytest.fixture
def auth_headers(super_admin_token: str) -> dict:
    """Create authorization headers with super admin token"""
    return {"Authorization": f"Bearer {super_admin_token}"}


@pytest.fixture
def coordinator_headers(coordinator_token: str) -> dict:
    """Create authorization headers with coordinator token"""
    return {"Authorization": f"Bearer {coordinator_token}"}


# ─── Entity Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
async def test_branch(db_session: AsyncSession) -> BranchModel:
    """Create test branch"""
    from uuid import uuid4

    branch = BranchModel(
        id=str(uuid4()),
        name="Test Branch",
        location="Test City",
        address="123 Test St",
        phone="1234567890",
        is_active=True,
    )
    db_session.add(branch)
    await db_session.commit()
    await db_session.refresh(branch)
    return branch


@pytest.fixture
async def test_department(
    db_session: AsyncSession, test_branch: BranchModel
) -> DepartmentModel:
    """Create test department"""
    from uuid import uuid4

    dept = DepartmentModel(
        id=str(uuid4()),
        name="Test Department",
        branch_id=test_branch.id,
        description="Test department description",
        is_active=True,
    )
    db_session.add(dept)
    await db_session.commit()
    await db_session.refresh(dept)
    return dept


@pytest.fixture
async def test_youth(
    db_session: AsyncSession,
    test_branch: BranchModel,
    test_department: DepartmentModel,
) -> YouthModel:
    """Create test youth"""
    from uuid import uuid4

    youth = YouthModel(
        id=str(uuid4()),
        fullname="Test Youth",
        email="youth@test.com",
        phone="9876543210",
        gender=Gender.MALE.value,
        branch_id=test_branch.id,
        department_id=test_department.id,
        membership_status=MembershipStatus.ACTIVE.value,
        attendance_rate=0.0,
    )
    db_session.add(youth)
    await db_session.commit()
    await db_session.refresh(youth)
    return youth


@pytest.fixture
async def test_event(
    db_session: AsyncSession, test_branch: BranchModel, super_admin_user: UserModel
) -> EventModel:
    """Create test event"""
    from uuid import uuid4
    from datetime import datetime, timedelta

    event = EventModel(
        id=str(uuid4()),
        title="Test Event",
        description="Test event description",
        event_type=EventType.WORSHIP_SERVICE.value,
        status=EventStatus.PUBLISHED.value,
        event_date=datetime.utcnow() + timedelta(days=7),
        branch_id=test_branch.id,
        created_by_id=super_admin_user.id,
        venue="Test Venue",
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)
    return event
