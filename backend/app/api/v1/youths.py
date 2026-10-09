"""Youth Management API Router"""
from fastapi import APIRouter, Depends, status
from app.api.deps import CurrentUserDep, DbSessionDep
from app.api.schemas.youth import *
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.responses import ApiResponse, PaginatedResponse
from app.application.services.youth_service import YouthService, get_youth_service

router = APIRouter(prefix="/youths", tags=["youths"])

@router.post("", response_model=ApiResponse[YouthResponse], status_code=status.HTTP_201_CREATED)
async def create_youth(
    data: YouthCreateRequest, current_user: CurrentUserDep, db: DbSessionDep,
    service: YouthService = Depends(get_youth_service)
):
    youth = await service.create_youth(
        data.fullname, data.branch_id, data.gender, data.email,
        data.phone, data.department_id, data.date_of_birth, db
    )
    return ApiResponse(data=YouthResponse.from_orm(youth))

@router.get("/{youth_id}", response_model=ApiResponse[YouthResponse])
async def get_youth(
    youth_id: str, current_user: CurrentUserDep, db: DbSessionDep,
    service: YouthService = Depends(get_youth_service)
):
    youth = await service.get_youth(youth_id, db)
    return ApiResponse(data=YouthResponse.from_orm(youth))

@router.get("", response_model=ApiResponse[PaginatedResponse[YouthResponse]])
async def list_youths(
    branch_id: str, current_user: CurrentUserDep, db: DbSessionDep,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: YouthService = Depends(get_youth_service)
):
    youths, total = await service.list_youths(branch_id, pagination.offset, pagination.limit, db)
    items = [YouthResponse.from_orm(y) for y in youths]
    return ApiResponse(data=PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size,
        has_next=(pagination.page * pagination.page_size) < total
    ))

@router.get("/search", response_model=ApiResponse[PaginatedResponse[YouthResponse]])
async def search_youths(
    query: str, branch_id: str | None, current_user: CurrentUserDep, db: DbSessionDep,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: YouthService = Depends(get_youth_service)
):
    youths, total = await service.search_youths(query, branch_id, pagination.offset, pagination.limit, db)
    items = [YouthResponse.from_orm(y) for y in youths]
    return ApiResponse(data=PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size,
        has_next=(pagination.page * pagination.page_size) < total
    ))
