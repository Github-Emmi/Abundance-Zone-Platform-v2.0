"""Comprehensive Service Layer Tests"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.application.services.attendance_service import AttendanceService
from app.application.services.event_service import EventService
from app.application.services.notification_service import NotificationService
from app.infrastructure.database.models.attendance import AttendanceModel
from app.infrastructure.database.models.event import EventModel
from app.infrastructure.database.models.notification import NotificationModel
from app.domain.value_objects.enums import EventType, EventStatus, NotificationType, NotificationChannel


@pytest.mark.asyncio
async def test_attendance_service_record_single():
    """Test recording single attendance"""
    mock_repo = AsyncMock()
    service = AttendanceService(attendance_repo=mock_repo)
    
    mock_attendance = AttendanceModel(
        id="att-1", event_id="evt-1", youth_id="youth-1"
    )
    mock_repo.record_attendance.return_value = mock_attendance
    
    db = AsyncMock()
    result = await service.record_single("evt-1", "youth-1", db)
    
    assert result.event_id == "evt-1"
    mock_repo.record_attendance.assert_called_once()


@pytest.mark.asyncio
async def test_attendance_service_record_bulk():
    """Test bulk attendance recording"""
    mock_repo = AsyncMock()
    service = AttendanceService(attendance_repo=mock_repo)
    
    mock_attendances = [
        AttendanceModel(id="att-1", event_id="evt-1", youth_id="youth-1"),
        AttendanceModel(id="att-2", event_id="evt-1", youth_id="youth-2")
    ]
    mock_repo.bulk_record.return_value = mock_attendances
    
    db = AsyncMock()
    result = await service.record_bulk("evt-1", ["youth-1", "youth-2"], db)
    
    assert len(result) == 2
    mock_repo.bulk_record.assert_called_once()


@pytest.mark.asyncio
async def test_event_service_create_event():
    """Test creating an event"""
    mock_repo = AsyncMock()
    service = EventService(event_repo=mock_repo)
    
    from datetime import datetime
    mock_event = EventModel(
        id="evt-1", title="Test Event", event_type=EventType.SUNDAY_SERVICE.value,
        event_date=datetime.utcnow(), branch_id="branch-1", created_by_id="user-1"
    )
    mock_repo.save.return_value = mock_event
    
    db = AsyncMock()
    result = await service.create_event(
        "Test Event", EventType.SUNDAY_SERVICE, datetime.utcnow(),
        "branch-1", "user-1", None, None, None, db
    )
    
    assert result.title == "Test Event"
    mock_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_notification_service_broadcast():
    """Test broadcasting notification to branch"""
    mock_repo = AsyncMock()
    service = NotificationService(notif_repo=mock_repo)
    
    mock_repo.broadcast_to_branch.return_value = 5
    
    db = AsyncMock()
    count = await service.broadcast_to_branch(
        "branch-1", "Test Title", "Test Content",
        NotificationType.ANNOUNCEMENT, db
    )
    
    assert count == 5
    mock_repo.broadcast_to_branch.assert_called_once()
