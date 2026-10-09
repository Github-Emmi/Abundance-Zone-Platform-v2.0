"""
User Management API Router
Endpoints for user CRUD operations and role management
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user, get_db, require_role
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.responses import ApiResponse, PaginatedResponse
from app.api.schemas.user import (
    BranchAssignmentRequest,
    RoleAssignmentRequest,
    UserCreate,
    UserDetail,
    UserResponse,
    UserUpdate,
)
from app.application.services.user_service import get_user_service
from app.domain.value_objects.enums import Role

router = APIRouter(tags=["User Management"])


@router.post("", response_model=ApiResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current_user: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
    user_service = Depends(get_user_service),
):
    """
    Create a new user (SUPER_ADMIN only).
    
    **Protected Endpoint** (SUPER_ADMIN only)
    
    **Business Rules:**
    - Only SUPER_ADMIN can create users
    - Email must be unique
    - Only SUPER_ADMIN can create BRANCH_COORDINATOR
    - Branch assignment required for non-SUPER_ADMIN roles
    - Admin-created users are pre-verified (no email verification needed)
    
    **Request Body:**
    - name: Full name
    - email: Email address
    - password: Password (will be hashed)
    - phone: Optional phone number
    - role: User role (default: YOUTH_MEMBER)
    - branch_id: Branch assignment (required for non-admin)
    - department_id: Optional department assignment
    
    **Returns:**
    - 201: User created successfully
    - 400: Email already exists or validation error
    - 403: Insufficient permissions to assign role
    """
    user = await user_service.create_user(payload, current_user, db)
    return ApiResponse(data=UserResponse.model_validate(user))


@router.get("/{user_id}", response_model=ApiResponse[UserDetail])
async def get_user(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    user_service = Depends(get_user_service),
):
    """
    Get user details by ID.
    
    **Protected Endpoint** (Authentication required)
    
    **Authorization Rules:**
    - SUPER_ADMIN: Can view any user
    - BRANCH_COORDINATOR: Can view users in their branch
    - Others: Can only view themselves
    
    **Path Parameters:**
    - user_id: UUID of user to retrieve
    
    **Returns:**
    - 200: User details with relationships (branch, department)
    - 403: Insufficient permissions
    - 404: User not found
    """
    user = await user_service.get_user(user_id, current_user, db)
    return ApiResponse(data=UserDetail.model_validate(user))


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    branch_id: str | None = Query(None, description="Filter by branch UUID"),
    role: Role | None = Query(None, description="Filter by role"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: CurrentUser = Depends(
        require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR])
    ),
    db: AsyncSession = Depends(get_db),
    user_service = Depends(get_user_service),
):
    """
    List users with pagination and filtering.
    
    **Protected Endpoint** (SUPER_ADMIN or BRANCH_COORDINATOR)
    
    **Authorization Rules:**
    - SUPER_ADMIN: Can list all users across all branches
    - BRANCH_COORDINATOR: Can only list users in their branch (branch_id filter ignored)
    
    **Query Parameters:**
    - branch_id: Filter by branch (SUPER_ADMIN only)
    - role: Filter by role
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - sort: Sort field (default: "created_at")
    - order: Sort order "asc" or "desc" (default: "desc")
    
    **Returns:**
    - 200: Paginated list of users
    - 403: Insufficient permissions
    """
    users, total = await user_service.list_users(
        branch_id=branch_id,
        role=role.value if role else None,
        page=pagination.page,
        page_size=pagination.page_size,
        current_user=current_user,
        db=db,
    )
    
    has_next = (pagination.page * pagination.page_size) < total
    
    return PaginatedResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        has_next=has_next,
    )


@router.patch("/{user_id}", response_model=ApiResponse[UserResponse])
async def update_user(
    user_id: str,
    payload: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    user_service = Depends(get_user_service),
):
    """
    Update user information.
    
    **Protected Endpoint** (Authentication required)
    
    **Authorization Rules:**
    - SUPER_ADMIN: Can update any user
    - BRANCH_COORDINATOR: Can update users in their branch
    - Users: Can update their own profile (limited fields)
    
    **Path Parameters:**
    - user_id: UUID of user to update
    
    **Request Body (all optional):**
    - name: Full name
    - phone: Phone number
    - profile_image_url: Profile image URL
    - branch_id: Branch assignment (admin only)
    - department_id: Department assignment
    
    **Returns:**
    - 200: User updated successfully
    - 403: Insufficient permissions
    - 404: User not found
    """
    user = await user_service.update_user(user_id, payload, current_user, db)
    return ApiResponse(data=UserResponse.model_validate(user))


@router.delete("/{user_id}", response_model=ApiResponse[dict])
async def delete_user(
    user_id: str,
    current_user: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
    user_service = Depends(get_user_service),
):
    """
    Soft delete user (deactivate account).
    
    **Protected Endpoint** (SUPER_ADMIN only)
    
    **Business Rules:**
    - Only SUPER_ADMIN can delete users
    - Cannot delete yourself
    - Soft delete: Sets is_active = False (data retained)
    
    **Path Parameters:**
    - user_id: UUID of user to delete
    
    **Returns:**
    - 200: User deleted successfully
    - 400: Attempting to delete yourself
    - 403: Insufficient permissions
    - 404: User not found
    """
    result = await user_service.delete_user(user_id, current_user, db)
    return ApiResponse(data=result)


@router.post("/{user_id}/role", response_model=ApiResponse[UserResponse])
async def assign_role(
    user_id: str,
    payload: RoleAssignmentRequest,
    current_user: CurrentUser = Depends(
        require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR])
    ),
    db: AsyncSession = Depends(get_db),
    user_service = Depends(get_user_service),
):
    """
    Assign role to user.
    
    **Protected Endpoint** (SUPER_ADMIN or BRANCH_COORDINATOR)
    
    **Authorization Matrix:**
    - SUPER_ADMIN: Can assign any role
    - BRANCH_COORDINATOR: Can assign DEPARTMENT_LEADER or YOUTH_MEMBER only
    
    **Path Parameters:**
    - user_id: UUID of user
    
    **Request Body:**
    - role: New role to assign
    
    **Returns:**
    - 200: Role assigned successfully
    - 403: Insufficient permissions to assign role
    - 404: User not found
    """
    user = await user_service.assign_role(
        user_id,
        payload.role,
        current_user,
        db
    )
    return ApiResponse(data=UserResponse.model_validate(user))


@router.post("/{user_id}/branch", response_model=ApiResponse[UserResponse])
async def assign_branch(
    user_id: str,
    payload: BranchAssignmentRequest,
    current_user: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
    user_service = Depends(get_user_service),
):
    """
    Assign user to branch (SUPER_ADMIN only).
    
    **Protected Endpoint** (SUPER_ADMIN only)
    
    **Path Parameters:**
    - user_id: UUID of user
    
    **Request Body:**
    - branch_id: UUID of branch to assign
    
    **Returns:**
    - 200: Branch assigned successfully
    - 403: Insufficient permissions
    - 404: User or branch not found
    """
    user = await user_service.assign_branch(
        user_id,
        payload.branch_id,
        current_user,
        db
    )
    return ApiResponse(data=UserResponse.model_validate(user))
