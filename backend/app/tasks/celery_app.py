"""
Celery Application Configuration
Handles background tasks and scheduled jobs for AZYMP
"""

import ssl
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "abundance_zone",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.emails",
        "app.tasks.notifications",
        "app.tasks.reports",
        "app.tasks.ai_ml",
    ],
)

# SSL/TLS configuration for Upstash Redis (rediss://)
_ssl_opts = {}
if settings.CELERY_BROKER_URL.startswith("rediss://"):
    _ssl_opts = {
        "broker_use_ssl": {"ssl_cert_reqs": ssl.CERT_NONE},
        "redis_backend_use_ssl": {"ssl_cert_reqs": ssl.CERT_NONE},
    }

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # Results expire after 1 hour
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    
    # Task routing (all use default queue for now)
    task_routes={
        "app.tasks.emails.*": {"queue": "default"},
        "app.tasks.notifications.*": {"queue": "default"},
        "app.tasks.reports.*": {"queue": "default"},
        "app.tasks.ai_ml.*": {"queue": "default"},
    },
    
    # Scheduled tasks (Celery Beat)
    beat_schedule={
        # ═══ DAILY TASKS ═══
        
        # Daily attendance report at 9:00 AM UTC
        "daily-attendance-report": {
            "task": "app.tasks.reports.generate_daily_attendance_report",
            "schedule": crontab(hour=9, minute=0),
            "options": {"expires": 3600}
        },
        
        # Detect at-risk youths daily at 7:00 AM UTC
        "detect-at-risk-youths-daily": {
            "task": "app.tasks.ai_ml.detect_at_risk_youths",
            "schedule": crontab(hour=7, minute=0),
            "kwargs": {"min_risk_level": "high"},
            "options": {"expires": 3600}
        },
        
        # Generate daily insights at 6:00 AM UTC
        "generate-daily-insights": {
            "task": "app.tasks.ai_ml.generate_insights",
            "schedule": crontab(hour=6, minute=0),
            "options": {"expires": 3600}
        },
        
        # ═══ WEEKLY TASKS ═══
        
        # Weekly analytics every Monday at 8:00 AM UTC
        "weekly-analytics-summary": {
            "task": "app.tasks.reports.generate_weekly_analytics",
            "schedule": crontab(day_of_week=1, hour=8, minute=0),
            "options": {"expires": 7200}
        },
        
        # Calculate engagement scores every Monday at 9:00 AM UTC
        "weekly-engagement-scores": {
            "task": "app.tasks.ai_ml.calculate_engagement_scores",
            "schedule": crontab(day_of_week=1, hour=9, minute=0),
            "options": {"expires": 7200}
        },
        
        # ═══ MONTHLY TASKS ═══
        
        # Monthly financial report on 1st of month at 10:00 AM UTC
        "monthly-financial-report": {
            "task": "app.tasks.reports.generate_monthly_financial_report",
            "schedule": crontab(day_of_month=1, hour=10, minute=0),
            "options": {"expires": 14400}
        },
        
        # ═══ MAINTENANCE TASKS ═══
        
        # Cleanup old task results every Sunday at 2:00 AM UTC
        "cleanup-old-task-results": {
            "task": "app.tasks.maintenance.cleanup_old_results",
            "schedule": crontab(day_of_week=0, hour=2, minute=0),
            "options": {"expires": 3600}
        },
    },
    
    **_ssl_opts,
)


# Task result backend settings
celery_app.conf.result_backend_transport_options = {
    'retry_policy': {
        'timeout': 5.0
    }
}

# Worker settings
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True
