"""Youth Model"""

from typing import Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base, TimestampMixin
from app.domain.value_objects.enums import Gender, MembershipStatus


class YouthModel(Base, TimestampMixin):
    __tablename__ = "youths"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    fullname: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    gender: Mapped[str] = mapped_column(
        SQLEnum(Gender, name="youth_gender"), nullable=False
    )
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    profile_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    membership_status: Mapped[str] = mapped_column(
        SQLEnum(MembershipStatus, name="membership_status"),
        default=MembershipStatus.ACTIVE,
    )
    attendance_rate: Mapped[float] = mapped_column(default=0.0, nullable=False)

    branch_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("branches.id"), nullable=False
    )
    department_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )

    branch = relationship("BranchModel", back_populates="youths")
    department = relationship("DepartmentModel", back_populates="youths")
    attendance_records = relationship(
        "AttendanceModel", back_populates="youth", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_youths_branch_id", "branch_id"),
        Index("ix_youths_status", "membership_status"),
        {"comment": "Youth members"},
    )
