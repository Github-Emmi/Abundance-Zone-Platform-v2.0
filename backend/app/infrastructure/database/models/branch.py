"""
Branch Model
Represents organizational branches (locations)
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.infrastructure.database.models.base import Base, TimestampMixin


class BranchModel(Base, TimestampMixin):
    """
    Branch model representing physical branch locations.
    Each branch has a coordinator and multiple departments.
    """
    
    __tablename__ = "branches"
    
    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    
    # Basic Info
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="Branch name (must be unique)"
    )
    
    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Branch location/city"
    )
    
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Full address"
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Branch contact phone"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Branch description"
    )
    
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Branch logo URL"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Branch active status"
    )
    
    founded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Branch founding date"
    )
    
    # Coordinator (Foreign Key)
    coordinator_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        comment="Branch coordinator user ID"
    )
    
    # Relationships
    coordinator = relationship(
        "UserModel",
        foreign_keys=[coordinator_id],
        backref="coordinated_branch"
    )
    
    members = relationship(
        "UserModel",
        foreign_keys="UserModel.branch_id",
        back_populates="branch"
    )
    
    youths = relationship(
        "YouthModel",
        back_populates="branch",
        cascade="all, delete-orphan"
    )
    
    departments = relationship(
        "DepartmentModel",
        back_populates="branch",
        cascade="all, delete-orphan"
    )
    
    events = relationship(
        "EventModel",
        back_populates="branch"
    )
    
    __table_args__ = (
        {"comment": "Organizational branches/locations"},
    )
    
    def __repr__(self) -> str:
        return f"<BranchModel(id={self.id}, name={self.name})>"
