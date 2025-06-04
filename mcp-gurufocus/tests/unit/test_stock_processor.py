"""
Tests for the StockProcessor.
"""

from app.processors.stock_processor import StockProcessor


class TestStockProcessor:
    """Test cases for StockProcessor."""

    def test_process_stock_summary_success(self, mock_stock_summary_response):
        """Test successful processing of stock summary data."""
        result = StockProcessor.process_stock_summary(mock_stock_summary_response)
        
        # Test general information
        assert result["allgemein"]["firma"] == "Apple Inc"
        assert result["allgemein"]["preis"] == 150.25
        assert result["allgemein"]["währung"] == "$"
        assert result["allgemein"]["gf_score"] == "85"
        assert result["allgemein"]["bewertung"] == "Fairly Valued"
        assert result["allgemein"]["sektor"] == "Technology"
        assert result["allgemein"]["branche"] == "Hardware"
        assert result["allgemein"]["unterbranche"] == "Consumer Electronics"
        assert result["allgemein"]["land"] == "USA"
        assert result["allgemein"]["risikobewertung"] == "Medium"
        
        # Test ratios
        assert result["kennzahlen"]["pe_ttm"] == 25.5
        assert result["kennzahlen"]["forward_pe"] == 22.1
        assert result["kennzahlen"]["ps"] == 7.2
        assert result["kennzahlen"]["pb"] == 8.9
        assert result["kennzahlen"]["ebitda_marge"] == 30.1

    def test_process_stock_summary_empty_data(self):
        """Test handling of empty data."""
        result = StockProcessor.process_stock_summary({})
        
        assert "error" in result
        assert result["error"] == "Keine gültigen Daten verfügbar"

    def test_process_stock_summary_none_data(self):
        """Test handling of None data."""
        result = StockProcessor.process_stock_summary(None)
        
        assert "error" in result
        assert result["error"] == "Keine gültigen Daten verfügbar"

    def test_process_stock_summary_invalid_data_type(self):
        """Test handling of invalid data type."""
        result = StockProcessor.process_stock_summary("invalid")
        
        assert "error" in result
        assert result["error"] == "Keine gültigen Daten verfügbar"

    def test_process_stock_summary_missing_summary(self):
        """Test handling of data without summary section."""
        data = {"other_data": "value"}
        result = StockProcessor.process_stock_summary(data)
        
        # Should still create structure with empty values
        assert "allgemein" in result
        assert result["allgemein"]["firma"] == ""
        assert result["allgemein"]["preis"] == 0
        assert result["allgemein"]["währung"] == "$"

    def test_process_stock_summary_partial_general_data(self):
        """Test handling of partial general data."""
        data = {
            "summary": {
                "general": {
                    "company": "Test Company",
                    "price": 100.0
                    # Missing other fields
                }
            }
        }
        result = StockProcessor.process_stock_summary(data)
        
        assert result["allgemein"]["firma"] == "Test Company"
        assert result["allgemein"]["preis"] == 100.0
        assert result["allgemein"]["währung"] == "$"  # Default value
        assert result["allgemein"]["gf_score"] == ""  # Missing field

    def test_process_stock_summary_with_growth_data(self):
        """Test processing with growth data."""
        data = {
            "summary": {
                "general": {"company": "Test Company"},
                "company_data": {
                    "rvn_growth_1y": 10.5,
                    "rvn_growth_3y": 15.2,
                    "earning_growth_1y": 20.1,
                    "FCFyield": 5.5
                }
            }
        }
        result = StockProcessor.process_stock_summary(data)
        
        assert result["wachstum"]["umsatz_wachstum_1y"] == 10.5
        assert result["wachstum"]["umsatz_wachstum_3y"] == 15.2
        assert result["wachstum"]["gewinn_wachstum_1y"] == 20.1
        assert result["kennzahlen"]["free_cashflow_yield"] == 5.5

    def test_process_stock_summary_with_valuation_data(self):
        """Test processing with valuation data."""
        data = {
            "summary": {
                "general": {"company": "Test Company"},
                "chart": {
                    "GF Value": 120.5,
                    "DCF (FCF Based)": 115.0,
                    "DCF (Earnings Based)": 118.2,
                    "Peter Lynch Value": 125.0
                }
            }
        }
        result = StockProcessor.process_stock_summary(data)
        
        assert result["bewertung"]["gf_value"] == 120.5
        assert result["bewertung"]["dcf_fcf"] == 115.0
        assert result["bewertung"]["dcf_earnings"] == 118.2
        assert result["bewertung"]["peter_lynch_value"] == 125.0

    def test_extract_ratio_value_success(self):
        """Test successful ratio value extraction."""
        ratio_data = {
            "P/E(ttm)": {"value": 25.5},
            "P/S": {"value": "7.2"}  # String value
        }
        
        assert StockProcessor.extract_ratio_value(ratio_data, "P/E(ttm)") == 25.5
        assert StockProcessor.extract_ratio_value(ratio_data, "P/S") == 7.2

    def test_extract_ratio_value_missing_key(self):
        """Test ratio value extraction with missing key."""
        ratio_data = {"P/E(ttm)": {"value": 25.5}}
        
        assert StockProcessor.extract_ratio_value(ratio_data, "P/S") == 0

    def test_extract_ratio_value_missing_value(self):
        """Test ratio value extraction with missing value field."""
        ratio_data = {"P/E(ttm)": {"other_field": 25.5}}
        
        assert StockProcessor.extract_ratio_value(ratio_data, "P/E(ttm)") == 0

    def test_extract_ratio_value_invalid_value(self):
        """Test ratio value extraction with invalid value."""
        ratio_data = {
            "P/E(ttm)": {"value": "invalid"},
            "P/S": {"value": None}
        }
        
        assert StockProcessor.extract_ratio_value(ratio_data, "P/E(ttm)") == 0
        assert StockProcessor.extract_ratio_value(ratio_data, "P/S") == 0

    def test_extract_ratio_value_empty_ratio_data(self):
        """Test ratio value extraction with empty ratio data."""
        assert StockProcessor.extract_ratio_value({}, "P/E(ttm)") == 0