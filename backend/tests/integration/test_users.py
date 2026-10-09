"""User Management Integration Tests"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, auth_headers, super_admin_user):
    """Test listing users with pagination"""
    response = await client.get(
        "/api/v1/users?page=1&page_size=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "total" in data["data"]


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, auth_headers, super_admin_user):
    """Test getting user by ID"""
    response = await client.get(
        f"/api/v1/users/{super_admin_user.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == super_admin_user.id


@pytest.mark.asyncio
async def test_create_user_super_admin_only(
    client: AsyncClient,
    coordinator_headers,
    test_branch
):
    """Test that only SUPER_ADMIN can create users"""
    response = await client.post(
        "/api/v1/users",
        headers=coordinator_headers,
        json={
            "name": "Test User",
            "email": "testuser@test.com",
            "password": "Test123!",
            "role": "YOUTH_MEMBER",
            "branch_id": test_branch.id
        }
    )
    assert response.status_code == 403
