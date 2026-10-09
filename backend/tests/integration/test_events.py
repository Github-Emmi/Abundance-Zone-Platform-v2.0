"""Event Management Integration Tests"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_create_event(client: AsyncClient, auth_headers, test_branch):
    """Test creating an event"""
    future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    response = await client.post(
        "/api/v1/events",
        headers=auth_headers,
        json={
            "title": "New Event",
            "event_type": "WORSHIP_SERVICE",
            "event_date": future_date,
            "branch_id": test_branch.id,
            "venue": "Test Venue"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "New Event"


@pytest.mark.asyncio
async def test_list_events(client: AsyncClient, auth_headers, test_branch, test_event):
    """Test listing events"""
    response = await client.get(
        f"/api/v1/events?branch_id={test_branch.id}&page=1&page_size=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) > 0
