"""
Task Monitoring API Package
Endpoints for tracking and monitoring Celery background tasks
"""

from app.api.v1.task.tasks import router

__all__ = ["router"]
