"""
Event Repository Implementation (Infrastructure Layer)
SQLAlchemy implementation of IEventRepository
"""

from datetime import datetime, timedelta
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.infrastructure.database.models.event import EventModel
from app.infrastructure.database.models.user import UserModel


class EventRepository:
    """SQLAlchemy implementation of event repository."""

    async def get_by_id(self, event_id: str, db: AsyncSession) -> EventModel | None:
        """Get event by ID with branch and creator loaded."""
        result = await db.execute(
            select(EventModel)
            .options(selectinload(EventModel.branch), selectinload(EventModel.creator))
            .where(EventModel.id == event_id)
        )
        return result.scalar_one_or_none()

    async def list_by_branch(
        self, branch_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[EventModel], int]:
        """List events for a specific branch with pagination."""
        # Get total count
        count_result = await db.execute(
            select(func.count())
            .select_from(EventModel)
            .where(EventModel.branch_id == branch_id)
        )
        total = count_result.scalar()

        # Get paginated results
        result = await db.execute(
            select(EventModel)
            .options(selectinload(EventModel.branch), selectinload(EventModel.creator))
            .where(EventModel.branch_id == branch_id)
            .offset(offset)
            .limit(limit)
            .order_by(EventModel.event_date.desc())
        )
        events = result.scalars().all()
        return list(events), total

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
        conditions = [
            EventModel.event_date >= start_date,
            EventModel.event_date <= end_date,
        ]
        if branch_id:
            conditions.append(EventModel.branch_id == branch_id)

        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(EventModel).where(and_(*conditions))
        )
        total = count_result.scalar()

        # Get paginated results
        result = await db.execute(
            select(EventModel)
            .options(selectinload(EventModel.branch), selectinload(EventModel.creator))
            .where(and_(*conditions))
            .offset(offset)
            .limit(limit)
            .order_by(EventModel.event_date.asc())
        )
        events = result.scalars().all()
        return list(events), total

    async def save(self, event: EventModel, db: AsyncSession) -> EventModel:
        """Create or update an event."""
        db.add(event)
        await db.flush()
        await db.refresh(event)
        return event

    async def delete(self, event_id: str, db: AsyncSession) -> bool:
        """Delete an event."""
        event = await self.get_by_id(event_id, db)
        if not event:
            return False

        await db.delete(event)
        await db.flush()
        return True

    async def create_rsvp(
        self, event_id: str, user_id: str, status: str, db: AsyncSession
    ) -> dict:
        """
        Create or update an RSVP for an event.
        Status: GOING, MAYBE, NOT_GOING

        Note: This is a simplified implementation.
        In a full implementation, you'd have a separate RSVP table/model.
        """
        # This is a placeholder - actual implementation would use RSVP model
        return {
            "event_id": event_id,
            "user_id": user_id,
            "status": status,
            "rsvp_at": datetime.utcnow(),
        }

    async def update_rsvp(
        self, event_id: str, user_id: str, status: str, db: AsyncSession
    ) -> dict:
        """Update an existing RSVP status."""
        # This is a placeholder - actual implementation would update RSVP model
        return await self.create_rsvp(event_id, user_id, status, db)

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
        # This is a placeholder - actual implementation would query RSVP table
        # For now, return empty list
        return [], 0

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
        frequency = recurrence_pattern.get("frequency", "weekly")
        interval = recurrence_pattern.get("interval", 1)
        end_date = recurrence_pattern.get("end_date")
        max_occurrences = recurrence_pattern.get(
            "occurrences", 52
        )  # Default 1 year of weekly events

        created_events = []
        current_date = base_event.event_date
        occurrence_count = 0

        while occurrence_count < max_occurrences:
            if frequency == "daily":
                current_date += timedelta(days=interval)
            elif frequency == "weekly":
                current_date += timedelta(weeks=interval)
            elif frequency == "monthly":
                # Simple monthly increment (doesn't handle edge cases perfectly)
                month = current_date.month + interval
                year = current_date.year + (month - 1) // 12
                month = ((month - 1) % 12) + 1
                current_date = current_date.replace(year=year, month=month)

            if end_date and current_date > end_date:
                break

            # Create new event instance
            from uuid import uuid4

            new_event = EventModel(
                id=str(uuid4()),
                title=base_event.title,
                description=base_event.description,
                event_type=base_event.event_type,
                status=base_event.status,
                event_date=current_date,
                end_date=(
                    current_date + (base_event.end_date - base_event.event_date)
                    if base_event.end_date
                    else None
                ),
                venue=base_event.venue,
                is_recurring=True,
                is_regional=base_event.is_regional,
                branch_id=base_event.branch_id,
                created_by_id=base_event.created_by_id,
            )

            db.add(new_event)
            created_events.append(new_event)
            occurrence_count += 1

        await db.flush()
        return created_events


def get_event_repository() -> EventRepository:
    """Factory function for dependency injection."""
    return EventRepository()
