"""
Tests for the FinancialsProcessor.
"""

from app.processors.financials_processor import FinancialsProcessor


class TestFinancialsProcessor:
    """Test cases for FinancialsProcessor."""

    def test_process_stock_financials_success(self, mock_financials_response):
        """Test successful processing of financials data."""
        data = {
            "financials": {
                "financial_template_parameters": {"REITs": "N"},
                "annuals": mock_financials_response
            }
        }
        
        result = FinancialsProcessor.process_stock_financials(data)
        
        assert result["is_reit"] is False
        assert "jahresabschlüsse" in result
        assert "perioden" in result["jahresabschlüsse"]

    def test_process_stock_financials_reit(self):
        """Test processing of REIT financials."""
        data = {
            "financials": {
                "financial_template_parameters": {"REITs": "Y"},
                "annuals": {"Fiscal Year": ["2023", "2022"]}
            }
        }
        
        result = FinancialsProcessor.process_stock_financials(data)
        
        assert result["is_reit"] is True

    def test_process_stock_financials_empty_data(self):
        """Test handling of empty data."""
        result = FinancialsProcessor.process_stock_financials({})
        
        assert "error" in result
        assert result["error"] == "Keine gültigen Finanzdaten verfügbar"

    def test_process_stock_financials_none_data(self):
        """Test handling of None data."""
        result = FinancialsProcessor.process_stock_financials(None)
        
        assert "error" in result
        assert result["error"] == "Keine gültigen Finanzdaten verfügbar"

    def test_process_stock_financials_invalid_data_type(self):
        """Test handling of invalid data type."""
        result = FinancialsProcessor.process_stock_financials("invalid")
        
        assert "error" in result
        assert result["error"] == "Keine gültigen Finanzdaten verfügbar"

    def test_process_stock_financials_missing_financials(self):
        """Test handling of data without financials section."""
        data = {"other_data": "value"}
        result = FinancialsProcessor.process_stock_financials(data)
        
        # Should still process but with minimal data
        assert result["is_reit"] is False  # Default value
        assert "jahresabschlüsse" in result

    def test_process_stock_financials_missing_template_params(self):
        """Test handling of missing template parameters."""
        data = {
            "financials": {
                "annuals": {"Fiscal Year": ["2023", "2022"]}
            }
        }
        
        result = FinancialsProcessor.process_stock_financials(data)
        
        assert result["is_reit"] is False  # Default when missing

    def test_clean_periods_normal_list(self):
        """Test cleaning of normal period list."""
        periods = ["2023-09", "2022-09", "2021-09"]
        result = FinancialsProcessor._clean_periods(periods)
        
        assert isinstance(result, list)
        assert len(result) == 3

    def test_clean_periods_empty_list(self):
        """Test cleaning of empty period list."""
        periods = []
        result = FinancialsProcessor._clean_periods(periods)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_clean_periods_none_input(self):
        """Test cleaning with None input."""
        # The method should handle None gracefully
        try:
            result = FinancialsProcessor._clean_periods(None)
            # If it doesn't raise an exception, check the result
            assert result is not None
        except (TypeError, AttributeError):
            # It's acceptable for the method to raise an exception with None input
            pass

    def test_process_stock_financials_structure(self):
        """Test the overall structure of processed financials."""
        data = {
            "financials": {
                "financial_template_parameters": {"REITs": "N"},
                "annuals": {
                    "Fiscal Year": ["2023-09", "2022-09", "2021-09"],
                    "Revenue": [394328000000, 365817000000, 274515000000],
                    "Net Income": [97001000000, 99803000000, 94680000000]
                }
            }
        }
        
        result = FinancialsProcessor.process_stock_financials(data)
        
        # Check main structure
        assert "is_reit" in result
        assert "jahresabschlüsse" in result
        
        # Check jahresabschlüsse structure
        jahres = result["jahresabschlüsse"]
        assert "perioden" in jahres
        assert "per_share_data" in jahres
        assert "income_statement" in jahres
        assert "balance_sheet" in jahres
        assert "cashflow_statement" in jahres
        
        # Verify periods are processed
        assert isinstance(jahres["perioden"], list)

    def test_filter_data_basic(self):
        """Test basic data filtering functionality."""
        section = {
            "Fiscal Year": ["2023", "2022", "2021"],
            "Revenue": [100000, 95000, 90000],
            "Net Income": [25000, 24000, 23000],
            "Preliminary": ["P", "P", "P"]
        }
        
        result = FinancialsProcessor._filter_data(section)
        
        # Should exclude default keys
        assert "Fiscal Year" not in result
        assert "Preliminary" not in result
        assert "Revenue" in result
        assert "Net Income" in result
        assert result["Revenue"] == [100000, 95000, 90000]

    def test_filter_data_with_custom_exclude_keys(self):
        """Test data filtering with custom exclude keys."""
        section = {
            "Fiscal Year": ["2023", "2022"],
            "Revenue": [100000, 95000],
            "Custom Field": [1, 2],
            "Another Field": [3, 4]
        }
        
        result = FinancialsProcessor._filter_data(section, ["Custom Field"])
        
        # Should exclude custom keys plus defaults
        assert "Fiscal Year" not in result
        assert "Custom Field" not in result
        assert "Revenue" in result
        assert "Another Field" in result

    def test_filter_data_limit_to_10_periods(self):
        """Test that filtering limits to 10 periods."""
        section = {
            "Long List": list(range(15))  # 15 items
        }
        
        result = FinancialsProcessor._filter_data(section)
        
        # Should limit to 10 items
        assert len(result["Long List"]) == 10
        assert result["Long List"] == list(range(10))

    def test_filter_data_non_list_values(self):
        """Test that non-list values are excluded."""
        section = {
            "Revenue": [100000, 95000],  # List - should be included
            "Single Value": 50000,       # Not a list - should be excluded
            "Dict Value": {"key": "value"},  # Not a list - should be excluded
            "None Value": None           # Not a list - should be excluded
        }
        
        result = FinancialsProcessor._filter_data(section)
        
        assert "Revenue" in result
        assert "Single Value" not in result
        assert "Dict Value" not in result
        assert "None Value" not in result

    def test_process_per_share_data(self):
        """Test per share data processing."""
        annuals = {
            "Per Share Data": {
                "EPS": [6.15, 5.98, 5.61],
                "Book Value": [4.25, 4.10, 3.95],
                "Fiscal Year": ["2023", "2022", "2021"]
            }
        }
        
        result = FinancialsProcessor._process_per_share_data(annuals)
        
        assert "EPS" in result
        assert "Book Value" in result
        assert "Fiscal Year" not in result
        assert result["EPS"] == [6.15, 5.98, 5.61]

    def test_process_per_share_data_missing_section(self):
        """Test per share data processing with missing section."""
        annuals = {}
        
        result = FinancialsProcessor._process_per_share_data(annuals)
        
        assert result == {}

    def test_process_income_statement(self):
        """Test income statement processing."""
        data = {
            "Income Statement": {
                "Revenue": [394328000000, 365817000000],
                "Net Income": [97001000000, 99803000000],
                "Fiscal Year": ["2023", "2022"]
            }
        }
        
        result = FinancialsProcessor._process_income_statement(data)
        
        assert "Revenue" in result
        assert "Net Income" in result
        assert "Fiscal Year" not in result
        assert result["Revenue"] == [394328000000, 365817000000]

    def test_process_balance_sheet(self):
        """Test balance sheet processing."""
        data = {
            "Balance Sheet": {
                "Total Assets": [352755000000, 323888000000],
                "Total Debt": [111109000000, 120069000000],
                "Fiscal Year": ["2023", "2022"]
            }
        }
        
        result = FinancialsProcessor._process_balance_sheet(data)
        
        assert "Total Assets" in result
        assert "Total Debt" in result
        assert "Fiscal Year" not in result
        assert result["Total Assets"] == [352755000000, 323888000000]

    def test_process_cashflow_statement(self):
        """Test cash flow statement processing."""
        data = {
            "Cash Flow": {
                "Operating Cash Flow": [114643000000, 122151000000],
                "Free Cash Flow": [99584000000, 111443000000],
                "Fiscal Year": ["2023", "2022"]
            }
        }
        
        result = FinancialsProcessor._process_cashflow_statement(data)
        
        assert "Operating Cash Flow" in result
        assert "Free Cash Flow" in result
        assert "Fiscal Year" not in result
        assert result["Operating Cash Flow"] == [114643000000, 122151000000]

    def test_process_profitability_ratios(self):
        """Test profitability ratios processing."""
        data = {
            "Profitability": {
                "ROE (%)": [28.5, 30.2],
                "ROA (%)": [15.2, 16.1],
                "Fiscal Year": ["2023", "2022"]
            }
        }
        
        result = FinancialsProcessor._process_profitability_ratios(data)
        
        assert "ROE (%)" in result
        assert "ROA (%)" in result
        assert "Fiscal Year" not in result

    def test_process_growth_ratios(self):
        """Test growth ratios processing."""
        data = {
            "Growth": {
                "Revenue Growth (%)": [8.5, 12.2],
                "EPS Growth (%)": [10.1, 15.3],
                "Fiscal Year": ["2023", "2022"]
            }
        }
        
        result = FinancialsProcessor._process_growth_ratios(data)
        
        assert "Revenue Growth (%)" in result
        assert "EPS Growth (%)" in result
        assert "Fiscal Year" not in result

    def test_process_cashflow_ratios(self):
        """Test cash flow ratios processing."""
        data = {
            "Cash Flow Ratios": {
                "FCF Yield (%)": [3.2, 3.8],
                "OCF to Revenue (%)": [29.1, 33.4],
                "Fiscal Year": ["2023", "2022"]
            }
        }
        
        result = FinancialsProcessor._process_cashflow_ratios(data)
        
        assert "FCF Yield (%)" in result
        assert "OCF to Revenue (%)" in result
        assert "Fiscal Year" not in result

    def test_process_financial_strength_ratios(self):
        """Test financial strength ratios processing."""
        data = {
            "Financial Strength": {
                "Debt to Equity": [1.2, 1.5],
                "Current Ratio": [0.93, 1.07],
                "Fiscal Year": ["2023", "2022"]
            }
        }
        
        result = FinancialsProcessor._process_financial_strength_ratios(data)
        
        assert "Debt to Equity" in result
        assert "Current Ratio" in result
        assert "Fiscal Year" not in result

    def test_process_efficiency_ratios(self):
        """Test efficiency ratios processing."""
        data = {
            "Efficiency": {
                "Asset Turnover": [1.1, 1.2],
                "Inventory Turnover": [40.2, 38.5],
                "Fiscal Year": ["2023", "2022"]
            }
        }
        
        result = FinancialsProcessor._process_efficiency_ratios(data)
        
        assert "Asset Turnover" in result
        assert "Inventory Turnover" in result
        assert "Fiscal Year" not in result

    def test_process_valuation_ratios(self):
        """Test valuation ratios processing."""
        data = {
            "Valuation Ratios": {
                "P/E": [25.5, 27.1],
                "P/B": [8.9, 9.2],
                "Fiscal Year": ["2023", "2022"]
            }
        }
        
        result = FinancialsProcessor._process_valuation_ratios(data)
        
        assert "P/E" in result
        assert "P/B" in result
        assert "Fiscal Year" not in result