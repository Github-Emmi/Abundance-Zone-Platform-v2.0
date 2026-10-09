"""Response Schema Tests"""
import pytest
from datetime import datetime
from app.api.schemas.responses import ApiResponse, ErrorResponse, ErrorDetail, PaginatedResponse


def test_api_response_success():
    """Test successful API response"""
    data = {"id": "123", "name": "Test"}
    response = ApiResponse(data=data)
    
    assert response.success is True
    assert response.data == data
    assert response.meta is None
    assert isinstance(response.timestamp, datetime)


def test_api_response_with_meta():
    """Test API response with metadata"""
    data = {"id": "123"}
    meta = {"version": "1.0"}
    response = ApiResponse(data=data, meta=meta)
    
    assert response.meta == meta


def test_error_response():
    """Test error response"""
    error = ErrorDetail(code="TEST_ERROR", message="Test error message")
    response = ErrorResponse(error=error)
    
    assert response.success is False
    assert response.error.code == "TEST_ERROR"
    assert response.error.message == "Test error message"


def test_error_detail_code_uppercase():
    """Test error code is converted to uppercase"""
    error = ErrorDetail(code="test_error", message="Test")
    assert error.code == "TEST_ERROR"


def test_paginated_response():
    """Test paginated response"""
    items = [{"id": "1"}, {"id": "2"}]
    response = PaginatedResponse(
        items=items, total=10, page=1, page_size=5, has_next=True
    )
    
    assert len(response.items) == 2
    assert response.total == 10
    assert response.page == 1
    assert response.page_size == 5
    assert response.has_next is True
    assert response.total_pages == 2


def test_paginated_response_no_next():
    """Test paginated response on last page"""
    items = [{"id": "1"}]
    response = PaginatedResponse(
        items=items, total=5, page=3, page_size=2, has_next=False
    )
    
    assert response.has_next is False
    assert response.total_pages == 3
