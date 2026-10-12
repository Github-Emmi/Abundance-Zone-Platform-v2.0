"""
AI/ML Background Tasks
Intelligent analytics, predictions, and risk detection
"""

from typing import Dict, List
from datetime import datetime, timedelta
import logging

from sqlalchemy import select, func, and_

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.models.attendance import AttendanceModel
from app.infrastructure.database.models.event import EventModel
from app.domain.value_objects.enums import AttendanceStatus

# Configure logging
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# AI/ML UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def calculate_attendance_rate(attended: int, total_events: int) -> float:
    """Calculate attendance rate percentage"""
    if total_events == 0:
        return 0.0
    return round((attended / total_events) * 100, 2)


def determine_risk_level(attendance_rate: float, consistency_score: float) -> str:
    """
    Determine risk level based on attendance and consistency

    Returns: 'low', 'medium', 'high', 'critical'
    """
    if attendance_rate >= 80 and consistency_score >= 70:
        return "low"
    elif attendance_rate >= 60 and consistency_score >= 50:
        return "medium"
    elif attendance_rate >= 40:
        return "high"
    else:
        return "critical"


def calculate_engagement_score(
    attendance_rate: float, consistency_score: float, recent_activity: int
) -> int:
    """
    Calculate overall engagement score (0-100)

    Weighted formula:
    - 50% attendance rate
    - 30% consistency
    - 20% recent activity
    """
    score = (
        (attendance_rate * 0.5)
        + (consistency_score * 0.3)
        + (min(recent_activity * 10, 100) * 0.2)
    )
    return round(score)


# ═══════════════════════════════════════════════════════════════════════════
# AI/ML CELERY TASKS
# ═══════════════════════════════════════════════════════════════════════════


@celery_app.task(name="app.tasks.ai_ml.predict_attendance_risk", bind=True)
def predict_attendance_risk(self, user_id: str) -> Dict:
    """
    Predict if user is at risk of becoming inactive

    Args:
        user_id: User UUID

    Returns:
        Dict with risk analysis
    """
    import asyncio

    async def _predict():
        try:
            logger.info(f"Analyzing attendance risk for user {user_id}")

            async with AsyncSessionLocal() as session:
                # Get user
                user_result = await session.execute(
                    select(UserModel).where(UserModel.id == user_id)
                )
                user = user_result.scalar_one_or_none()

                if not user:
                    return {"status": "error", "message": "User not found"}

                # Get attendance history (last 60 days)
                sixty_days_ago = datetime.utcnow() - timedelta(days=60)

                attendance_query = (
                    select(AttendanceModel)
                    .where(
                        and_(
                            AttendanceModel.user_id == user_id,
                            AttendanceModel.check_in_time >= sixty_days_ago,
                            AttendanceModel.status.in_(
                                [AttendanceStatus.PRESENT, AttendanceStatus.LATE]
                            ),
                        )
                    )
                    .order_by(AttendanceModel.check_in_time)
                )

                attendance_result = await session.execute(attendance_query)
                attendance_records = attendance_result.scalars().all()

                # Get total events in same period
                events_query = select(func.count(EventModel.id)).where(
                    EventModel.start_time >= sixty_days_ago
                )
                events_result = await session.execute(events_query)
                total_events = events_result.scalar() or 0

                # Calculate metrics
                attended_count = len(attendance_records)
                attendance_rate = calculate_attendance_rate(
                    attended_count, total_events
                )

                # Calculate consistency (attendance every week)
                weeks_active = len(
                    set(
                        record.check_in_time.isocalendar()[1]
                        for record in attendance_records
                    )
                )
                consistency_score = (
                    round((weeks_active / 8) * 100, 2) if weeks_active else 0
                )

                # Recent activity (last 14 days)
                fourteen_days_ago = datetime.utcnow() - timedelta(days=14)
                recent_attendance = sum(
                    1
                    for record in attendance_records
                    if record.check_in_time >= fourteen_days_ago
                )

                # Determine risk level
                risk_level = determine_risk_level(attendance_rate, consistency_score)

                # Calculate engagement score
                engagement_score = calculate_engagement_score(
                    attendance_rate, consistency_score, recent_attendance
                )

                logger.info(
                    f"Risk analysis complete for {user.name}: "
                    f"Risk={risk_level}, Engagement={engagement_score}"
                )

                return {
                    "user_id": user_id,
                    "user_name": user.name,
                    "user_email": user.email,
                    "period_days": 60,
                    "total_events": total_events,
                    "attended_count": attended_count,
                    "attendance_rate": attendance_rate,
                    "consistency_score": consistency_score,
                    "weeks_active": weeks_active,
                    "recent_activity": recent_attendance,
                    "engagement_score": engagement_score,
                    "risk_level": risk_level,
                    "recommendations": get_recommendations(risk_level, attendance_rate),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as exc:
            logger.error(f"Failed to predict attendance risk: {str(exc)}")
            raise

    return asyncio.run(_predict())


def get_recommendations(risk_level: str, attendance_rate: float) -> List[str]:
    """Generate personalized recommendations based on risk level"""
    recommendations = []

    if risk_level == "critical":
        recommendations = [
            "Immediate intervention required - contact youth coordinator",
            "Schedule one-on-one meeting to understand barriers",
            "Consider home visit if appropriate",
            "Assign mentor or buddy for support",
        ]
    elif risk_level == "high":
        recommendations = [
            "Send personalized message/call to check in",
            "Invite to upcoming special event",
            "Connect with peers who attend regularly",
            "Identify and address any obstacles",
        ]
    elif risk_level == "medium":
        recommendations = [
            "Send friendly reminder about upcoming events",
            "Acknowledge their participation positively",
            "Invite to join a small group or team",
        ]
    else:  # low
        recommendations = [
            "Continue positive reinforcement",
            "Consider as peer mentor for at-risk youth",
            "Recognize their consistency publicly",
        ]

    return recommendations


@celery_app.task(name="app.tasks.ai_ml.detect_at_risk_youths", bind=True)
def detect_at_risk_youths(self, min_risk_level: str = "medium") -> Dict:
    """
    Detect all at-risk youths and generate alerts

    Args:
        min_risk_level: Minimum risk level to include (medium, high, critical)

    Returns:
        Dict with list of at-risk youths
    """
    import asyncio

    async def _detect():
        try:
            logger.info(f"Detecting at-risk youths (min level: {min_risk_level})")

            async with AsyncSessionLocal() as session:
                # Get all active users
                users_query = select(UserModel).where(UserModel.is_active is True)
                users_result = await session.execute(users_query)
                users = users_result.scalars().all()

                at_risk_users = []
                risk_levels = {"critical": [], "high": [], "medium": [], "low": []}

                for user in users:
                    # Analyze each user
                    analysis = await asyncio.create_task(
                        asyncio.to_thread(predict_attendance_risk, user.id)
                    )

                    risk_level = analysis.get("risk_level", "low")
                    risk_levels[risk_level].append(analysis)

                    # Filter by minimum risk level
                    if min_risk_level == "critical" and risk_level == "critical":
                        at_risk_users.append(analysis)
                    elif min_risk_level == "high" and risk_level in [
                        "critical",
                        "high",
                    ]:
                        at_risk_users.append(analysis)
                    elif min_risk_level == "medium" and risk_level in [
                        "critical",
                        "high",
                        "medium",
                    ]:
                        at_risk_users.append(analysis)

                # Sort by risk level and engagement score
                risk_priority = {"critical": 0, "high": 1, "medium": 2, "low": 3}
                at_risk_users.sort(
                    key=lambda x: (
                        risk_priority[x["risk_level"]],
                        x["engagement_score"],
                    )
                )

                logger.info(
                    f"At-risk detection complete: "
                    f"{len(risk_levels['critical'])} critical, "
                    f"{len(risk_levels['high'])} high, "
                    f"{len(risk_levels['medium'])} medium"
                )

                # TODO: Send alerts to coordinators
                # TODO: Queue follow-up tasks (emails, notifications)

                return {
                    "status": "completed",
                    "total_analyzed": len(users),
                    "at_risk_count": len(at_risk_users),
                    "critical_count": len(risk_levels["critical"]),
                    "high_count": len(risk_levels["high"]),
                    "medium_count": len(risk_levels["medium"]),
                    "low_count": len(risk_levels["low"]),
                    "at_risk_users": at_risk_users,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as exc:
            logger.error(f"Failed to detect at-risk youths: {str(exc)}")
            raise

    return asyncio.run(_detect())


@celery_app.task(name="app.tasks.ai_ml.calculate_engagement_scores", bind=True)
def calculate_engagement_scores(self) -> Dict:
    """
    Calculate engagement scores for all active users

    Returns:
        Dict with engagement statistics
    """
    import asyncio

    async def _calculate():
        try:
            logger.info("Calculating engagement scores for all users")

            async with AsyncSessionLocal() as session:
                users_query = select(UserModel).where(UserModel.is_active is True)
                users_result = await session.execute(users_query)
                users = users_result.scalars().all()

                engagement_data = []

                for user in users:
                    analysis = await asyncio.create_task(
                        asyncio.to_thread(predict_attendance_risk, user.id)
                    )

                    engagement_data.append(
                        {
                            "user_id": user.id,
                            "user_name": user.name,
                            "engagement_score": analysis.get("engagement_score", 0),
                            "risk_level": analysis.get("risk_level", "low"),
                            "attendance_rate": analysis.get("attendance_rate", 0),
                        }
                    )

                # Sort by engagement score
                engagement_data.sort(key=lambda x: x["engagement_score"], reverse=True)

                # Calculate averages
                avg_score = (
                    sum(u["engagement_score"] for u in engagement_data)
                    / len(engagement_data)
                    if engagement_data
                    else 0
                )
                avg_attendance = (
                    sum(u["attendance_rate"] for u in engagement_data)
                    / len(engagement_data)
                    if engagement_data
                    else 0
                )

                logger.info(
                    f"Engagement calculation complete: "
                    f"Avg score={avg_score:.2f}, Avg attendance={avg_attendance:.2f}%"
                )

                return {
                    "status": "completed",
                    "total_users": len(users),
                    "average_engagement_score": round(avg_score, 2),
                    "average_attendance_rate": round(avg_attendance, 2),
                    "top_10_engaged": engagement_data[:10],
                    "bottom_10_engaged": (
                        engagement_data[-10:] if len(engagement_data) >= 10 else []
                    ),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as exc:
            logger.error(f"Failed to calculate engagement scores: {str(exc)}")
            raise

    return asyncio.run(_calculate())


@celery_app.task(name="app.tasks.ai_ml.generate_insights", bind=True)
def generate_insights(self) -> Dict:
    """
    Generate automated insights from platform data

    Returns:
        Dict with AI-generated insights
    """
    import asyncio

    async def _generate():
        try:
            logger.info("Generating automated insights")

            async with AsyncSessionLocal() as session:
                # Get overall statistics
                total_users_query = select(func.count(UserModel.id)).where(
                    UserModel.is_active is True
                )
                total_users = (await session.execute(total_users_query)).scalar() or 0

                # Get attendance trends (last 30 days vs previous 30 days)
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                sixty_days_ago = datetime.utcnow() - timedelta(days=60)

                recent_attendance_query = select(func.count(AttendanceModel.id)).where(
                    AttendanceModel.check_in_time >= thirty_days_ago
                )
                recent_attendance = (
                    await session.execute(recent_attendance_query)
                ).scalar() or 0

                previous_attendance_query = select(
                    func.count(AttendanceModel.id)
                ).where(
                    and_(
                        AttendanceModel.check_in_time >= sixty_days_ago,
                        AttendanceModel.check_in_time < thirty_days_ago,
                    )
                )
                previous_attendance = (
                    await session.execute(previous_attendance_query)
                ).scalar() or 0

                # Calculate trend
                if previous_attendance > 0:
                    trend_percentage = (
                        (recent_attendance - previous_attendance) / previous_attendance
                    ) * 100
                else:
                    trend_percentage = 100.0 if recent_attendance > 0 else 0.0

                # Generate insights
                insights = []

                if trend_percentage > 10:
                    insights.append(
                        {
                            "type": "positive",
                            "title": "Attendance Growth",
                            "message": f"Attendance increased by {trend_percentage:.1f}% in the last 30 days",
                            "action": "Continue current engagement strategies",
                        }
                    )
                elif trend_percentage < -10:
                    insights.append(
                        {
                            "type": "warning",
                            "title": "Attendance Decline",
                            "message": f"Attendance decreased by {abs(trend_percentage):.1f}% in the last 30 days",
                            "action": "Review and adjust engagement programs",
                        }
                    )

                # Add more insights based on data patterns
                if total_users > 0:
                    avg_attendance_per_user = recent_attendance / total_users
                    if avg_attendance_per_user < 2:
                        insights.append(
                            {
                                "type": "alert",
                                "title": "Low Engagement",
                                "message": f"Average attendance is {avg_attendance_per_user:.1f} per user this month",
                                "action": "Increase event frequency or improve event appeal",
                            }
                        )

                logger.info(f"Generated {len(insights)} insights")

                return {
                    "status": "completed",
                    "insights": insights,
                    "statistics": {
                        "total_active_users": total_users,
                        "recent_attendance": recent_attendance,
                        "previous_attendance": previous_attendance,
                        "trend_percentage": round(trend_percentage, 2),
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as exc:
            logger.error(f"Failed to generate insights: {str(exc)}")
            raise

    return asyncio.run(_generate())
