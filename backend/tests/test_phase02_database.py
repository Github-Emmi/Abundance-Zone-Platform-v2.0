"""
Phase 02 Database Design Validation Tests
Tests database schema, models, and migrations
"""

import pytest
import asyncio
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine, AsyncSessionLocal
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


@pytest.mark.asyncio
async def test_database_connection():
    """Test that we can connect to Neon PostgreSQL database"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_all_tables_exist():
    """Test that all 10 application tables exist in the database"""
    expected_tables = {
        'users', 'branches', 'departments', 'youths', 'events',
        'attendance', 'pledges', 'payments', 'notifications', 'refresh_tokens'
    }
    
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """))
        tables = {row[0] for row in result}
    
    assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"


@pytest.mark.asyncio
async def test_enum_types_exist():
    """Test that all 12 ENUM types exist in the database"""
    expected_enums = {
        'user_role', 'gender', 'membership_status', 'event_type', 'event_status',
        'attendance_status', 'pledge_type', 'pledge_status', 'notification_type',
        'notification_channel', 'notification_priority', 'notification_status'
    }
    
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT typname 
            FROM pg_type 
            WHERE typcategory = 'E'
        """))
        enums = {row[0] for row in result}
    
    assert expected_enums.issubset(enums), f"Missing enums: {expected_enums - enums}"


@pytest.mark.asyncio
async def test_foreign_keys_exist():
    """Test that foreign key constraints are properly set up"""
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT 
                tc.table_name,
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name
        """))
        fks = list(result)
    
    # Should have at least 15 foreign keys across all tables
    assert len(fks) >= 15, f"Expected at least 15 foreign keys, got {len(fks)}"
    
    # Check specific critical FKs
    fk_dict = {(row[0], row[2]): row[3] for row in fks}
    assert fk_dict.get(('users', 'branch_id')) == 'branches'
    assert fk_dict.get(('youths', 'branch_id')) == 'branches'
    assert fk_dict.get(('attendance', 'event_id')) == 'events'
    assert fk_dict.get(('attendance', 'youth_id')) == 'youths'


@pytest.mark.asyncio
async def test_indexes_exist():
    """Test that indexes are created for common query columns"""
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT 
                tablename,
                indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """))
        indexes = [(row[0], row[1]) for row in result]
    
    # Check for critical indexes
    index_names = [idx[1] for idx in indexes]
    assert any('email' in idx for idx in index_names), "Missing email index"
    assert any('branch_id' in idx for idx in index_names), "Missing branch_id index"


@pytest.mark.asyncio
async def test_timestamp_columns():
    """Test that all models have created_at and updated_at columns"""
    tables_with_timestamps = [
        'users', 'branches', 'departments', 'youths', 'events',
        'attendance', 'pledges', 'payments', 'notifications', 'refresh_tokens'
    ]
    
    async with engine.connect() as conn:
        for table in tables_with_timestamps:
            result = await conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name IN ('created_at', 'updated_at')
            """))
            columns = [row[0] for row in result]
            assert 'created_at' in columns, f"Table {table} missing created_at"
            assert 'updated_at' in columns, f"Table {table} missing updated_at"


@pytest.mark.asyncio
async def test_circular_fk_constraints():
    """Test that circular foreign keys between branches, departments, and users are properly set"""
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name IN ('branches', 'departments', 'users')
        """))
        fks = [(row[0], row[1], row[2]) for row in result]
    
    # Check circular dependencies
    fk_set = set(fks)
    assert ('branches', 'coordinator_id', 'users') in fk_set, "Missing branches.coordinator_id → users"
    assert ('departments', 'leader_id', 'users') in fk_set, "Missing departments.leader_id → users"
    assert ('users', 'branch_id', 'branches') in fk_set, "Missing users.branch_id → branches"
    assert ('users', 'department_id', 'departments') in fk_set, "Missing users.department_id → departments"


def test_model_imports():
    """Test that all models can be imported successfully"""
    assert UserModel is not None
    assert BranchModel is not None
    assert DepartmentModel is not None
    assert YouthModel is not None
    assert EventModel is not None
    assert AttendanceModel is not None
    assert PledgeModel is not None
    assert PaymentModel is not None
    assert NotificationModel is not None
    assert RefreshTokenModel is not None


def test_model_table_names():
    """Test that models have correct table names"""
    assert UserModel.__tablename__ == 'users'
    assert BranchModel.__tablename__ == 'branches'
    assert DepartmentModel.__tablename__ == 'departments'
    assert YouthModel.__tablename__ == 'youths'
    assert EventModel.__tablename__ == 'events'
    assert AttendanceModel.__tablename__ == 'attendance'
    assert PledgeModel.__tablename__ == 'pledges'
    assert PaymentModel.__tablename__ == 'payments'
    assert NotificationModel.__tablename__ == 'notifications'
    assert RefreshTokenModel.__tablename__ == 'refresh_tokens'


@pytest.mark.asyncio
async def test_alembic_version():
    """Test that Alembic migration was applied"""
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
    
    assert version is not None, "No Alembic version found"
    assert version == '1af19b204f77', f"Unexpected Alembic version: {version}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
