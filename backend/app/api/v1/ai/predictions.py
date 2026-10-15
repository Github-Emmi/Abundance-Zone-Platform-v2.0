"""
AI/ML Predictions API Router

Provides AI-powered risk prediction and at-risk youth detection endpoints.
Uses machine learning algorithms to analyze attendance patterns and predict
disengagement risk before it becomes critical.

Endpoints:
    POST /ai/predict-risk: Individual user risk prediction
    POST /ai/detect-at-risk: Bulk at-risk youth detection

Business Use Cases:
    - Early intervention for at-risk youth
    - Proactive outreach planning
    - Resource allocation optimization
    - Targeted support program design

Implements: FR-AI-001, FR-AI-002
"""

import logging
from fastapi import APIRouter, Depends, status
from typing import Dict

from app.api.deps import CurrentUser, get_current_user, require_role
from app.api.schemas.ai import RiskPredictionRequest, AtRiskDetectionRequest
from app.api.schemas.responses import ApiResponse
from app.domain.value_objects.enums import Role
from app.tasks.ai_ml import predict_attendance_risk, detect_at_risk_youths

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ai", tags=["AI/ML Predictions"])


@router.post(
    "/predict-risk",
    response_model=ApiResponse[Dict],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role([Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN]))],
    summary="Predict individual user attendance risk",
    description="""
    **AI-Powered Risk Prediction**
    
    Analyzes a user's attendance patterns over the last 60 days to predict
    disengagement risk using machine learning algorithms.
    
    **Algorithm Overview:**
    The risk prediction model uses three key metrics:
    
    1. **Attendance Rate** (50% weight):
       - Percentage of events attended in the last 60 days
       - Accounts for total available events vs actual attendance
    
    2. **Consistency Score** (30% weight):
       - Measures weekly attendance consistency
       - Tracks how many weeks the user attended at least one event
       - Higher score indicates reliable, predictable engagement
    
    3. **Recent Activity** (20% weight):
       - Number of attendances in the last 14 days
       - Gives more weight to recent behavior patterns
       - Helps identify sudden drops in engagement
    
    **Risk Levels:**
    - **Low**: Attendance ≥80%, Consistency ≥70% (healthy engagement)
    - **Medium**: Attendance ≥60%, Consistency ≥50% (monitor closely)
    - **High**: Attendance ≥40% (intervention needed)
    - **Critical**: Attendance <40% (immediate action required)
    
    **Business Use Cases:**
    - Pre-emptive outreach before complete disengagement
    - Personalized intervention strategies
    - Resource allocation for support programs
    - Early identification of at-risk youth
    
    **Response Time:**
    This is a long-running task (5-10 seconds typical). The endpoint returns
    immediately with a task_id. Use the task monitoring endpoint
    `GET /api/v1/tasks/{task_id}` to check completion status and retrieve results.
    
    **Required Permissions:**
    - BRANCH_COORDINATOR: Can predict risk for users in their branch
    - SUPER_ADMIN: Can predict risk for any user
    
    **Example Workflow:**
    ```python
    # Step 1: Submit prediction request
    response = await client.post("/api/v1/ai/predict-risk", 
                                  json={"user_id": "123..."})
    task_id = response.json()["data"]["task_id"]
    
    # Step 2: Poll for completion
    result = await client.get(f"/api/v1/tasks/{task_id}")
    
    # Step 3: Access prediction results
    if result["status"] == "SUCCESS":
        analysis = result["result"]
        print(f"Risk Level: {analysis['risk_level']}")
        print(f"Engagement Score: {analysis['engagement_score']}")
    ```
    """,
)
async def predict_risk(
    request: RiskPredictionRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[Dict]:
    """
    Predict attendance risk for a specific user.

    This endpoint dispatches an asynchronous Celery task to analyze a user's
    attendance patterns and calculate risk metrics.

    Args:
        request: Risk prediction request with user_id
        current_user: Authenticated user making the request

    Returns:
        ApiResponse containing task_id for monitoring the prediction job

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 403: If user lacks required permissions
        HTTPException 500: If task dispatch fails

    Example:
        Request:
        ```json
        {
            "user_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        ```

        Response:
        ```json
        {
            "success": true,
            "data": {
                "task_id": "a7f3e8d9-1234-5678-90ab-cdef12345678",
                "status": "queued",
                "message": "Risk prediction started",
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        ```
    """
    try:
        # Dispatch async Celery task
        task = predict_attendance_risk.delay(request.user_id)
        task_id = task.id

        logger.info(
            f"Dispatched risk prediction task {task_id} for user {request.user_id} "
            f"by {current_user.name} ({current_user.role})"
        )

        return ApiResponse(
            data={
                "task_id": task_id,
                "status": "queued",
                "message": "Risk prediction started",
                "user_id": request.user_id,
            }
        )

    except Exception as e:
        logger.warning(
            f"Failed to dispatch risk prediction task for user {request.user_id}: {e}"
        )
        return ApiResponse(
            data={
                "task_id": None,
                "status": "error",
                "message": "Failed to queue task",
                "user_id": request.user_id,
                "error": str(e),
            }
        )


@router.post(
    "/detect-at-risk",
    response_model=ApiResponse[Dict],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role(Role.SUPER_ADMIN))],
    summary="Detect all at-risk youth in platform",
    description="""
    **Bulk At-Risk Youth Detection**
    
    Performs comprehensive risk analysis across all active users in the platform
    to identify youth who need intervention or support.
    
    **Algorithm Overview:**
    This endpoint runs individual risk predictions for every active user and
    aggregates the results based on the specified minimum risk level threshold.
    
    **Risk Level Filtering:**
    - **critical**: Only users in critical state (attendance <40%)
    - **high**: Critical + high risk users (attendance <60%)
    - **medium** (default): Critical + high + medium risk (attendance <80%)
    - **low**: All users (complete analysis)
    
    **Sorting Logic:**
    Results are sorted by:
    1. Risk level (critical first, then high, medium, low)
    2. Engagement score (lowest first within each risk level)
    
    This ensures the most urgent cases appear first in the results.
    
    **Business Use Cases:**
    - Monthly/quarterly risk assessment reports
    - Batch intervention planning
    - Coordinator workload distribution
    - Board reporting and grant applications
    - Trend analysis over time
    
    **Performance Characteristics:**
    - **Long-running task**: Can take 1-5 minutes depending on user count
    - Processes 10-20 users per second
    - Returns immediately with task_id
    - Check progress via task monitoring endpoint
    
    **Resource Considerations:**
    - Database-intensive operation
    - Analyzes 60 days of attendance history per user
    - Recommended to run during off-peak hours
    - Consider scheduling via Celery Beat for automatic weekly runs
    
    **Required Permissions:**
    - SUPER_ADMIN only (platform-wide analysis)
    
    **Example Workflow:**
    ```python
    # Step 1: Submit detection request for high-risk users
    response = await client.post("/api/v1/ai/detect-at-risk",
                                  json={"min_risk_level": "high"})
    task_id = response.json()["data"]["task_id"]
    
    # Step 2: Monitor task progress
    while True:
        result = await client.get(f"/api/v1/tasks/{task_id}")
        if result["status"] in ["SUCCESS", "FAILURE"]:
            break
        await asyncio.sleep(5)
    
    # Step 3: Process results
    if result["status"] == "SUCCESS":
        analysis = result["result"]
        print(f"Total at-risk: {analysis['at_risk_count']}")
        print(f"Critical: {analysis['critical_count']}")
        print(f"High: {analysis['high_count']}")
        
        # Get detailed user list
        for user in analysis["at_risk_users"]:
            print(f"{user['user_name']}: {user['risk_level']}")
    ```
    
    **Recommended Scheduling:**
    Configure Celery Beat to run this automatically:
    - Weekly: Sunday night for Monday coordinator review
    - Monthly: 1st of month for board reports
    - Quarterly: For grant reporting and trend analysis
    """,
)
async def detect_at_risk(
    request: AtRiskDetectionRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[Dict]:
    """
    Detect all at-risk youth across the platform.

    This endpoint dispatches an asynchronous Celery task to analyze all active
    users and identify those meeting the specified risk threshold.

    Args:
        request: Detection request with minimum risk level threshold
        current_user: Authenticated user making the request (must be SUPER_ADMIN)

    Returns:
        ApiResponse containing task_id for monitoring the detection job

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 403: If user is not SUPER_ADMIN
        HTTPException 500: If task dispatch fails

    Example:
        Request:
        ```json
        {
            "min_risk_level": "high"
        }
        ```

        Response:
        ```json
        {
            "success": true,
            "data": {
                "task_id": "b8g4f9e0-2345-6789-01bc-def123456789",
                "status": "queued",
                "message": "At-risk detection started",
                "min_risk_level": "high",
                "estimated_duration": "2-5 minutes"
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        ```
    """
    try:
        # Dispatch async Celery task
        task = detect_at_risk_youths.delay(request.min_risk_level)
        task_id = task.id

        logger.info(
            f"Dispatched at-risk detection task {task_id} "
            f"(min_level: {request.min_risk_level}) "
            f"by {current_user.name} ({current_user.role})"
        )

        return ApiResponse(
            data={
                "task_id": task_id,
                "status": "queued",
                "message": "At-risk detection started",
                "min_risk_level": request.min_risk_level,
                "estimated_duration": "2-5 minutes",
            }
        )

    except Exception as e:
        logger.warning(f"Failed to dispatch at-risk detection task: {e}")
        return ApiResponse(
            data={
                "task_id": None,
                "status": "error",
                "message": "Failed to queue task",
                "min_risk_level": request.min_risk_level,
                "error": str(e),
            }
        )
