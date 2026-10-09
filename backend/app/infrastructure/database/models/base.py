"""
Base SQLAlchemy Model
Provides common functionality for all models
"""

from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    
    # Type annotation for SQLAlchemy 2.0 style
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps to models.
    Apply to models that need automatic timestamp tracking.
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when record was last updated"
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary (for JSON serialization)"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
