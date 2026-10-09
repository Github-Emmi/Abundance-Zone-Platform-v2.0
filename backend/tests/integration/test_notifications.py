"""Notification Integration Tests"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_notifications(client: AsyncClient, auth_headers):
    """Test listing user notifications"""
    response = await client.get(
        "/api/v1/notifications?page=1&page_size=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]


@pytest.mark.asyncio
async def test_mark_all_as_read(client: AsyncClient, auth_headers):
    """Test marking all notifications as read"""
    response = await client.post(
        "/api/v1/notifications/read-all",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
