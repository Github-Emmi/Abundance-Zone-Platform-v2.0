"""
Unit tests for pagination utilities.

Tests PaginationParams model and get_pagination_params dependency function.
Validates FR-API-003 compliance.
"""

import pytest
from pydantic import ValidationError

from app.api.schemas.pagination import PaginationParams, get_pagination_params


class TestPaginationParams:
    """Test suite for PaginationParams model."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        params = PaginationParams()
        
        assert params.page == 1
        assert params.page_size == 20
        assert params.sort is None
        assert params.order == "desc"
    
    def test_custom_values(self):
        """Test that custom values are accepted."""
        params = PaginationParams(
            page=5,
            page_size=50,
            sort="name",
            order="asc"
        )
        
        assert params.page == 5
        assert params.page_size == 50
        assert params.sort == "name"
        assert params.order == "asc"
    
    def test_page_minimum_validation(self):
        """Test that page must be at least 1."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page=0)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "page" in str(errors[0])
    
    def test_page_negative_validation(self):
        """Test that negative page numbers are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page=-1)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
    
    def test_page_size_minimum_validation(self):
        """Test that page_size must be at least 1."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page_size=0)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "page_size" in str(errors[0])
    
    def test_page_size_maximum_validation(self):
        """Test that page_size cannot exceed 100."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page_size=101)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "page_size" in str(errors[0])
    
    def test_page_size_boundary_values(self):
        """Test boundary values for page_size (1 and 100 should be valid)."""
        # Test minimum boundary
        params_min = PaginationParams(page_size=1)
        assert params_min.page_size == 1
        
        # Test maximum boundary
        params_max = PaginationParams(page_size=100)
        assert params_max.page_size == 100
    
    def test_order_validation(self):
        """Test that order only accepts 'asc' or 'desc'."""
        # Valid values
        params_asc = PaginationParams(order="asc")
        assert params_asc.order == "asc"
        
        params_desc = PaginationParams(order="desc")
        assert params_desc.order == "desc"
        
        # Invalid value should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(order="invalid")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "order" in str(errors[0])
    
    def test_offset_calculation(self):
        """Test that offset is calculated correctly."""
        # Page 1: offset should be 0
        params1 = PaginationParams(page=1, page_size=20)
        assert params1.offset == 0
        
        # Page 2: offset should be 20
        params2 = PaginationParams(page=2, page_size=20)
        assert params2.offset == 20
        
        # Page 3 with page_size 50: offset should be 100
        params3 = PaginationParams(page=3, page_size=50)
        assert params3.offset == 100
        
        # Page 10 with page_size 25: offset should be 225
        params4 = PaginationParams(page=10, page_size=25)
        assert params4.offset == 225
    
    def test_limit_property(self):
        """Test that limit returns page_size."""
        params = PaginationParams(page_size=30)
        assert params.limit == 30
        assert params.limit == params.page_size


class TestGetPaginationParams:
    """Test suite for get_pagination_params dependency function."""
    
    def test_dependency_with_custom_values(self):
        """Test dependency function with custom values passed as integers."""
        # The dependency is designed to be used with FastAPI which extracts
        # values from query parameters. For direct testing, we pass actual values.
        params = get_pagination_params(
            page=3,
            page_size=50,
            sort="email",
            order="asc"
        )
        
        assert params.page == 3
        assert params.page_size == 50
        assert params.sort == "email"
        assert params.order == "asc"
    
    def test_dependency_returns_pagination_params_instance(self):
        """Test that dependency returns PaginationParams instance."""
        params = get_pagination_params(
            page=1,
            page_size=20,
            sort=None,
            order="desc"
        )
        assert isinstance(params, PaginationParams)
    
    def test_dependency_computed_properties(self):
        """Test that returned instance has working computed properties."""
        params = get_pagination_params(
            page=2,
            page_size=30,
            sort=None,
            order="desc"
        )
        
        assert params.offset == 30
        assert params.limit == 30


class TestPaginationIntegration:
    """Integration tests for pagination in realistic scenarios."""
    
    def test_pagination_scenario_first_page(self):
        """Test pagination for fetching first page of results."""
        params = PaginationParams(page=1, page_size=10)
        
        assert params.offset == 0
        assert params.limit == 10
        # Simulates: SELECT * FROM table OFFSET 0 LIMIT 10
    
    def test_pagination_scenario_middle_page(self):
        """Test pagination for fetching a middle page."""
        params = PaginationParams(page=5, page_size=20)
        
        assert params.offset == 80
        assert params.limit == 20
        # Simulates: SELECT * FROM table OFFSET 80 LIMIT 20
    
    def test_pagination_scenario_with_sorting(self):
        """Test pagination with sorting parameters."""
        params = PaginationParams(
            page=2,
            page_size=25,
            sort="created_at",
            order="desc"
        )
        
        assert params.page == 2
        assert params.offset == 25
        assert params.limit == 25
        assert params.sort == "created_at"
        assert params.order == "desc"
        # Simulates: SELECT * FROM table ORDER BY created_at DESC OFFSET 25 LIMIT 25
    
    def test_pagination_scenario_large_page_size(self):
        """Test pagination with maximum allowed page size."""
        params = PaginationParams(page=1, page_size=100)
        
        assert params.offset == 0
        assert params.limit == 100
    
    def test_pagination_edge_case_high_page_number(self):
        """Test pagination with very high page numbers."""
        params = PaginationParams(page=1000, page_size=50)
        
        assert params.offset == 49950
        assert params.limit == 50
