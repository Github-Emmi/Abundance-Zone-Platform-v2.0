"""Event Management Service"""

from uuid import uuid4
from datetime import datetime
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.repositories.event_repository import (
    EventRepository,
    get_event_repository,
)
from app.infrastructure.database.models.event import EventModel
from app.domain.value_objects.enums import EventType, EventStatus


class EventService:
    def __init__(self, event_repo: EventRepository = Depends(get_event_repository)):
        self.event_repo = event_repo

    async def create_event(
        self,
        title: str,
        event_type: EventType,
        event_date: datetime,
        branch_id: str,
        created_by_id: str,
        description: str | None,
        venue: str | None,
        end_date: datetime | None,
        db: AsyncSession,
    ) -> EventModel:
        event = EventModel(
            id=str(uuid4()),
            title=title,
            event_type=event_type,
            event_date=event_date,
            branch_id=branch_id,
            created_by_id=created_by_id,
            description=description,
            venue=venue,
            end_date=end_date,
            status=EventStatus.DRAFT,
        )
        return await self.event_repo.save(event, db)

    async def get_event(self, event_id: str, db: AsyncSession) -> EventModel:
        event = await self.event_repo.get_by_id(event_id, db)
        if not event:
            raise NotFoundException(f"Event {event_id} not found")
        return event

    async def list_events(
        self, branch_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[EventModel], int]:
        return await self.event_repo.list_by_branch(branch_id, offset, limit, db)

    async def update_event(
        self, event_id: str, updates: dict, db: AsyncSession
    ) -> EventModel:
        event = await self.get_event(event_id, db)
        for key, value in updates.items():
            if hasattr(event, key):
                setattr(event, key, value)
        return await self.event_repo.save(event, db)

    async def delete_event(self, event_id: str, db: AsyncSession) -> bool:
        return await self.event_repo.delete(event_id, db)

    async def create_rsvp(
        self, event_id: str, user_id: str, status: str, db: AsyncSession
    ) -> dict:
        event = await self.get_event(event_id, db)
        return await self.event_repo.create_rsvp(event_id, user_id, status, db)

    async def update_rsvp(
        self, event_id: str, user_id: str, status: str, db: AsyncSession
    ) -> dict:
        return await self.event_repo.update_rsvp(event_id, user_id, status, db)

    async def list_attendees(
        self, event_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[dict], int]:
        return await self.event_repo.get_attendees(event_id, offset, limit, db)

    async def create_recurring_series(
        self, base_event: EventModel, recurrence_pattern: dict, db: AsyncSession
    ) -> list[EventModel]:
        return await self.event_repo.create_recurring(
            base_event, recurrence_pattern, db
        )


def get_event_service(
    event_repo: EventRepository = Depends(get_event_repository),
) -> EventService:
    return EventService(event_repo)
