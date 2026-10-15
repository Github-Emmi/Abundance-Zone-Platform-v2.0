"""
AI/ML API Schemas
Pydantic models for AI-powered risk predictions, engagement analytics, and insights
"""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator
import uuid


class RiskPredictionRequest(BaseModel):
    """
    Request schema for individual user risk prediction.

    Attributes:
        user_id: UUID of the user to analyze

    Examples:
        >>> request = RiskPredictionRequest(user_id="123e4567-e89b-12d3-a456-426614174000")
    """

    user_id: str = Field(
        ...,
        description="User UUID to analyze for attendance risk",
        min_length=36,
        max_length=36,
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    @field_validator("user_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate that user_id is a valid UUID format."""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("user_id must be a valid UUID")

    class Config:
        json_schema_extra = {
            "example": {"user_id": "123e4567-e89b-12d3-a456-426614174000"}
        }


class RiskPredictionResponse(BaseModel):
    """
    Response schema for risk prediction analysis results.

    Contains comprehensive attendance and engagement metrics with AI-generated
    risk assessment and personalized recommendations.

    Attributes:
        user_id: UUID of analyzed user
        user_name: Full name of the user
        period_days: Analysis period in days (typically 60)
        total_events: Total events in the analysis period
        attended_count: Number of events attended
        attendance_rate: Percentage of events attended (0-100)
        consistency_score: Weekly attendance consistency score (0-100)
        weeks_active: Number of weeks with at least one attendance
        recent_activity: Number of attendances in last 14 days
        engagement_score: Overall engagement score (0-100)
        risk_level: AI-determined risk level (low/medium/high/critical)
        recommendations: List of personalized action recommendations
        timestamp: ISO timestamp of analysis

    Examples:
        >>> response = RiskPredictionResponse(
        ...     user_id="123",
        ...     user_name="John Doe",
        ...     period_days=60,
        ...     total_events=20,
        ...     attended_count=15,
        ...     attendance_rate=75.0,
        ...     consistency_score=62.5,
        ...     weeks_active=5,
        ...     recent_activity=3,
        ...     engagement_score=71,
        ...     risk_level="medium",
        ...     recommendations=["Send friendly reminder"],
        ...     timestamp="2024-01-15T10:30:00Z"
        ... )
    """

    user_id: str = Field(..., description="User UUID")
    user_name: str = Field(..., description="Full name of the user")
    period_days: int = Field(
        ..., description="Analysis period in days", ge=1, examples=[60]
    )
    total_events: int = Field(
        ..., description="Total events in period", ge=0, examples=[20]
    )
    attended_count: int = Field(
        ..., description="Number of events attended", ge=0, examples=[15]
    )
    attendance_rate: float = Field(
        ..., description="Attendance percentage (0-100)", ge=0, le=100, examples=[75.0]
    )
    consistency_score: float = Field(
        ...,
        description="Weekly attendance consistency (0-100)",
        ge=0,
        le=100,
        examples=[62.5],
    )
    weeks_active: int = Field(
        ..., description="Weeks with at least one attendance", ge=0, examples=[5]
    )
    recent_activity: int = Field(
        ..., description="Attendances in last 14 days", ge=0, examples=[3]
    )
    engagement_score: int = Field(
        ..., description="Overall engagement score (0-100)", ge=0, le=100, examples=[71]
    )
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="AI-determined risk level", examples=["medium"]
    )
    recommendations: List[str] = Field(
        ...,
        description="Personalized action recommendations",
        examples=[["Send friendly reminder about upcoming events"]],
    )
    timestamp: str = Field(
        ..., description="ISO timestamp of analysis", examples=["2024-01-15T10:30:00Z"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_name": "John Doe",
                "period_days": 60,
                "total_events": 20,
                "attended_count": 15,
                "attendance_rate": 75.0,
                "consistency_score": 62.5,
                "weeks_active": 5,
                "recent_activity": 3,
                "engagement_score": 71,
                "risk_level": "medium",
                "recommendations": [
                    "Send friendly reminder about upcoming events",
                    "Acknowledge their participation positively",
                ],
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


class AtRiskDetectionRequest(BaseModel):
    """
    Request schema for bulk at-risk youth detection.

    Attributes:
        min_risk_level: Minimum risk level threshold for inclusion

    Examples:
        >>> request = AtRiskDetectionRequest(min_risk_level="high")
    """

    min_risk_level: Literal["low", "medium", "high", "critical"] = Field(
        default="medium",
        description="Minimum risk level to include in results",
        examples=["medium"],
    )

    class Config:
        json_schema_extra = {"example": {"min_risk_level": "medium"}}


class AtRiskYouthResponse(BaseModel):
    """
    Response schema for individual at-risk youth in bulk detection.

    Attributes:
        user_id: UUID of at-risk user
        user_name: Full name of the user
        user_email: Email address for contact
        risk_level: AI-determined risk level
        engagement_score: Overall engagement score (0-100)
        attendance_rate: Attendance percentage (0-100)
        recommendations: Personalized intervention recommendations

    Examples:
        >>> youth = AtRiskYouthResponse(
        ...     user_id="123",
        ...     user_name="Jane Smith",
        ...     user_email="jane@example.com",
        ...     risk_level="high",
        ...     engagement_score=35,
        ...     attendance_rate=42.0,
        ...     recommendations=["Send personalized message/call to check in"]
        ... )
    """

    user_id: str = Field(..., description="User UUID")
    user_name: str = Field(..., description="Full name of the user")
    user_email: str = Field(..., description="Email address for contact")
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="AI-determined risk level"
    )
    engagement_score: int = Field(
        ..., description="Overall engagement score (0-100)", ge=0, le=100
    )
    attendance_rate: float = Field(
        ..., description="Attendance percentage (0-100)", ge=0, le=100
    )
    recommendations: List[str] = Field(
        ..., description="Personalized intervention recommendations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_name": "Jane Smith",
                "user_email": "jane@example.com",
                "risk_level": "high",
                "engagement_score": 35,
                "attendance_rate": 42.0,
                "recommendations": [
                    "Send personalized message/call to check in",
                    "Invite to upcoming special event",
                ],
            }
        }


class EngagementScoreItem(BaseModel):
    """
    Individual user engagement score item.

    Attributes:
        user_id: UUID of the user
        user_name: Full name of the user
        engagement_score: Overall engagement score (0-100)
        risk_level: AI-determined risk level
        attendance_rate: Attendance percentage (0-100)

    Examples:
        >>> item = EngagementScoreItem(
        ...     user_id="123",
        ...     user_name="Alex Johnson",
        ...     engagement_score=85,
        ...     risk_level="low",
        ...     attendance_rate=88.5
        ... )
    """

    user_id: str = Field(..., description="User UUID")
    user_name: str = Field(..., description="Full name of the user")
    engagement_score: int = Field(
        ..., description="Overall engagement score (0-100)", ge=0, le=100
    )
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="AI-determined risk level"
    )
    attendance_rate: float = Field(
        ..., description="Attendance percentage (0-100)", ge=0, le=100
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_name": "Alex Johnson",
                "engagement_score": 85,
                "risk_level": "low",
                "attendance_rate": 88.5,
            }
        }


class EngagementScoreResponse(BaseModel):
    """
    Response schema for engagement score analytics.

    Contains platform-wide engagement statistics with top and bottom performers.

    Attributes:
        total_users: Total number of active users analyzed
        average_engagement_score: Mean engagement score across all users
        average_attendance_rate: Mean attendance rate across all users
        top_10_engaged: List of 10 most engaged users
        bottom_10_engaged: List of 10 least engaged users (needs attention)
        timestamp: ISO timestamp of analysis

    Examples:
        >>> response = EngagementScoreResponse(
        ...     total_users=150,
        ...     average_engagement_score=68.5,
        ...     average_attendance_rate=72.3,
        ...     top_10_engaged=[],
        ...     bottom_10_engaged=[],
        ...     timestamp="2024-01-15T10:30:00Z"
        ... )
    """

    total_users: int = Field(
        ..., description="Total active users analyzed", ge=0, examples=[150]
    )
    average_engagement_score: float = Field(
        ...,
        description="Mean engagement score across all users",
        ge=0,
        le=100,
        examples=[68.5],
    )
    average_attendance_rate: float = Field(
        ...,
        description="Mean attendance rate across all users",
        ge=0,
        le=100,
        examples=[72.3],
    )
    top_10_engaged: List[EngagementScoreItem] = Field(
        ..., description="10 most engaged users"
    )
    bottom_10_engaged: List[EngagementScoreItem] = Field(
        ..., description="10 least engaged users (needs attention)"
    )
    timestamp: str = Field(
        ..., description="ISO timestamp of analysis", examples=["2024-01-15T10:30:00Z"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_users": 150,
                "average_engagement_score": 68.5,
                "average_attendance_rate": 72.3,
                "top_10_engaged": [
                    {
                        "user_id": "123",
                        "user_name": "Alice Brown",
                        "engagement_score": 95,
                        "risk_level": "low",
                        "attendance_rate": 96.0,
                    }
                ],
                "bottom_10_engaged": [
                    {
                        "user_id": "456",
                        "user_name": "Bob Wilson",
                        "engagement_score": 25,
                        "risk_level": "critical",
                        "attendance_rate": 22.0,
                    }
                ],
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


class InsightItem(BaseModel):
    """
    Individual AI-generated insight item.

    Attributes:
        type: Type of insight (positive/warning/alert)
        title: Short title summarizing the insight
        message: Detailed insight message
        action: Recommended action to take

    Examples:
        >>> insight = InsightItem(
        ...     type="warning",
        ...     title="Attendance Decline",
        ...     message="Attendance decreased by 15% in the last 30 days",
        ...     action="Review and adjust engagement programs"
        ... )
    """

    type: Literal["positive", "warning", "alert"] = Field(
        ...,
        description="Type of insight (positive=good news, warning=needs attention, alert=urgent)",
        examples=["warning"],
    )
    title: str = Field(
        ...,
        description="Short title summarizing the insight",
        min_length=1,
        max_length=100,
        examples=["Attendance Decline"],
    )
    message: str = Field(
        ...,
        description="Detailed insight message",
        min_length=1,
        max_length=500,
        examples=["Attendance decreased by 15% in the last 30 days"],
    )
    action: str = Field(
        ...,
        description="Recommended action to take",
        min_length=1,
        max_length=200,
        examples=["Review and adjust engagement programs"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "warning",
                "title": "Attendance Decline",
                "message": "Attendance decreased by 15% in the last 30 days",
                "action": "Review and adjust engagement programs",
            }
        }


class InsightsResponse(BaseModel):
    """
    Response schema for automated AI-generated insights.

    Contains AI-analyzed patterns and trends with actionable recommendations.

    Attributes:
        insights: List of AI-generated insights
        statistics: Supporting statistical data
        timestamp: ISO timestamp of analysis

    Examples:
        >>> response = InsightsResponse(
        ...     insights=[],
        ...     statistics={"total_active_users": 150},
        ...     timestamp="2024-01-15T10:30:00Z"
        ... )
    """

    insights: List[InsightItem] = Field(
        ..., description="List of AI-generated insights"
    )
    statistics: dict = Field(
        ..., description="Supporting statistical data for insights"
    )
    timestamp: str = Field(
        ..., description="ISO timestamp of analysis", examples=["2024-01-15T10:30:00Z"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "insights": [
                    {
                        "type": "positive",
                        "title": "Attendance Growth",
                        "message": "Attendance increased by 12.5% in the last 30 days",
                        "action": "Continue current engagement strategies",
                    },
                    {
                        "type": "alert",
                        "title": "Low Engagement",
                        "message": "Average attendance is 1.5 per user this month",
                        "action": "Increase event frequency or improve event appeal",
                    },
                ],
                "statistics": {
                    "total_active_users": 150,
                    "recent_attendance": 225,
                    "previous_attendance": 200,
                    "trend_percentage": 12.5,
                },
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }
