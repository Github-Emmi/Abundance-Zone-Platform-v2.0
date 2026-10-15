"""Youth Management API Router"""

from fastapi import APIRouter, Depends, status
from app.api.deps import CurrentUserDep, DbSessionDep, get_db, Depends
from app.api.schemas.youth import *
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.responses import ApiResponse, PaginatedResponse
from app.application.services.youth_service import YouthService, get_youth_service

router = APIRouter(prefix="/youths", tags=["youths"])


@router.post(
    "", response_model=ApiResponse[YouthResponse], status_code=status.HTTP_201_CREATED
)
async def create_youth(
    data: YouthCreateRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: YouthService = Depends(get_youth_service),
):
    youth = await service.create_youth(
        data.fullname,
        data.branch_id,
        data.gender,
        data.email,
        data.phone,
        data.department_id,
        data.date_of_birth,
        db,
    )
    return ApiResponse(data=YouthResponse.from_orm(youth))


@router.get("/{youth_id}", response_model=ApiResponse[YouthResponse])
async def get_youth(
    youth_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    service: YouthService = Depends(get_youth_service),
):
    youth = await service.get_youth(youth_id, db)
    return ApiResponse(data=YouthResponse.from_orm(youth))


@router.get("", response_model=ApiResponse[PaginatedResponse[YouthResponse]])
async def list_youths(
    branch_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: YouthService = Depends(get_youth_service),
):
    youths, total = await service.list_youths(
        branch_id, pagination.offset, pagination.limit, db
    )
    items = [YouthResponse.from_orm(y) for y in youths]
    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=(pagination.page * pagination.page_size) < total,
        )
    )


@router.get("/search", response_model=ApiResponse[PaginatedResponse[YouthResponse]])
async def search_youths(
    query: str,
    branch_id: str | None,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: YouthService = Depends(get_youth_service),
):
    youths, total = await service.search_youths(
        query, branch_id, pagination.offset, pagination.limit, db
    )
    items = [YouthResponse.from_orm(y) for y in youths]
    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=(pagination.page * pagination.page_size) < total,
        )
    )


# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# AI/ML Integration Endpoints
# ═══════════════════════════════════════════════════════════════════════════

import logging
from datetime import datetime
from app.api.deps import require_role
from app.domain.value_objects.enums import Role
from app.tasks.ai_ml import (
    detect_at_risk_youths,
    calculate_engagement_scores,
    generate_insights,
)

logger = logging.getLogger(__name__)


@router.get(
    "/at-risk",
    response_model=ApiResponse[dict],
    dependencies=[Depends(require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]))],
)
async def get_at_risk_youths(
    db: DbSessionDep,
    min_risk_level: str = "medium",
):
    """Get at-risk youths using AI/ML analysis."""
    task_id = None
    try:
        task = detect_at_risk_youths.delay(min_risk_level=min_risk_level)
        task_id = task.id
        logger.info(
            f"Dispatched at-risk youth detection task {task_id} with min_risk_level={min_risk_level}"
        )
        status_str = "queued"
        message = "At-risk youth detection started"
    except Exception as e:
        logger.error(f"Failed to dispatch at-risk detection task: {e}")
        status_str = "error"
        message = "Failed to queue at-risk youth detection"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status_str,
            "message": message,
            "min_risk_level": min_risk_level,
            "estimated_completion": "2-3 minutes",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@router.post(
    "/engagement-scores/calculate",
    response_model=ApiResponse[dict],
    dependencies=[Depends(require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]))],
)
async def calculate_youth_engagement_scores(
    db: DbSessionDep,
):
    """Calculate engagement scores for all youth members."""
    task_id = None
    try:
        task = calculate_engagement_scores.delay()
        task_id = task.id
        logger.info(f"Dispatched engagement score calculation task {task_id}")
        status_str = "queued"
        message = "Engagement score calculation started"
    except Exception as e:
        logger.error(f"Failed to dispatch engagement score calculation: {e}")
        status_str = "error"
        message = "Failed to queue engagement score calculation"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status_str,
            "message": message,
            "estimated_completion": "1-2 minutes",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@router.post(
    "/insights/generate",
    response_model=ApiResponse[dict],
    dependencies=[Depends(require_role([Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR]))],
)
async def generate_youth_insights(
    db: DbSessionDep,
):
    """Generate AI-powered insights from youth attendance data."""
    task_id = None
    try:
        task = generate_insights.delay()
        task_id = task.id
        logger.info(f"Dispatched insights generation task {task_id}")
        status_str = "queued"
        message = "Insights generation started"
    except Exception as e:
        logger.error(f"Failed to dispatch insights generation: {e}")
        status_str = "error"
        message = "Failed to queue insights generation"

    return ApiResponse(
        data={
            "task_id": task_id,
            "status": status_str,
            "message": message,
            "estimated_completion": "5-10 seconds",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
