"""Branch Management API Router"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUserDep, DbSessionDep
from app.api.schemas.branch import *
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.responses import ApiResponse, PaginatedResponse
from app.application.services.branch_service import BranchService, get_branch_service
from app.domain.value_objects.enums import Role

router = APIRouter(prefix="/branches", tags=["branches"])

@router.post("", response_model=ApiResponse[BranchResponse], status_code=status.HTTP_201_CREATED)
async def create_branch(
    data: BranchCreateRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: BranchService = Depends(get_branch_service)
):
    """Create branch (SUPER_ADMIN only)"""
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    branch = await service.create_branch(
        data.name, data.location, data.address, data.phone, data.description, db
    )
    return ApiResponse(data=BranchResponse.from_orm(branch))

@router.get("/{branch_id}", response_model=ApiResponse[BranchResponse])
async def get_branch(
    branch_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: BranchService = Depends(get_branch_service)
):
    """Get branch details"""
    branch = await service.get_branch(branch_id, db)
    return ApiResponse(data=BranchResponse.from_orm(branch))

@router.get("", response_model=ApiResponse[PaginatedResponse[BranchResponse]])
async def list_branches(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: BranchService = Depends(get_branch_service)
):
    """List all branches"""
    branches, total = await service.list_branches(pagination.offset, pagination.limit, db)
    items = [BranchResponse.from_orm(b) for b in branches]
    return ApiResponse(data=PaginatedResponse(
        items=items, total=total, page=pagination.page,
        page_size=pagination.page_size,
        has_next=(pagination.page * pagination.page_size) < total
    ))

@router.patch("/{branch_id}", response_model=ApiResponse[BranchResponse])
async def update_branch(
    branch_id: str,
    data: BranchUpdateRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: BranchService = Depends(get_branch_service)
):
    """Update branch"""
    updates = data.dict(exclude_unset=True)
    branch = await service.update_branch(branch_id, updates, db)
    return ApiResponse(data=BranchResponse.from_orm(branch))

@router.post("/{branch_id}/coordinator", response_model=ApiResponse[BranchResponse])
async def assign_coordinator(
    branch_id: str,
    data: CoordinatorAssignmentRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: BranchService = Depends(get_branch_service)
):
    """Assign coordinator"""
    branch = await service.assign_coordinator(branch_id, data.coordinator_id, db)
    return ApiResponse(data=BranchResponse.from_orm(branch))

@router.get("/{branch_id}/statistics", response_model=ApiResponse[BranchStatisticsResponse])
async def get_statistics(
    branch_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: BranchService = Depends(get_branch_service)
):
    """Get branch statistics"""
    stats = await service.get_statistics(branch_id, db)
    return ApiResponse(data=BranchStatisticsResponse(**stats))
