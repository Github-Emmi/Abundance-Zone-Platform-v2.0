"""
Task Monitoring API Router
Endpoints for tracking Celery task status, listing active tasks, and monitoring workers
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from celery.result import AsyncResult
from celery import states

from app.api.deps import CurrentUserDep
from app.api.schemas.task import (
    TaskStatusResponse,
    TaskListResponse,
    TaskInfo,
    ActiveTasksResponse,
    ScheduledTasksResponse,
    WorkerStatsResponse,
    TaskCancelRequest,
    TaskRetryRequest,
)
from app.api.schemas.responses import ApiResponse
from app.tasks.celery_app import celery_app
from app.domain.value_objects.enums import Role

router = APIRouter(prefix="/tasks", tags=["Task Monitoring"])


def get_celery_app():
    """Dependency to inject Celery app"""
    return celery_app


@router.get("/{task_id}", response_model=ApiResponse[TaskStatusResponse])
async def get_task_status(
    task_id: str,
    current_user: CurrentUserDep,
    celery: "Celery" = Depends(get_celery_app),
):
    """
    Get the status of a specific Celery task.

    **Authentication Required:** Any authenticated user can check task status

    **Path Parameters:**
    - task_id: Celery task ID returned when task was submitted

    **Returns:**
    - Task status (PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED)
    - Result data if task completed successfully
    - Error message and traceback if task failed
    - Progress information for long-running tasks

    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "task_id": "a7f3e8d9-1234-5678-90ab-cdef12345678",
            "status": "SUCCESS",
            "result": {"email_sent": true, "recipient": "user@example.com"},
            "error": null,
            "started_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T10:30:05Z"
        }
    }
    ```
    """
    try:
        # Get task result from Celery
        task_result = AsyncResult(task_id, app=celery)

        # Build response based on task state
        response_data = {
            "task_id": task_id,
            "status": task_result.state,
            "result": None,
            "error": None,
            "traceback": None,
            "started_at": None,
            "completed_at": None,
            "progress": None,
            "worker": None,
        }

        if task_result.state == states.SUCCESS:
            response_data["result"] = task_result.result
            response_data["completed_at"] = task_result.date_done

        elif task_result.state == states.FAILURE:
            response_data["error"] = str(task_result.result)
            response_data["traceback"] = task_result.traceback

        elif task_result.state == states.STARTED:
            # Get progress if available
            if hasattr(task_result, "info") and task_result.info:
                response_data["progress"] = task_result.info

        # Get worker information if available
        if task_result.info and isinstance(task_result.info, dict):
            response_data["worker"] = task_result.info.get("worker")

        return ApiResponse(data=TaskStatusResponse(**response_data))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task status: {str(e)}",
        )


@router.get("/active/list", response_model=ApiResponse[ActiveTasksResponse])
async def get_active_tasks(
    current_user: CurrentUserDep,
    celery: "Celery" = Depends(get_celery_app),
):
    """
    Get list of currently active (running) tasks across all workers.

    **Authentication Required:** Any authenticated user

    **Permissions:**
    - Regular users: See all active tasks (limited info)
    - SUPER_ADMIN: See detailed task information

    **Returns:**
    - List of active tasks
    - Worker count
    - Tasks grouped by worker

    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "active_tasks": [
                {
                    "task_id": "task-1",
                    "name": "generate_report",
                    "status": "STARTED"
                }
            ],
            "worker_count": 1,
            "workers": {
                "celery@worker1": [...]
            }
        }
    }
    ```
    """
    try:
        # Inspect active tasks from all workers
        inspect = celery.control.inspect()
        active_tasks = inspect.active()

        if not active_tasks:
            return ApiResponse(
                data=ActiveTasksResponse(active_tasks=[], worker_count=0, workers={})
            )

        # Parse active tasks
        all_tasks = []
        workers_dict = {}

        for worker_name, tasks in active_tasks.items():
            worker_tasks = []
            for task in tasks:
                task_info = TaskInfo(
                    task_id=task.get("id", "unknown"),
                    name=task.get("name", "unknown"),
                    status="STARTED",
                    submitted_at=None,
                    args=(
                        task.get("args")
                        if current_user.role == Role.SUPER_ADMIN
                        else None
                    ),
                    kwargs=(
                        task.get("kwargs")
                        if current_user.role == Role.SUPER_ADMIN
                        else None
                    ),
                )
                all_tasks.append(task_info)
                worker_tasks.append(task_info)

            workers_dict[worker_name] = worker_tasks

        return ApiResponse(
            data=ActiveTasksResponse(
                active_tasks=all_tasks,
                worker_count=len(active_tasks),
                workers=workers_dict,
            )
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active tasks: {str(e)}",
        )


@router.get("/scheduled/list", response_model=ApiResponse[ScheduledTasksResponse])
async def get_scheduled_tasks(
    current_user: CurrentUserDep,
    celery: "Celery" = Depends(get_celery_app),
):
    """
    Get list of scheduled tasks (Celery Beat configuration).

    **Authentication Required:** SUPER_ADMIN only

    **Returns:**
    - List of scheduled periodic tasks
    - Task names, schedules, and enabled status
    - Last run and next run times

    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "total": 3,
            "scheduled_tasks": [
                {
                    "name": "daily-attendance-report",
                    "task": "generate_daily_attendance_report",
                    "schedule": "crontab(hour=9, minute=0)",
                    "enabled": true
                }
            ]
        }
    }
    ```
    """
    # Permission check
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SUPER_ADMIN can view scheduled tasks",
        )

    try:
        # Get Celery Beat schedule
        schedule = celery.conf.beat_schedule
        scheduled_tasks = []

        for name, config in schedule.items():
            task_info = {
                "name": name,
                "task": config.get("task"),
                "schedule": str(config.get("schedule")),
                "enabled": config.get("options", {}).get("enabled", True),
                "args": config.get("args", []),
                "kwargs": config.get("kwargs", {}),
            }
            scheduled_tasks.append(task_info)

        return ApiResponse(
            data=ScheduledTasksResponse(
                scheduled_tasks=scheduled_tasks, total=len(scheduled_tasks)
            )
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scheduled tasks: {str(e)}",
        )


@router.get("/workers/stats", response_model=ApiResponse[WorkerStatsResponse])
async def get_worker_stats(
    current_user: CurrentUserDep,
    celery: "Celery" = Depends(get_celery_app),
):
    """
    Get statistics about Celery workers.

    **Authentication Required:** SUPER_ADMIN only

    **Returns:**
    - Worker count (total and healthy)
    - Per-worker statistics (active tasks, processed count, pool size)
    - Worker status (online/offline)

    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "total_workers": 1,
            "healthy_workers": 1,
            "workers": {
                "celery@worker1": {
                    "status": "online",
                    "active_tasks": 2,
                    "processed": 150
                }
            }
        }
    }
    ```
    """
    # Permission check
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SUPER_ADMIN can view worker stats",
        )

    try:
        inspect = celery.control.inspect()

        # Get stats from all workers
        stats = inspect.stats()
        active_tasks = inspect.active()
        registered = inspect.registered()

        if not stats:
            return ApiResponse(
                data=WorkerStatsResponse(workers={}, total_workers=0, healthy_workers=0)
            )

        workers_info = {}
        healthy_count = 0

        for worker_name, worker_stats in stats.items():
            active_count = len(active_tasks.get(worker_name, []))
            is_healthy = worker_stats.get("pool", {}).get("writes", 0) > 0

            if is_healthy:
                healthy_count += 1

            workers_info[worker_name] = {
                "status": "online" if is_healthy else "degraded",
                "active_tasks": active_count,
                "processed": worker_stats.get("total", {}).get("tasks", 0),
                "pool_size": worker_stats.get("pool", {}).get("max-concurrency", 0),
                "registered_tasks": len(registered.get(worker_name, [])),
            }

        return ApiResponse(
            data=WorkerStatsResponse(
                workers=workers_info,
                total_workers=len(stats),
                healthy_workers=healthy_count,
            )
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve worker stats: {str(e)}",
        )


@router.post("/{task_id}/cancel", response_model=ApiResponse[dict])
async def cancel_task(
    task_id: str,
    request: TaskCancelRequest,
    current_user: CurrentUserDep,
    celery: "Celery" = Depends(get_celery_app),
):
    """
    Cancel a running or pending task.

    **Authentication Required:** SUPER_ADMIN only

    **Path Parameters:**
    - task_id: Celery task ID to cancel

    **Request Body:**
    - terminate: Force terminate (use with caution)
    - signal: Signal to send (SIGTERM, SIGKILL)

    **Returns:**
    - Cancellation status

    **Warning:** Terminating tasks can leave data in inconsistent state.
    Use with caution!
    """
    # Permission check
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SUPER_ADMIN can cancel tasks",
        )

    try:
        task_result = AsyncResult(task_id, app=celery)

        if request.terminate:
            # Force terminate task
            celery.control.revoke(task_id, terminate=True, signal=request.signal)
            message = f"Task {task_id} terminated forcefully"
        else:
            # Gracefully revoke task
            celery.control.revoke(task_id, terminate=False)
            message = f"Task {task_id} cancelled"

        return ApiResponse(
            data={
                "task_id": task_id,
                "cancelled": True,
                "message": message,
                "previous_status": task_result.state,
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}",
        )


@router.post("/{task_id}/retry", response_model=ApiResponse[dict])
async def retry_task(
    task_id: str,
    request: TaskRetryRequest,
    current_user: CurrentUserDep,
    celery: "Celery" = Depends(get_celery_app),
):
    """
    Retry a failed task.

    **Authentication Required:** SUPER_ADMIN only

    **Path Parameters:**
    - task_id: Celery task ID to retry

    **Request Body:**
    - countdown: Delay in seconds before retry
    - max_retries: Override max retry attempts

    **Returns:**
    - New task ID for the retry
    """
    # Permission check
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SUPER_ADMIN can retry tasks",
        )

    try:
        task_result = AsyncResult(task_id, app=celery)

        # Check if task failed
        if task_result.state != states.FAILURE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task is in {task_result.state} state, can only retry FAILURE tasks",
            )

        # Get original task info
        task_name = task_result.name
        if not task_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot determine original task name",
            )

        # Note: Actual retry implementation would need task args/kwargs
        # This is a simplified version
        return ApiResponse(
            data={
                "message": "Task retry functionality requires task args/kwargs storage",
                "original_task_id": task_id,
                "task_name": task_name,
                "note": "Implement task metadata storage for full retry support",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry task: {str(e)}",
        )
