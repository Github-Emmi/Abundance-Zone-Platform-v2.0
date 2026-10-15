"""
Task Monitoring Schemas
Pydantic models for Celery task status tracking and monitoring
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskStatusResponse(BaseModel):
    """Response schema for individual task status"""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(
        ...,
        description="Task status: PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED",
    )
    result: Optional[Any] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    traceback: Optional[str] = Field(None, description="Full traceback if failed")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(
        None, description="Task completion timestamp"
    )
    progress: Optional[Dict[str, Any]] = Field(
        None, description="Progress information for long-running tasks"
    )
    worker: Optional[str] = Field(None, description="Worker that executed the task")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "a7f3e8d9-1234-5678-90ab-cdef12345678",
                "status": "SUCCESS",
                "result": {"email_sent": True, "recipient": "user@example.com"},
                "error": None,
                "traceback": None,
                "started_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:30:05Z",
                "progress": None,
                "worker": "celery@worker1",
            }
        }


class TaskSubmitResponse(BaseModel):
    """Response schema when submitting a new task"""

    task_id: str = Field(..., description="Celery task ID for tracking")
    status: str = Field(default="PENDING", description="Initial task status")
    message: str = Field(..., description="Human-readable message")
    status_url: str = Field(..., description="URL to check task status")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "a7f3e8d9-1234-5678-90ab-cdef12345678",
                "status": "PENDING",
                "message": "Email task queued successfully",
                "status_url": "/api/v1/tasks/a7f3e8d9-1234-5678-90ab-cdef12345678",
            }
        }


class TaskInfo(BaseModel):
    """Brief task information for listing"""

    task_id: str = Field(..., description="Celery task ID")
    name: str = Field(..., description="Task name/type")
    status: str = Field(..., description="Current status")
    submitted_at: Optional[datetime] = Field(None, description="Submission timestamp")
    args: Optional[List[Any]] = Field(None, description="Task arguments")
    kwargs: Optional[Dict[str, Any]] = Field(None, description="Task keyword arguments")


class TaskListResponse(BaseModel):
    """Response schema for listing multiple tasks"""

    total: int = Field(..., description="Total number of tasks")
    tasks: List[TaskInfo] = Field(..., description="List of task information")
    active_count: int = Field(0, description="Number of active/running tasks")
    pending_count: int = Field(0, description="Number of pending tasks")
    failed_count: int = Field(0, description="Number of failed tasks")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 3,
                "active_count": 1,
                "pending_count": 1,
                "failed_count": 1,
                "tasks": [
                    {
                        "task_id": "task-1",
                        "name": "send_welcome_email",
                        "status": "SUCCESS",
                        "submitted_at": "2024-01-15T10:30:00Z",
                    },
                    {
                        "task_id": "task-2",
                        "name": "generate_report",
                        "status": "STARTED",
                        "submitted_at": "2024-01-15T10:31:00Z",
                    },
                    {
                        "task_id": "task-3",
                        "name": "send_notification",
                        "status": "PENDING",
                        "submitted_at": "2024-01-15T10:32:00Z",
                    },
                ],
            }
        }


class TaskCancelRequest(BaseModel):
    """Request schema to cancel a running task"""

    terminate: bool = Field(False, description="Force terminate (use with caution)")
    signal: str = Field("SIGTERM", description="Signal to send (SIGTERM, SIGKILL)")


class TaskRetryRequest(BaseModel):
    """Request schema to retry a failed task"""

    countdown: Optional[int] = Field(None, description="Delay in seconds before retry")
    max_retries: Optional[int] = Field(None, description="Override max retry attempts")


class ActiveTasksResponse(BaseModel):
    """Response schema for currently active tasks"""

    active_tasks: List[TaskInfo] = Field(..., description="List of active tasks")
    worker_count: int = Field(..., description="Number of active workers")
    workers: Dict[str, List[TaskInfo]] = Field(
        ..., description="Tasks grouped by worker"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "active_tasks": [
                    {
                        "task_id": "task-1",
                        "name": "generate_report",
                        "status": "STARTED",
                        "submitted_at": "2024-01-15T10:30:00Z",
                    }
                ],
                "worker_count": 1,
                "workers": {
                    "celery@worker1": [
                        {
                            "task_id": "task-1",
                            "name": "generate_report",
                            "status": "STARTED",
                            "submitted_at": "2024-01-15T10:30:00Z",
                        }
                    ]
                },
            }
        }


class ScheduledTasksResponse(BaseModel):
    """Response schema for scheduled tasks (Celery Beat)"""

    scheduled_tasks: List[Dict[str, Any]] = Field(
        ..., description="List of scheduled task configurations"
    )
    total: int = Field(..., description="Total number of scheduled tasks")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 3,
                "scheduled_tasks": [
                    {
                        "name": "daily-attendance-report",
                        "task": "generate_daily_attendance_report",
                        "schedule": "crontab(hour=9, minute=0)",
                        "enabled": True,
                        "last_run": "2024-01-15T09:00:00Z",
                        "next_run": "2024-01-16T09:00:00Z",
                    }
                ],
            }
        }


class WorkerStatsResponse(BaseModel):
    """Response schema for worker statistics"""

    workers: Dict[str, Dict[str, Any]] = Field(..., description="Worker information")
    total_workers: int = Field(..., description="Total number of workers")
    healthy_workers: int = Field(..., description="Number of healthy workers")

    class Config:
        json_schema_extra = {
            "example": {
                "total_workers": 1,
                "healthy_workers": 1,
                "workers": {
                    "celery@worker1": {
                        "status": "online",
                        "active_tasks": 2,
                        "processed": 150,
                        "pool_size": 4,
                    }
                },
            }
        }
