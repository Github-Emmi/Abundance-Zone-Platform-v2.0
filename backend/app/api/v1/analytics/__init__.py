"""
Analytics and Reports API Endpoints

Provides comprehensive reporting and analytics capabilities with async Celery integration.
Exports routers for daily, weekly, monthly, and custom reports with CSV download support.

Available Routers:
    - reports_router: Report generation and download endpoints
    - dashboard_router: Real-time dashboard analytics and statistics

Implements: FR-REPORTS-001, FR-REPORTS-002, FR-ANALYTICS-001
"""

from app.api.v1.analytics.reports import router as reports_router
from app.api.v1.analytics.dashboard import router as dashboard_router

__all__ = ["reports_router", "dashboard_router"]
