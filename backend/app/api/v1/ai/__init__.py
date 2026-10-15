"""
AI/ML API Endpoints

This module provides AI-powered predictive analytics and insights endpoints
for youth engagement monitoring and risk detection.

Submodules:
    predictions: Individual risk predictions and bulk at-risk detection
    analytics: Engagement scoring and automated insights generation
"""

from app.api.v1.ai.predictions import router as predictions_router
from app.api.v1.ai.analytics import router as analytics_router

__all__ = ["predictions_router", "analytics_router"]
