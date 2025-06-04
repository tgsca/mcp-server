"""
Tests for the AnalystProcessor.
"""

from app.processors.analyst_processor import AnalystProcessor


class TestAnalystProcessor:
    """Test cases for AnalystProcessor."""

    def test_process_analyst_estimates_success(self, mock_analyst_estimates_response):
        """Test successful processing of analyst estimates."""
        result = AnalystProcessor.process_analyst_estimates(mock_analyst_estimates_response)
        
        assert "jährlich" in result
        assert "quartal" in result
        assert "wachstumsraten" in result
        
        # Test annual data processing
        annual_data = result["jährlich"]
        assert "2024" in annual_data
        assert annual_data["2024"]["umsatz"] == 385000000000
        assert annual_data["2024"]["nettogewinn"] == 95000000000
        assert annual_data["2024"]["eps"] == 6.15
        assert annual_data["2024"]["dividende"] == 0.95
        assert annual_data["2024"]["roe"] == 28.5
        assert annual_data["2024"]["bruttomarge"] == 42.5
        
        # Test quarterly data processing (should limit to 4 quarters)
        quarterly_data = result["quartal"]
        assert len(quarterly_data) == 4  # Should limit to 4 quarters
        assert "2024-Q1" in quarterly_data
        assert quarterly_data["2024-Q1"]["umsatz"] == 95000000000
        assert quarterly_data["2024-Q1"]["eps"] == 1.48
        
        # Test growth rates processing
        growth_data = result["wachstumsraten"]
        assert "revenue" in growth_data
        assert growth_data["revenue"] == 8.5
        assert "eps" in growth_data
        assert growth_data["eps"] == 12.2

    def test_process_analyst_estimates_empty_data(self):
        """Test handling of empty data."""
        result = AnalystProcessor.process_analyst_estimates({})
        
        assert "error" in result
        assert "Keine gültigen Daten verfügbar" in result["error"]

    def test_process_analyst_estimates_none_data(self):
        """Test handling of None data."""
        result = AnalystProcessor.process_analyst_estimates(None)
        
        assert "error" in result
        assert "Keine gültigen Daten verfügbar" in result["error"]

    def test_process_analyst_estimates_invalid_data_type(self):
        """Test handling of invalid data type."""
        result = AnalystProcessor.process_analyst_estimates("invalid")
        
        assert "error" in result
        assert "Keine gültigen Daten verfügbar" in result["error"]

    def test_process_analyst_estimates_missing_estimates(self):
        """Test handling of data without estimates section."""
        data = {"other_data": "value"}
        result = AnalystProcessor.process_analyst_estimates(data)
        
        # Should create empty structure
        assert "jährlich" in result
        assert "quartal" in result
        assert "wachstumsraten" in result

    def test_process_analyst_estimates_partial_data(self):
        """Test handling of partial estimates data."""
        data = {
            "annual": {
                "date": ["2024"],
                "revenue_estimate": [385000000000]
                # Missing other fields
            }
        }
        result = AnalystProcessor.process_analyst_estimates(data)
        
        assert "jährlich" in result
        assert "quartal" in result
        assert "wachstumsraten" in result
        assert "2024" in result["jährlich"]
        assert result["jährlich"]["2024"]["umsatz"] == 385000000000
        assert result["jährlich"]["2024"]["nettogewinn"] is None  # Missing field

    def test_process_analyst_estimates_with_annual_only(self):
        """Test processing with only annual data."""
        data = {
            "annual": {
                "date": ["2024", "2025"],
                "revenue_estimate": [100000000000, 110000000000],
                "per_share_eps_estimate": [5.0, 5.5]
            }
        }
        result = AnalystProcessor.process_analyst_estimates(data)
        
        assert len(result["jährlich"]) == 2
        assert "2024" in result["jährlich"]
        assert result["jährlich"]["2024"]["umsatz"] == 100000000000
        assert result["jährlich"]["2024"]["eps"] == 5.0
        assert len(result["quartal"]) == 0

    def test_process_analyst_estimates_with_quarterly_only(self):
        """Test processing with only quarterly data."""
        data = {
            "quarterly": {
                "date": ["Q1", "Q2", "Q3"],
                "revenue_estimate": [25000000000, 26000000000, 24000000000],
                "per_share_eps_estimate": [1.2, 1.3, 1.1]
            }
        }
        result = AnalystProcessor.process_analyst_estimates(data)
        
        assert len(result["jährlich"]) == 0
        assert len(result["quartal"]) == 3
        assert "Q1" in result["quartal"]
        assert result["quartal"]["Q1"]["umsatz"] == 25000000000

    def test_process_analyst_estimates_quarterly_limit(self):
        """Test that quarterly data is limited to 4 quarters."""
        data = {
            "quarterly": {
                "date": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
                "revenue_estimate": [25, 26, 24, 27, 28, 29],
                "per_share_eps_estimate": [1.2, 1.3, 1.1, 1.4, 1.5, 1.6]
            }
        }
        result = AnalystProcessor.process_analyst_estimates(data)
        
        assert len(result["quartal"]) == 4  # Should be limited to 4
        assert "Q1" in result["quartal"]
        assert "Q4" in result["quartal"]
        assert "Q5" not in result["quartal"]

    def test_get_value_at_index_success(self):
        """Test successful value extraction at index."""
        data = {"test_key": [10.5, 20.7, 30.9]}
        
        assert AnalystProcessor.get_value_at_index(data, "test_key", 0) == 10.5
        assert AnalystProcessor.get_value_at_index(data, "test_key", 1) == 20.7
        assert AnalystProcessor.get_value_at_index(data, "test_key", 2) == 30.9

    def test_get_value_at_index_out_of_bounds(self):
        """Test value extraction with out of bounds index."""
        data = {"test_key": [10.5, 20.7]}
        
        assert AnalystProcessor.get_value_at_index(data, "test_key", 5) is None

    def test_get_value_at_index_missing_key(self):
        """Test value extraction with missing key."""
        data = {"other_key": [10.5, 20.7]}
        
        assert AnalystProcessor.get_value_at_index(data, "test_key", 0) is None

    def test_get_value_at_index_string_conversion(self):
        """Test value extraction with string numbers."""
        data = {"test_key": ["10.5", "20.7", "invalid"]}
        
        assert AnalystProcessor.get_value_at_index(data, "test_key", 0) == 10.5
        assert AnalystProcessor.get_value_at_index(data, "test_key", 1) == 20.7
        assert AnalystProcessor.get_value_at_index(data, "test_key", 2) == "invalid"  # Returns original for invalid conversion

    def test_get_value_at_index_type_error(self):
        """Test value extraction with non-convertible values."""
        data = {"test_key": [None, {"nested": "dict"}]}
        
        assert AnalystProcessor.get_value_at_index(data, "test_key", 0) is None
        assert AnalystProcessor.get_value_at_index(data, "test_key", 1) == {"nested": "dict"}