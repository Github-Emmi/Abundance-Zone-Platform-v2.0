"""Youth Management Integration Tests"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_youth(client: AsyncClient, auth_headers, test_branch):
    """Test creating a youth profile"""
    response = await client.post(
        "/api/v1/youths",
        headers=auth_headers,
        json={
            "fullname": "New Youth",
            "email": "newyouth@test.com",
            "phone": "5556667777",
            "gender": "MALE",
            "branch_id": test_branch.id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["fullname"] == "New Youth"


@pytest.mark.asyncio
async def test_list_youths(client: AsyncClient, auth_headers, test_branch, test_youth):
    """Test listing youths"""
    response = await client.get(
        f"/api/v1/youths?branch_id={test_branch.id}&page=1&page_size=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) > 0


@pytest.mark.asyncio
async def test_search_youths(client: AsyncClient, auth_headers, test_youth):
    """Test searching youths"""
    response = await client.get(
        f"/api/v1/youths/search?query=Test&page=1&page_size=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
