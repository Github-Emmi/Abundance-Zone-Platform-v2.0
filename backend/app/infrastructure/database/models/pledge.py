"""Pledge and Payment Models"""

from typing import Optional
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Index,
    Text,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base, TimestampMixin
from app.domain.value_objects.enums import PledgeType, PledgeStatus


class PledgeModel(Base, TimestampMixin):
    __tablename__ = "pledges"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    pledge_type: Mapped[str] = mapped_column(
        SQLEnum(PledgeType, name="pledge_type"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00")
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(PledgeStatus, name="pledge_status"), default=PledgeStatus.PLEDGED
    )
    project: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", name="fk_pledges_user"),
        nullable=False,
    )
    user = relationship("UserModel", back_populates="pledges")
    payments = relationship(
        "PaymentModel", back_populates="pledge", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_pledges_user", "user_id"),
        Index("ix_pledges_status", "status"),
        {"comment": "Financial pledges"},
    )


class PaymentModel(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    receipt_data: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="AI-parsed receipt data"
    )
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    pledge_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("pledges.id", ondelete="CASCADE"),
        nullable=False,
    )
    pledge = relationship("PledgeModel", back_populates="payments")

    __table_args__ = (
        Index("ix_payments_pledge", "pledge_id"),
        {"comment": "Pledge payments"},
    )
