"""Simplified Test Fixtures"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    """Create test HTTP client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer mock_token"}
