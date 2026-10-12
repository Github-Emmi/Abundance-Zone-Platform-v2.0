"""Event Management API Router"""

from fastapi import APIRouter, Depends, status
from app.api.deps import CurrentUserDep, DbSessionDep
from app.api.schemas.event import *
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.responses import ApiResponse, PaginatedResponse
from app.application.services.event_service import EventService, get_event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post(
    "", response_model=ApiResponse[EventResponse], status_code=status.HTTP_201_CREATED
)
async def create_event(
    data: EventCreateRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: EventService = Depends(get_event_service),
):
    event = await service.create_event(
        data.title,
        data.event_type,
        data.event_date,
        data.branch_id,
        current_user.id,
        data.description,
        data.venue,
        data.end_date,
        db,
    )
    return ApiResponse(data=EventResponse.from_orm(event))


@router.get("/{event_id}", response_model=ApiResponse[EventResponse])
async def get_event(
    event_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: EventService = Depends(get_event_service),
):
    event = await service.get_event(event_id, db)
    return ApiResponse(data=EventResponse.from_orm(event))


@router.get("", response_model=ApiResponse[PaginatedResponse[EventResponse]])
async def list_events(
    branch_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: EventService = Depends(get_event_service),
):
    events, total = await service.list_events(
        branch_id, pagination.offset, pagination.limit, db
    )
    items = [EventResponse.from_orm(e) for e in events]
    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=(pagination.page * pagination.page_size) < total,
        )
    )
