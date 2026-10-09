"""
Unit Tests for Pagination Utilities

Tests the PaginationParams model and get_pagination_params dependency.
Validates FR-API-003: Pagination Standard.
"""

import pytest
from pydantic import ValidationError

from app.api.schemas.pagination import PaginationParams, get_pagination_params


class TestPaginationParams:
    """Test suite for PaginationParams model."""
    
    def test_default_values(self):
        """Test that default values are correctly set."""
        params = PaginationParams()
        
        assert params.page == 1
        assert params.page_size == 20
        assert params.sort is None
        assert params.order == "desc"
    
    def test_custom_values(self):
        """Test creating PaginationParams with custom values."""
        params = PaginationParams(
            page=3,
            page_size=50,
            sort="name",
            order="asc"
        )
        
        assert params.page == 3
        assert params.page_size == 50
        assert params.sort == "name"
        assert params.order == "asc"
    
    def test_offset_calculation_first_page(self):
        """Test offset calculation for first page."""
        params = PaginationParams(page=1, page_size=20)
        assert params.offset == 0
    
    def test_offset_calculation_second_page(self):
        """Test offset calculation for second page."""
        params = PaginationParams(page=2, page_size=20)
        assert params.offset == 20
    
    def test_offset_calculation_third_page(self):
        """Test offset calculation for third page with custom page size."""
        params = PaginationParams(page=3, page_size=50)
        assert params.offset == 100
    
    def test_offset_calculation_large_page(self):
        """Test offset calculation for large page numbers."""
        params = PaginationParams(page=10, page_size=25)
        assert params.offset == 225
    
    def test_limit_property(self):
        """Test that limit property returns page_size."""
        params = PaginationParams(page_size=30)
        assert params.limit == 30
        
        params2 = PaginationParams(page_size=100)
        assert params2.limit == 100
    
    def test_page_validation_minimum(self):
        """Test that page must be at least 1."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page=0)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("page",)
        assert "greater than or equal to 1" in str(errors[0]["msg"]).lower()
    
    def test_page_validation_negative(self):
        """Test that negative page numbers are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page=-1)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("page",)
    
    def test_page_size_validation_minimum(self):
        """Test that page_size must be at least 1."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page_size=0)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("page_size",)
        assert "1" in str(errors[0]["msg"]) and "greater" in str(errors[0]["msg"]).lower()
    
    def test_page_size_validation_maximum(self):
        """Test that page_size cannot exceed 100."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page_size=101)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("page_size",)
        assert "100" in str(errors[0]["msg"])
    
    def test_page_size_boundary_values(self):
        """Test page_size boundary values (1 and 100 should be valid)."""
        # Minimum boundary
        params_min = PaginationParams(page_size=1)
        assert params_min.page_size == 1
        
        # Maximum boundary
        params_max = PaginationParams(page_size=100)
        assert params_max.page_size == 100
    
    def test_order_validation_asc(self):
        """Test that 'asc' is a valid order value."""
        params = PaginationParams(order="asc")
        assert params.order == "asc"
    
    def test_order_validation_desc(self):
        """Test that 'desc' is a valid order value."""
        params = PaginationParams(order="desc")
        assert params.order == "desc"
    
    def test_order_validation_invalid(self):
        """Test that invalid order values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(order="invalid")  # type: ignore
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("order",)
    
    def test_sort_field_optional(self):
        """Test that sort field is optional."""
        params = PaginationParams()
        assert params.sort is None
        
        params_with_sort = PaginationParams(sort="created_at")
        assert params_with_sort.sort == "created_at"
    
    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are caught together."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page=0, page_size=200)
        
        errors = exc_info.value.errors()
        assert len(errors) == 2
        
        error_locs = [error["loc"] for error in errors]
        assert ("page",) in error_locs
        assert ("page_size",) in error_locs
    
    def test_model_serialization(self):
        """Test that the model can be serialized to dict."""
        params = PaginationParams(
            page=2,
            page_size=30,
            sort="email",
            order="asc"
        )
        
        result = params.model_dump()
        
        assert result["page"] == 2
        assert result["page_size"] == 30
        assert result["sort"] == "email"
        assert result["order"] == "asc"
    
    def test_model_json_serialization(self):
        """Test that the model can be serialized to JSON."""
        params = PaginationParams(page=5, page_size=15, sort="name")
        
        json_str = params.model_dump_json()
        
        assert '"page":5' in json_str or '"page": 5' in json_str
        assert '"page_size":15' in json_str or '"page_size": 15' in json_str
        assert '"sort":"name"' in json_str or '"sort": "name"' in json_str


class TestGetPaginationParams:
    """Test suite for get_pagination_params dependency function."""
    
    def test_creates_pagination_params_instance(self):
        """Test that the dependency function signature is correct."""
        # We can't actually call the dependency outside of FastAPI context,
        # but we can verify it exists and has the right signature
        import inspect
        from fastapi import Query
        
        sig = inspect.signature(get_pagination_params)
        params = sig.parameters
        
        assert "page" in params
        assert "page_size" in params
        assert "sort" in params
        assert "order" in params
        
        # Check that defaults are Query objects with correct values
        assert isinstance(params["page"].default, type(Query(1)))
        assert isinstance(params["page_size"].default, type(Query(20)))
        assert params["sort"].default is None or isinstance(params["sort"].default, type(Query(None)))
        assert isinstance(params["order"].default, type(Query("desc")))
    
    def test_dependency_returns_correct_type(self):
        """Test that return annotation is PaginationParams."""
        import inspect
        
        sig = inspect.signature(get_pagination_params)
        return_annotation = sig.return_annotation
        
        assert return_annotation == PaginationParams


class TestPaginationEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_large_page_number(self):
        """Test pagination with very large page numbers."""
        params = PaginationParams(page=999999, page_size=100)
        
        assert params.page == 999999
        # (999999 - 1) * 100 = 99999800
        assert params.offset == 99999800
        assert params.limit == 100
    
    def test_minimum_valid_configuration(self):
        """Test minimum valid pagination configuration."""
        params = PaginationParams(page=1, page_size=1)
        
        assert params.page == 1
        assert params.page_size == 1
        assert params.offset == 0
        assert params.limit == 1
    
    def test_maximum_valid_configuration(self):
        """Test maximum valid pagination configuration."""
        params = PaginationParams(page=1000000, page_size=100)
        
        assert params.page == 1000000
        assert params.page_size == 100
        assert params.offset == 99999900
        assert params.limit == 100
    
    def test_sort_with_special_characters(self):
        """Test sort field with various characters."""
        # Underscores
        params1 = PaginationParams(sort="created_at")
        assert params1.sort == "created_at"
        
        # Mixed case
        params2 = PaginationParams(sort="firstName")
        assert params2.sort == "firstName"
        
        # Dots (for nested fields)
        params3 = PaginationParams(sort="user.name")
        assert params3.sort == "user.name"
    
    def test_typical_use_cases(self):
        """Test typical real-world pagination scenarios."""
        # First page of search results
        params1 = PaginationParams(page=1, page_size=20, sort="relevance", order="desc")
        assert params1.offset == 0
        assert params1.limit == 20
        
        # Middle page of sorted list
        params2 = PaginationParams(page=5, page_size=50, sort="name", order="asc")
        assert params2.offset == 200
        assert params2.limit == 50
        
        # Last page with small page size
        params3 = PaginationParams(page=100, page_size=10, sort="created_at", order="desc")
        assert params3.offset == 990
        assert params3.limit == 10


class TestPaginationValidationMessages:
    """Test that validation error messages are clear and helpful."""
    
    def test_page_zero_error_message(self):
        """Test error message when page is 0."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page=0)
        
        errors = exc_info.value.errors()
        error_msg = str(errors[0]["msg"]).lower()
        
        # Should mention the constraint
        assert "1" in error_msg or "greater" in error_msg
    
    def test_page_size_too_large_error_message(self):
        """Test error message when page_size exceeds maximum."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page_size=150)
        
        errors = exc_info.value.errors()
        error_msg = str(errors[0]["msg"])
        
        # Should mention the maximum value
        assert "100" in error_msg
    
    def test_page_size_zero_error_message(self):
        """Test error message when page_size is 0."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page_size=0)
        
        errors = exc_info.value.errors()
        error_msg = str(errors[0]["msg"]).lower()
        
        # Should mention minimum requirement
        assert "1" in error_msg or "least" in error_msg


class TestPaginationIntegration:
    """Integration tests simulating real API usage."""
    
    def test_pagination_workflow(self):
        """Test complete pagination workflow through multiple pages."""
        total_items = 95
        page_size = 20
        
        pages = []
        for page_num in range(1, 6):  # Pages 1-5
            params = PaginationParams(page=page_num, page_size=page_size)
            pages.append({
                "page": params.page,
                "offset": params.offset,
                "limit": params.limit
            })
        
        # Verify page 1
        assert pages[0]["offset"] == 0
        assert pages[0]["limit"] == 20
        
        # Verify page 2
        assert pages[1]["offset"] == 20
        assert pages[1]["limit"] == 20
        
        # Verify page 3
        assert pages[2]["offset"] == 40
        
        # Verify page 5 (last page with partial results)
        assert pages[4]["offset"] == 80
        assert pages[4]["limit"] == 20  # Still 20, but would return only 15 items
    
    def test_pagination_with_sorting_scenarios(self):
        """Test pagination combined with different sorting scenarios."""
        # Newest first
        params1 = PaginationParams(sort="created_at", order="desc")
        assert params1.sort == "created_at"
        assert params1.order == "desc"
        
        # Alphabetical order
        params2 = PaginationParams(sort="name", order="asc")
        assert params2.sort == "name"
        assert params2.order == "asc"
        
        # No sorting (database default)
        params3 = PaginationParams()
        assert params3.sort is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
