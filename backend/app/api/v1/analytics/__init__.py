"""
Analytics and Reports API Endpoints

Provides comprehensive reporting and analytics capabilities with async Celery integration.
Exports routers for daily, weekly, monthly, and custom reports with CSV download support.

Available Routers:
    - reports_router: Report generation and download endpoints

Implements: FR-REPORTS-001, FR-REPORTS-002, FR-ANALYTICS-001
"""

from app.api.v1.analytics.reports import router as reports_router

__all__ = ["reports_router"]
