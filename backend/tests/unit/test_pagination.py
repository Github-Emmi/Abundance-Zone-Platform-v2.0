"""Pagination Tests"""
import pytest
from app.api.schemas.pagination import PaginationParams


def test_pagination_defaults():
    """Test pagination with default values"""
    params = PaginationParams()
    assert params.page == 1
    assert params.page_size == 20
    assert params.order == "desc"
    assert params.offset == 0
    assert params.limit == 20


def test_pagination_custom_values():
    """Test pagination with custom values"""
    params = PaginationParams(page=3, page_size=50, order="asc")
    assert params.page == 3
    assert params.page_size == 50
    assert params.order == "asc"
    assert params.offset == 100  # (3-1) * 50
    assert params.limit == 50


def test_pagination_validation_min_page():
    """Test page number validation"""
    with pytest.raises(Exception):
        PaginationParams(page=0)


def test_pagination_validation_max_page_size():
    """Test page size validation"""
    with pytest.raises(Exception):
        PaginationParams(page_size=101)


def test_pagination_validation_min_page_size():
    """Test minimum page size validation"""
    with pytest.raises(Exception):
        PaginationParams(page_size=0)
