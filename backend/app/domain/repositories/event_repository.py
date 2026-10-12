"""
Event Repository Interface (Domain Layer)
Abstract protocol for event data access operations
"""

from typing import Protocol
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.event import EventModel


class IEventRepository(Protocol):
    """
    Event repository interface defining data access contract.

    Implementations must handle CRUD operations, RSVP management, and recurring events.
    """

    async def get_by_id(self, event_id: str, db: AsyncSession) -> EventModel | None:
        """Get event by ID."""
        ...

    async def list_by_branch(
        self, branch_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[EventModel], int]:
        """List events for a specific branch with pagination."""
        ...

    async def list_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        branch_id: str | None,
        offset: int,
        limit: int,
        db: AsyncSession,
    ) -> tuple[list[EventModel], int]:
        """List events within a date range, optionally filtered by branch."""
        ...

    async def save(self, event: EventModel, db: AsyncSession) -> EventModel:
        """Create or update an event."""
        ...

    async def delete(self, event_id: str, db: AsyncSession) -> bool:
        """Delete an event."""
        ...

    async def create_rsvp(
        self, event_id: str, user_id: str, status: str, db: AsyncSession
    ) -> dict:
        """
        Create or update an RSVP for an event.
        Status: GOING, MAYBE, NOT_GOING
        """
        ...

    async def update_rsvp(
        self, event_id: str, user_id: str, status: str, db: AsyncSession
    ) -> dict:
        """Update an existing RSVP status."""
        ...

    async def get_attendees(
        self, event_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[dict], int]:
        """
        Get list of attendees who RSVP'd to an event.

        Returns list of dicts with:
        - user_id: str
        - user_name: str
        - rsvp_status: str
        - rsvp_at: datetime
        """
        ...

    async def create_recurring(
        self, base_event: EventModel, recurrence_pattern: dict, db: AsyncSession
    ) -> list[EventModel]:
        """
        Create recurring event series based on a pattern.

        recurrence_pattern dict contains:
        - frequency: "daily" | "weekly" | "monthly"
        - interval: int (every N days/weeks/months)
        - end_date: datetime
        - occurrences: int | None (max number of occurrences)
        """
        ...
