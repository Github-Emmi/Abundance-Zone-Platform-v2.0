"""
Integration Tests for Pagination with FastAPI

Tests the pagination utilities in a FastAPI application context.
"""

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.api.schemas.pagination import PaginationParams, get_pagination_params


# Create a minimal test app
app = FastAPI()


@app.get("/items")
async def list_items(pagination: PaginationParams = Depends(get_pagination_params)):
    """Test endpoint that uses pagination dependency."""
    return {
        "page": pagination.page,
        "page_size": pagination.page_size,
        "offset": pagination.offset,
        "limit": pagination.limit,
        "sort": pagination.sort,
        "order": pagination.order,
    }


client = TestClient(app)


class TestPaginationInFastAPI:
    """Test pagination dependency in FastAPI context."""
    
    def test_default_query_parameters(self):
        """Test pagination with default query parameters."""
        response = client.get("/items")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["offset"] == 0
        assert data["limit"] == 20
        assert data["sort"] is None
        assert data["order"] == "desc"
    
    def test_custom_query_parameters(self):
        """Test pagination with custom query parameters."""
        response = client.get("/items?page=3&page_size=50&sort=name&order=asc")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 3
        assert data["page_size"] == 50
        assert data["offset"] == 100
        assert data["limit"] == 50
        assert data["sort"] == "name"
        assert data["order"] == "asc"
    
    def test_partial_query_parameters(self):
        """Test pagination with only some query parameters specified."""
        response = client.get("/items?page=5&sort=created_at")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 5
        assert data["page_size"] == 20  # default
        assert data["offset"] == 80
        assert data["sort"] == "created_at"
        assert data["order"] == "desc"  # default
    
    def test_invalid_page_returns_422(self):
        """Test that invalid page number returns 422 validation error."""
        response = client.get("/items?page=0")
        
        assert response.status_code == 422
        data = response.json()
        
        assert "detail" in data
        errors = data["detail"]
        assert any(error["loc"] == ["query", "page"] for error in errors)
    
    def test_invalid_page_size_returns_422(self):
        """Test that invalid page_size returns 422 validation error."""
        response = client.get("/items?page_size=150")
        
        assert response.status_code == 422
        data = response.json()
        
        assert "detail" in data
        errors = data["detail"]
        assert any(error["loc"] == ["query", "page_size"] for error in errors)
    
    def test_invalid_order_returns_422(self):
        """Test that invalid order value returns 422 validation error."""
        response = client.get("/items?order=invalid")
        
        assert response.status_code == 422
        data = response.json()
        
        assert "detail" in data
        errors = data["detail"]
        assert any(error["loc"] == ["query", "order"] for error in errors)
    
    def test_boundary_values(self):
        """Test pagination with boundary values."""
        # Minimum valid values
        response = client.get("/items?page=1&page_size=1")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 1
        
        # Maximum valid page_size
        response = client.get("/items?page=1&page_size=100")
        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 100
    
    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are returned together."""
        response = client.get("/items?page=-1&page_size=200&order=wrong")
        
        assert response.status_code == 422
        data = response.json()
        
        errors = data["detail"]
        error_locations = [tuple(error["loc"]) for error in errors]
        
        # Should have errors for all three invalid parameters
        assert ("query", "page") in error_locations
        assert ("query", "page_size") in error_locations
        assert ("query", "order") in error_locations
    
    def test_large_page_number(self):
        """Test pagination with large page numbers."""
        response = client.get("/items?page=1000&page_size=50")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1000
        assert data["offset"] == 49950
        assert data["limit"] == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
