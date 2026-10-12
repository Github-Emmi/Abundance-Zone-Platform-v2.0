"""
User Model
Represents system users (all roles: Super Admin, Coordinators, Leaders, Youth Members)
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.infrastructure.database.models.base import Base, TimestampMixin
from app.domain.value_objects.enums import Role


class UserModel(Base, TimestampMixin):
    """
    User model for authentication and authorization.
    Supports 4-tier RBAC: SUPER_ADMIN, BRANCH_COORDINATOR, DEPARTMENT_LEADER, YOUTH_MEMBER
    """

    __tablename__ = "users"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="Unique identifier",
    )

    # Basic Info
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Full name")

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email address (unique login)",
    )

    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Hashed password (bcrypt)"
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="Phone number"
    )

    # Role & Permissions
    role: Mapped[str] = mapped_column(
        SQLEnum(Role, name="user_role"),
        nullable=False,
        default=Role.YOUTH_MEMBER,
        index=True,
        comment="User role for RBAC",
    )

    # Profile
    profile_image_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="Cloudinary/Firebase Storage URL"
    )

    # Status Flags
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Email verification status"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Account active status",
    )

    # Authentication Tracking
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last successful login timestamp",
    )

    # Foreign Keys
    branch_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Branch assignment",
    )

    department_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        comment="Department assignment",
    )

    # Relationships
    branch = relationship(
        "BranchModel", foreign_keys=[branch_id], back_populates="members"
    )

    department = relationship(
        "DepartmentModel", foreign_keys=[department_id], back_populates="members"
    )

    # Reverse Relationships
    refresh_tokens = relationship(
        "RefreshTokenModel", back_populates="user", cascade="all, delete-orphan"
    )

    pledges = relationship(
        "PledgeModel", back_populates="user", cascade="all, delete-orphan"
    )

    notifications = relationship(
        "NotificationModel", back_populates="user", cascade="all, delete-orphan"
    )

    created_events = relationship(
        "EventModel", back_populates="creator", foreign_keys="EventModel.created_by_id"
    )

    # Indexes
    __table_args__ = ({"comment": "System users with role-based access control"},)

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"
