"""
User Management API Router
Endpoints for user CRUD operations and role management
"""

from datetime import datetime
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


@router.post(
    "", response_model=ApiResponse[UserResponse], status_code=status.HTTP_201_CREATED
)
async def create_user(
    payload: UserCreate,
    current_user: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
    user_service=Depends(get_user_service),
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
    user_service=Depends(get_user_service),
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
    user_service=Depends(get_user_service),
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
    user_service=Depends(get_user_service),
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
    user_service=Depends(get_user_service),
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
    user_service=Depends(get_user_service),
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
    user = await user_service.assign_role(user_id, payload.role, current_user, db)
    return ApiResponse(data=UserResponse.model_validate(user))


@router.post("/{user_id}/branch", response_model=ApiResponse[UserResponse])
async def assign_branch(
    user_id: str,
    payload: BranchAssignmentRequest,
    current_user: CurrentUser = Depends(require_role([Role.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
    user_service=Depends(get_user_service),
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
        user_id, payload.branch_id, current_user, db
    )
    return ApiResponse(data=UserResponse.model_validate(user))


# ═══════════════════════════════════════════════════════════════════════════
# AI/ML Integration Endpoints
# ═══════════════════════════════════════════════════════════════════════════

import logging
from app.tasks.ai_ml import predict_attendance_risk

logger = logging.getLogger(__name__)


@router.get("/{user_id}/risk-assessment", response_model=ApiResponse[dict])
async def get_risk_assessment(
    user_id: str,
    current_user: CurrentUser = Depends(
        require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR])
    ),
    db: AsyncSession = Depends(get_db),
    user_service=Depends(get_user_service),
):
    """
    Get AI-powered attendance risk assessment for user.

    **Protected Endpoint** (SUPER_ADMIN or BRANCH_COORDINATOR)

    **Business Rules:**
    - Analyzes attendance patterns over last 60 days
    - Calculates risk level: low, medium, high, critical
    - Generates personalized recommendations
    - Results cached for 24 hours for performance

    **Path Parameters:**
    - user_id: UUID of user to assess

    **Authorization Rules:**
    - SUPER_ADMIN: Can assess any user
    - BRANCH_COORDINATOR: Can assess users in their branch

    **Returns:**
    - task_id: Celery task ID for background processing
    - status: "queued" or "error"
    - message: Status message
    - user_id: User being assessed

    **AI/ML Metrics Calculated:**
    - attendance_rate: Percentage of events attended (0-100%)
    - consistency_score: Weekly attendance consistency (0-100%)
    - engagement_score: Overall engagement metric (0-100)
    - risk_level: low/medium/high/critical
    - recommendations: Personalized action items

    **Risk Level Criteria:**
    - **Low**: ≥80% attendance, ≥70% consistency
    - **Medium**: ≥60% attendance, ≥50% consistency
    - **High**: ≥40% attendance
    - **Critical**: <40% attendance

    **Use Cases:**
    - Early intervention for at-risk youth
    - Monthly coordinator reviews
    - Parent/guardian communications
    - Targeted engagement programs

    **Performance:**
    - Analysis runs asynchronously (1-5 seconds)
    - Check task status via /api/v1/tasks/{task_id}
    - Result includes full analysis when complete

    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "task_id": "abc-123-def",
            "status": "queued",
            "message": "Risk assessment started",
            "user_id": "user-uuid",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
    ```
    """
    # Verify user exists and check permissions
    await user_service.get_user(user_id, current_user, db)

    task_id = None
    try:
        task = predict_attendance_risk.delay(user_id)
        task_id = task.id
        logger.info(f"Dispatched risk assessment task {task_id} for user {user_id}")
        status_str = "queued"
        message = "Risk assessment started"
    except Exception as e:
        logger.error(f"Failed to dispatch risk assessment task: {e}")
        status_str = "error"
        message = "Failed to queue risk assessment"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status_str,
            "message": message,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@router.get("/{user_id}/engagement-score", response_model=ApiResponse[dict])
async def get_engagement_score(
    user_id: str,
    current_user: CurrentUser = Depends(
        require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR])
    ),
    db: AsyncSession = Depends(get_db),
    user_service=Depends(get_user_service),
):
    """
    Get user's engagement score with detailed metrics.

    **Protected Endpoint** (SUPER_ADMIN or BRANCH_COORDINATOR)

    **Business Rules:**
    - Calculates comprehensive engagement score (0-100)
    - Analyzes multiple engagement dimensions
    - Triggers background calculation for real-time data
    - Result available via task monitoring

    **Path Parameters:**
    - user_id: UUID of user

    **Authorization Rules:**
    - SUPER_ADMIN: Can view any user's score
    - BRANCH_COORDINATOR: Can view scores for users in their branch

    **Returns:**
    - task_id: Celery task ID for background calculation
    - status: "queued" or "error"
    - message: Status message
    - user_id: User being assessed

    **Engagement Score Formula:**
    ```
    Score = (Attendance Rate × 0.5) +
            (Consistency × 0.3) +
            (Recent Activity × 0.2)
    ```

    **Score Calculation:**
    - **Attendance Rate (50%)**: % of events attended vs. total events
    - **Consistency (30%)**: Regular weekly attendance pattern
    - **Recent Activity (20%)**: Attendance in last 14 days

    **Score Interpretation:**
    - **90-100**: Highly engaged - excellent attendance
    - **70-89**: Engaged - good attendance patterns
    - **50-69**: Moderately engaged - needs encouragement
    - **30-49**: Low engagement - intervention recommended
    - **0-29**: Disengaged - immediate action required

    **Use Cases:**
    - Recognition programs (top engaged youth)
    - Gamification and leaderboards
    - Progress tracking over time
    - Parent reports
    - Coordinator dashboards

    **Performance:**
    - Calculation runs in background (1-3 seconds)
    - Monitor via /api/v1/tasks/{task_id}
    - Includes attendance breakdown in result

    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "task_id": "xyz-789-abc",
            "status": "queued",
            "message": "Engagement score calculation started",
            "user_id": "user-uuid",
            "timestamp": "2024-01-15T10:35:00Z"
        }
    }
    ```

    **Related Endpoints:**
    - GET /api/v1/users/{user_id}/risk-assessment - Full risk analysis
    - POST /api/v1/ai/engagement-scores - Calculate scores for all users
    - GET /api/v1/tasks/{task_id} - Check calculation status
    """
    # Verify user exists and check permissions
    await user_service.get_user(user_id, current_user, db)

    task_id = None
    try:
        # Reuse the risk prediction task which includes engagement score
        task = predict_attendance_risk.delay(user_id)
        task_id = task.id
        logger.info(
            f"Dispatched engagement score calculation task {task_id} for user {user_id}"
        )
        status_str = "queued"
        message = "Engagement score calculation started"
    except Exception as e:
        logger.error(f"Failed to dispatch engagement score task: {e}")
        status_str = "error"
        message = "Failed to queue engagement score calculation"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status_str,
            "message": message,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
