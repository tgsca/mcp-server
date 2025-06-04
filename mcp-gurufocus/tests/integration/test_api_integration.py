"""
Integration tests for API client and processors working together.
"""

import pytest
from unittest.mock import patch
from app.api.client import GuruFocusClient
from app.processors.stock_processor import StockProcessor
from app.processors.financials_processor import FinancialsProcessor


class TestAPIIntegration:
    """Integration tests for API and processors."""

    @pytest.mark.asyncio
    async def test_stock_summary_integration(self, mock_stock_summary_response):
        """Test complete flow from API call to processed data."""
        with patch.object(GuruFocusClient, "get_stock_summary") as mock_api:
            mock_api.return_value = mock_stock_summary_response

            # Simulate the flow: API -> Processor
            raw_data = await GuruFocusClient.get_stock_summary("AAPL")
            processed_data = StockProcessor.process_stock_summary(raw_data)

            # Verify API was called
            mock_api.assert_called_once_with("AAPL")

            # Verify data was processed correctly
            assert "allgemein" in processed_data
            assert processed_data["allgemein"]["firma"] == "Apple Inc"
            assert processed_data["allgemein"]["preis"] == 150.25

    @pytest.mark.asyncio
    async def test_financials_integration(self, mock_financials_response):
        """Test complete flow for financials data."""
        full_mock_response = {
            "financials": {
                "financial_template_parameters": {"REITs": "N"},
                "annuals": mock_financials_response,
            }
        }

        with patch.object(GuruFocusClient, "get_stock_financials") as mock_api:
            mock_api.return_value = full_mock_response

            # Simulate the flow: API -> Processor
            raw_data = await GuruFocusClient.get_stock_financials("AAPL")
            processed_data = FinancialsProcessor.process_stock_financials(raw_data)

            # Verify API was called
            mock_api.assert_called_once_with("AAPL")

            # Verify data was processed correctly
            assert "is_reit" in processed_data
            assert processed_data["is_reit"] is False
            assert "jahresabschlüsse" in processed_data

    @pytest.mark.asyncio
    async def test_api_error_handling_integration(self):
        """Test integration with API errors."""
        with patch.object(GuruFocusClient, "get_stock_summary") as mock_api:
            mock_api.return_value = None  # Simulate API failure

            # Simulate the flow: API -> Processor
            raw_data = await GuruFocusClient.get_stock_summary("INVALID")
            processed_data = StockProcessor.process_stock_summary(raw_data)

            # Verify error handling
            assert "error" in processed_data
            assert "Keine gültigen Daten verfügbar" in processed_data["error"]
