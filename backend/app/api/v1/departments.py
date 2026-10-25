"""Department Management API Router"""

from fastapi import Query, APIRouter, Depends, status
from app.api.deps import CurrentUserDep, DbSessionDep
from app.api.schemas.department import *
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.responses import ApiResponse, PaginatedResponse
from app.application.services.department_service import (
    DepartmentService,
    get_department_service,
)

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post(
    "",
    response_model=ApiResponse[DepartmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
    data: DepartmentCreateRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: DepartmentService = Depends(get_department_service),
):
    dept = await service.create_department(
        data.name, data.branch_id, data.description, db
    )
    return ApiResponse(data=DepartmentResponse.from_orm(dept))


@router.get("/{dept_id}", response_model=ApiResponse[DepartmentResponse])
async def get_department(
    dept_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: DepartmentService = Depends(get_department_service),
):
    dept = await service.get_department(dept_id, db)
    return ApiResponse(data=DepartmentResponse.from_orm(dept))


@router.get("", response_model=ApiResponse[PaginatedResponse[DepartmentResponse]])
async def list_departments(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    branch_id: str | None = Query(None),
    pagination: PaginationParams = Depends(get_pagination_params),
    service: DepartmentService = Depends(get_department_service),
):
    depts, total = await service.list_departments(
        branch_id, pagination.offset, pagination.limit, db
    )
    items = [DepartmentResponse.from_orm(d) for d in depts]
    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=(pagination.page * pagination.page_size) < total,
        )
    )


@router.post("/{dept_id}/leader", response_model=ApiResponse[DepartmentResponse])
async def assign_leader(
    dept_id: str,
    data: LeaderAssignmentRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: DepartmentService = Depends(get_department_service),
):
    dept = await service.assign_leader(dept_id, data.leader_id, db)
    return ApiResponse(data=DepartmentResponse.from_orm(dept))
