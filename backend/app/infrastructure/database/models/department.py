"""Department Model"""

from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base, TimestampMixin


class DepartmentModel(Base, TimestampMixin):
    """Department model within a branch"""

    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    branch_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("branches.id", ondelete="CASCADE", name="fk_departments_branch"),
        nullable=False,
    )
    leader_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL", name="fk_departments_leader"),
        nullable=True,
    )

    branch = relationship(
        "BranchModel", foreign_keys=[branch_id], back_populates="departments"
    )
    leader = relationship(
        "UserModel", foreign_keys=[leader_id], backref="led_department"
    )
    members = relationship(
        "UserModel", foreign_keys="UserModel.department_id", back_populates="department"
    )
    youths = relationship("YouthModel", back_populates="department")

    __table_args__ = (
        Index("ix_departments_branch_id", "branch_id"),
        {"comment": "Branch departments"},
    )
