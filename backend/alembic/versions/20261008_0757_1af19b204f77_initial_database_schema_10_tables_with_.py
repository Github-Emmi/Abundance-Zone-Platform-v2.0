"""Initial database schema - 10 tables with circular FK fix

Revision ID: 1af19b204f77
Revises: 
Create Date: 2026-10-08 07:57:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1af19b204f77'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types first using DO blocks to check existence
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER', 'YOUTH_MEMBER');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE gender AS ENUM ('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE membership_status AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE event_type AS ENUM ('WORSHIP', 'FELLOWSHIP', 'TRAINING', 'OUTREACH', 'CONFERENCE', 'MEETING', 'OTHER');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE event_status AS ENUM ('DRAFT', 'SCHEDULED', 'ONGOING', 'COMPLETED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE attendance_status AS ENUM ('PRESENT', 'ABSENT', 'EXCUSED', 'LATE');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE pledge_type AS ENUM ('TITHE', 'OFFERING', 'BUILDING_FUND', 'MISSION', 'SPECIAL', 'OTHER');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE pledge_status AS ENUM ('PENDING', 'PARTIAL', 'COMPLETED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notification_type AS ENUM ('INFO', 'EVENT', 'REMINDER', 'ALERT', 'MESSAGE');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notification_channel AS ENUM ('EMAIL', 'SMS', 'PUSH', 'IN_APP');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notification_priority AS ENUM ('LOW', 'NORMAL', 'HIGH', 'URGENT');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notification_status AS ENUM ('QUEUED', 'SENT', 'DELIVERED', 'FAILED', 'READ');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Step 1: Create branches table WITHOUT coordinator_id FK
    op.create_table('branches',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='Branch name (must be unique)'),
        sa.Column('location', sa.String(length=255), nullable=False, comment='Branch location/city'),
        sa.Column('address', sa.String(length=500), nullable=True, comment='Full address'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='Branch contact phone'),
        sa.Column('description', sa.Text(), nullable=True, comment='Branch description'),
        sa.Column('logo_url', sa.String(length=500), nullable=True, comment='Branch logo URL'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Branch active status'),
        sa.Column('founded_at', sa.DateTime(timezone=True), nullable=True, comment='Branch founding date'),
        sa.Column('coordinator_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Branch coordinator user ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('coordinator_id'),
        comment='Organizational branches/locations'
    )
    op.create_index(op.f('ix_branches_is_active'), 'branches', ['is_active'], unique=False)
    
    # Step 2: Create departments table WITHOUT leader_id FK
    op.create_table('departments',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('branch_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('leader_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Branch departments'
    )
    op.create_index('ix_departments_branch_id', 'departments', ['branch_id'], unique=False)
    
    # Step 3: Create users table with branch_id and department_id FKs
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='Full name'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='Email address (unique login)'),
        sa.Column('password', sa.String(length=255), nullable=False, comment='Hashed password (bcrypt)'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='Phone number'),
        sa.Column('role', postgresql.ENUM('SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER', 'YOUTH_MEMBER', name='user_role', create_type=False), nullable=False, comment='User role for RBAC'),
        sa.Column('profile_image_url', sa.String(length=500), nullable=True, comment='Cloudinary/Firebase Storage URL'),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, comment='Email verification status'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Account active status'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True, comment='Last successful login timestamp'),
        sa.Column('branch_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Branch assignment'),
        sa.Column('department_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Department assignment'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='System users with role-based access control'
    )
    op.create_index(op.f('ix_users_branch_id'), 'users', ['branch_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    
    # Step 4: Add circular FKs now that all tables exist
    op.create_foreign_key('fk_branches_coordinator_id', 'branches', 'users', ['coordinator_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_departments_leader_id', 'departments', 'users', ['leader_id'], ['id'], ondelete='SET NULL')
    
    # Step 5: Create youths table
    op.create_table('youths',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', postgresql.ENUM('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY', name='gender', create_type=False), nullable=False),
        sa.Column('membership_status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING', name='membership_status', create_type=False), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('profile_image_url', sa.String(length=500), nullable=True),
        sa.Column('guardian_name', sa.String(length=200), nullable=True),
        sa.Column('guardian_phone', sa.String(length=20), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('branch_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Youth members'
    )
    op.create_index('ix_youths_branch_id', 'youths', ['branch_id'], unique=False)
    op.create_index('ix_youths_status', 'youths', ['membership_status'], unique=False)
    
    # Step 6: Create events table
    op.create_table('events',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', postgresql.ENUM('WORSHIP', 'FELLOWSHIP', 'TRAINING', 'OUTREACH', 'CONFERENCE', 'MEETING', 'OTHER', name='event_type', create_type=False), nullable=False),
        sa.Column('event_status', postgresql.ENUM('DRAFT', 'SCHEDULED', 'ONGOING', 'COMPLETED', 'CANCELLED', name='event_status', create_type=False), nullable=False),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('max_attendees', sa.Integer(), nullable=True),
        sa.Column('banner_url', sa.String(length=500), nullable=True),
        sa.Column('branch_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Youth events'
    )
    op.create_index('ix_events_date', 'events', ['event_date'], unique=False)
    op.create_index('ix_events_type', 'events', ['event_type'], unique=False)
    
    # Step 7: Create attendance table
    op.create_table('attendance',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('status', postgresql.ENUM('PRESENT', 'ABSENT', 'EXCUSED', 'LATE', name='attendance_status', create_type=False), nullable=False),
        sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('event_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('youth_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('marked_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['marked_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['youth_id'], ['youths.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'youth_id', name='uq_attendance_event_youth'),
        comment='Event attendance records'
    )
    op.create_index('ix_attendance_event', 'attendance', ['event_id'], unique=False)
    op.create_index('ix_attendance_youth', 'attendance', ['youth_id'], unique=False)
    
    # Step 8: Create pledges table
    op.create_table('pledges',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('pledge_type', postgresql.ENUM('TITHE', 'OFFERING', 'BUILDING_FUND', 'MISSION', 'SPECIAL', 'OTHER', name='pledge_type', create_type=False), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'PARTIAL', 'COMPLETED', 'CANCELLED', name='pledge_status', create_type=False), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Financial pledges'
    )
    op.create_index('ix_pledges_status', 'pledges', ['status'], unique=False)
    op.create_index('ix_pledges_user', 'pledges', ['user_id'], unique=False)
    
    # Step 9: Create payments table
    op.create_table('payments',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('transaction_id', sa.String(length=255), nullable=True),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('pledge_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.ForeignKeyConstraint(['pledge_id'], ['pledges.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Pledge payments'
    )
    op.create_index('ix_payments_pledge', 'payments', ['pledge_id'], unique=False)
    
    # Step 10: Create notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('type', postgresql.ENUM('INFO', 'EVENT', 'REMINDER', 'ALERT', 'MESSAGE', name='notification_type', create_type=False), nullable=False),
        sa.Column('channel', postgresql.ENUM('EMAIL', 'SMS', 'PUSH', 'IN_APP', name='notification_channel', create_type=False), nullable=False),
        sa.Column('priority', postgresql.ENUM('LOW', 'NORMAL', 'HIGH', 'URGENT', name='notification_priority', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('QUEUED', 'SENT', 'DELIVERED', 'FAILED', 'READ', name='notification_status', create_type=False), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('notification_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Additional metadata for the notification'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='User notifications'
    )
    op.create_index('ix_notifications_type', 'notifications', ['type'], unique=False)
    op.create_index('ix_notifications_user', 'notifications', ['user_id'], unique=False)
    
    # Step 11: Create refresh_tokens table
    op.create_table('refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='JWT refresh tokens'
    )
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)
    op.create_index('ix_refresh_tokens_user', 'refresh_tokens', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_refresh_tokens_user', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_token', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    
    op.drop_index('ix_notifications_user', table_name='notifications')
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_table('notifications')
    
    op.drop_index('ix_payments_pledge', table_name='payments')
    op.drop_table('payments')
    
    op.drop_index('ix_pledges_user', table_name='pledges')
    op.drop_index('ix_pledges_status', table_name='pledges')
    op.drop_table('pledges')
    
    op.drop_index('ix_attendance_youth', table_name='attendance')
    op.drop_index('ix_attendance_event', table_name='attendance')
    op.drop_table('attendance')
    
    op.drop_index('ix_events_type', table_name='events')
    op.drop_index('ix_events_date', table_name='events')
    op.drop_table('events')
    
    op.drop_index('ix_youths_status', table_name='youths')
    op.drop_index('ix_youths_branch_id', table_name='youths')
    op.drop_table('youths')
    
    op.drop_constraint('fk_departments_leader_id', 'departments', type_='foreignkey')
    op.drop_constraint('fk_branches_coordinator_id', 'branches', type_='foreignkey')
    
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_is_active'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_branch_id'), table_name='users')
    op.drop_table('users')
    
    op.drop_index('ix_departments_branch_id', table_name='departments')
    op.drop_table('departments')
    
    op.drop_index(op.f('ix_branches_is_active'), table_name='branches')
    op.drop_table('branches')
    
    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS notification_status")
    op.execute("DROP TYPE IF EXISTS notification_priority")
    op.execute("DROP TYPE IF EXISTS notification_channel")
    op.execute("DROP TYPE IF EXISTS notification_type")
    op.execute("DROP TYPE IF EXISTS pledge_status")
    op.execute("DROP TYPE IF EXISTS pledge_type")
    op.execute("DROP TYPE IF EXISTS attendance_status")
    op.execute("DROP TYPE IF EXISTS event_status")
    op.execute("DROP TYPE IF EXISTS event_type")
    op.execute("DROP TYPE IF EXISTS membership_status")
    op.execute("DROP TYPE IF EXISTS gender")
    op.execute("DROP TYPE IF EXISTS user_role")
