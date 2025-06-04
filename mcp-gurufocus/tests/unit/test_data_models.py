"""
Tests for the Data Models (Pydantic).
"""

import pytest
from pydantic import ValidationError
from app.models.data_models import StockSummary, AnalystEstimate, SegmentData


class TestStockSummary:
    """Test cases for StockSummary model."""

    def test_stock_summary_valid_data(self):
        """Test StockSummary with valid data."""
        data = {
            "company": "Apple Inc",
            "price": 150.25,
            "currency": "$",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "USA",
        }

        stock = StockSummary(**data)

        assert stock.company == "Apple Inc"
        assert stock.price == 150.25
        assert stock.currency == "$"
        assert stock.sector == "Technology"
        assert stock.industry == "Consumer Electronics"
        assert stock.country == "USA"

    def test_stock_summary_default_currency(self):
        """Test StockSummary with default currency."""
        data = {
            "company": "Apple Inc",
            "price": 150.25,
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "USA",
        }

        stock = StockSummary(**data)

        assert stock.currency == "$"  # Default value

    def test_stock_summary_missing_required_field(self):
        """Test StockSummary with missing required field."""
        data = {
            "price": 150.25,
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "USA",
            # Missing required 'company' field
        }

        with pytest.raises(ValidationError) as exc_info:
            StockSummary(**data)

        assert "company" in str(exc_info.value)

    def test_stock_summary_invalid_price_type(self):
        """Test StockSummary with invalid price type."""
        data = {
            "company": "Apple Inc",
            "price": "invalid_price",  # Should be float
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "USA",
        }

        with pytest.raises(ValidationError) as exc_info:
            StockSummary(**data)

        assert "price" in str(exc_info.value)

    def test_stock_summary_negative_price(self):
        """Test StockSummary with negative price."""
        data = {
            "company": "Apple Inc",
            "price": -150.25,
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "USA",
        }

        # Should accept negative price (could be valid in some contexts)
        stock = StockSummary(**data)
        assert stock.price == -150.25


class TestAnalystEstimate:
    """Test cases for AnalystEstimate model."""

    def test_analyst_estimate_valid_data(self):
        """Test AnalystEstimate with valid data."""
        data = {
            "revenue": [100000000000, 110000000000, 120000000000],
            "eps": [5.0, 5.5, 6.0],
            "dates": ["2024", "2025", "2026"],
        }

        estimate = AnalystEstimate(**data)

        assert estimate.revenue == [100000000000, 110000000000, 120000000000]
        assert estimate.eps == [5.0, 5.5, 6.0]
        assert estimate.dates == ["2024", "2025", "2026"]

    def test_analyst_estimate_empty_lists(self):
        """Test AnalystEstimate with empty lists."""
        data = {"revenue": [], "eps": [], "dates": []}

        estimate = AnalystEstimate(**data)

        assert estimate.revenue == []
        assert estimate.eps == []
        assert estimate.dates == []

    def test_analyst_estimate_missing_required_field(self):
        """Test AnalystEstimate with missing required field."""
        data = {
            "eps": [5.0, 5.5, 6.0],
            "dates": ["2024", "2025", "2026"],
            # Missing required 'revenue' field
        }

        with pytest.raises(ValidationError) as exc_info:
            AnalystEstimate(**data)

        assert "revenue" in str(exc_info.value)

    def test_analyst_estimate_invalid_list_type(self):
        """Test AnalystEstimate with invalid list type."""
        data = {
            "revenue": "not_a_list",  # Should be list
            "eps": [5.0, 5.5, 6.0],
            "dates": ["2024", "2025", "2026"],
        }

        with pytest.raises(ValidationError) as exc_info:
            AnalystEstimate(**data)

        assert "revenue" in str(exc_info.value)

    def test_analyst_estimate_mixed_numeric_types(self):
        """Test AnalystEstimate with mixed numeric types."""
        data = {
            "revenue": [100000000000, 110000000000.5, 120],  # Mix of int and float
            "eps": [5, 5.5, 6.0],  # Mix of int and float
            "dates": ["2024", "2025", "2026"],
        }

        estimate = AnalystEstimate(**data)

        assert estimate.revenue[0] == 100000000000
        assert estimate.revenue[1] == 110000000000.5
        assert estimate.eps[0] == 5
        assert estimate.eps[1] == 5.5


class TestSegmentData:
    """Test cases for SegmentData model."""

    def test_segment_data_creation(self):
        """Test basic SegmentData model creation."""
        # Since SegmentData is incomplete in the source file,
        # we test that it can be imported without errors

        # This tests that the model class exists and can be imported
        assert SegmentData is not None
        assert hasattr(SegmentData, "__name__")
        assert SegmentData.__name__ == "SegmentData"


class TestModelValidation:
    """Test cases for general model validation."""

    def test_model_field_descriptions(self):
        """Test that models have proper field descriptions."""
        # Test StockSummary field descriptions
        stock_fields = StockSummary.model_fields
        assert "company" in stock_fields
        company_field = stock_fields["company"]
        assert hasattr(company_field, "description")
        assert "Der Name des Unternehmens" in company_field.description

        # Test AnalystEstimate field descriptions
        estimate_fields = AnalystEstimate.model_fields
        assert "revenue" in estimate_fields
        revenue_field = estimate_fields["revenue"]
        assert hasattr(revenue_field, "description")
        assert "Umsatzprognosen" in revenue_field.description

    def test_model_defaults(self):
        """Test model default values."""
        # Test StockSummary default currency
        stock_fields = StockSummary.model_fields
        currency_field = stock_fields["currency"]
        assert currency_field.default == "$"

    def test_model_serialization(self):
        """Test model serialization to dict."""
        stock_data = {
            "company": "Apple Inc",
            "price": 150.25,
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "USA",
        }

        stock = StockSummary(**stock_data)
        serialized = stock.model_dump()

        assert serialized["company"] == "Apple Inc"
        assert serialized["price"] == 150.25
        assert serialized["currency"] == "$"
        assert serialized["sector"] == "Technology"

    def test_model_json_serialization(self):
        """Test model JSON serialization."""
        stock_data = {
            "company": "Apple Inc",
            "price": 150.25,
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "USA",
        }

        stock = StockSummary(**stock_data)
        json_str = stock.model_dump_json()

        assert isinstance(json_str, str)
        assert "Apple Inc" in json_str
        assert "150.25" in json_str
        assert "Technology" in json_str

    def test_model_from_json(self):
        """Test model creation from JSON."""
        json_data = '{"company": "Apple Inc", "price": 150.25, "sector": "Technology", "industry": "Consumer Electronics", "country": "USA"}'

        stock = StockSummary.model_validate_json(json_data)

        assert stock.company == "Apple Inc"
        assert stock.price == 150.25
        assert stock.sector == "Technology"
