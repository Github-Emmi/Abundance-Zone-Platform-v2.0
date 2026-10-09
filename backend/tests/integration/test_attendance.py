"""Attendance Integration Tests"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_record_attendance(
    client: AsyncClient,
    auth_headers,
    test_event,
    test_youth
):
    """Test recording single attendance"""
    response = await client.post(
        "/api/v1/attendance",
        headers=auth_headers,
        json={
            "event_id": test_event.id,
            "youth_id": test_youth.id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_record_bulk_attendance(
    client: AsyncClient,
    auth_headers,
    test_event,
    test_youth
):
    """Test recording bulk attendance"""
    response = await client.post(
        "/api/v1/attendance/bulk",
        headers=auth_headers,
        json={
            "event_id": test_event.id,
            "youth_ids": [test_youth.id]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 1


@pytest.mark.asyncio
async def test_get_attendance_summary(
    client: AsyncClient,
    auth_headers,
    test_branch
):
    """Test getting attendance summary"""
    response = await client.get(
        f"/api/v1/attendance/summary?branch_id={test_branch.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_events" in data["data"]
