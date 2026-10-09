"""Branch Management Integration Tests"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_branch(client: AsyncClient, auth_headers):
    """Test creating a branch"""
    response = await client.post(
        "/api/v1/branches",
        headers=auth_headers,
        json={
            "name": "New Branch",
            "location": "New City",
            "address": "456 New St",
            "phone": "1112223333"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "New Branch"


@pytest.mark.asyncio
async def test_list_branches(client: AsyncClient, auth_headers, test_branch):
    """Test listing branches"""
    response = await client.get(
        "/api/v1/branches?page=1&page_size=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) > 0


@pytest.mark.asyncio
async def test_get_branch_statistics(
    client: AsyncClient,
    auth_headers,
    test_branch
):
    """Test getting branch statistics"""
    response = await client.get(
        f"/api/v1/branches/{test_branch.id}/statistics",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "youth_count" in data["data"]
    assert "department_count" in data["data"]
