"""Department Management Integration Tests"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_department(client: AsyncClient, auth_headers, test_branch):
    """Test creating a department"""
    response = await client.post(
        "/api/v1/departments",
        headers=auth_headers,
        json={
            "name": "New Department",
            "branch_id": test_branch.id,
            "description": "Test department"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "New Department"


@pytest.mark.asyncio
async def test_list_departments(
    client: AsyncClient,
    auth_headers,
    test_branch,
    test_department
):
    """Test listing departments"""
    response = await client.get(
        f"/api/v1/departments?branch_id={test_branch.id}&page=1&page_size=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) > 0
