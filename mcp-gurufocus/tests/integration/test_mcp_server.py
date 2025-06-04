"""
MCP Server Integration Tests.

Tests the MCP server components working together in integration scenarios.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from app.main import (
    get_concise_stock_summary,
    get_concise_stock_financials,
    get_concise_analyst_estimates,
    get_concise_segments_data,
    get_concise_news_headlines,
)


class TestMCPServerIntegration:
    """Integration tests for MCP tool functionality without full protocol overhead."""

    @pytest.mark.asyncio
    async def test_mcp_tool_integration_full_stack(self):
        """Test MCP tools work with full stack integration (API client + processors)."""
        with patch(
            "app.api.client.GuruFocusClient.get_stock_summary", new_callable=AsyncMock
        ) as mock_api:
            # Mock realistic API response
            mock_api.return_value = {
                "summary": {
                    "general": {
                        "company": "Apple Inc",
                        "price": 150.25,
                        "currency": "$",
                        "sector": "Technology",
                    },
                    "ratio": {"P/E(ttm)": {"value": 25.5}},
                }
            }

            # Test that the tool works end-to-end
            result = await get_concise_stock_summary("AAPL")

            # Verify integration worked
            assert result is not None
            assert "allgemein" in result
            assert result["allgemein"]["firma"] == "Apple Inc"
            assert result["allgemein"]["preis"] == 150.25

            # Verify API was called
            mock_api.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    async def test_stock_financials_integration(self):
        """Test stock financials tool integration."""
        with patch(
            "app.api.client.GuruFocusClient.get_stock_financials",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.return_value = {
                "financials": {
                    "financial_template_parameters": {"REITs": "N"},
                    "annuals": {
                        "Fiscal Year": ["2023", "2022"],
                        "Revenue": [394328000000, 365817000000],
                    },
                }
            }

            result = await get_concise_stock_financials("AAPL", "EUR")

            assert result is not None
            assert "is_reit" in result
            assert result["is_reit"] is False
            assert "jahresabschlüsse" in result

            mock_api.assert_called_once_with("AAPL", "EUR")

    @pytest.mark.asyncio
    async def test_analyst_estimates_integration(self):
        """Test analyst estimates tool integration."""
        with patch(
            "app.api.client.GuruFocusClient.get_analyst_estimates",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.return_value = {
                "annual": {
                    "date": ["2024", "2025"],
                    "revenue_estimate": [400000000000, 420000000000],
                    "per_share_eps_estimate": [6.0, 6.5],
                }
            }

            result = await get_concise_analyst_estimates("AAPL")

            assert result is not None
            assert "jährlich" in result
            assert "quartal" in result
            assert "wachstumsraten" in result

            mock_api.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    async def test_segments_data_integration(self):
        """Test segments data tool integration."""
        with patch(
            "app.api.client.GuruFocusClient.get_segments_data", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = {
                "business": {
                    "annual": [
                        {
                            "date": "2023",
                            "iPhone": 200000000000,
                            "Services": 85000000000,
                        }
                    ]
                }
            }

            result = await get_concise_segments_data("AAPL", "202301")

            assert result is not None
            assert "geschäftsbereiche" in result
            assert "regionen" in result

            mock_api.assert_called_once_with("AAPL", "202301")

    @pytest.mark.asyncio
    async def test_news_headlines_integration(self):
        """Test news headlines tool integration."""
        with patch(
            "app.api.client.GuruFocusClient.get_news_headlines", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = {
                "news": [
                    {
                        "date": "2024-01-15",
                        "headline": "Apple Reports Strong Q4 Results",
                        "url": "https://example.com/news1",
                    }
                ]
            }

            result = await get_concise_news_headlines("AAPL")

            assert result is not None
            assert isinstance(result, list)
            assert len(result) > 0
            assert "datum" in result[0]
            assert "überschrift" in result[0]

            mock_api.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across the full stack."""
        with patch(
            "app.api.client.GuruFocusClient.get_stock_summary", new_callable=AsyncMock
        ) as mock_api:
            # Mock API failure
            mock_api.return_value = None

            result = await get_concise_stock_summary("INVALID_SYMBOL")

            # Should handle gracefully, not crash
            assert result is not None
            assert "error" in result

            mock_api.assert_called_once_with("INVALID_SYMBOL")

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test multiple tools can run concurrently."""
        with (
            patch(
                "app.api.client.GuruFocusClient.get_stock_summary",
                new_callable=AsyncMock,
            ) as mock_summary,
            patch(
                "app.api.client.GuruFocusClient.get_stock_financials",
                new_callable=AsyncMock,
            ) as mock_financials,
            patch(
                "app.api.client.GuruFocusClient.get_analyst_estimates",
                new_callable=AsyncMock,
            ) as mock_estimates,
        ):
            # Mock responses
            mock_summary.return_value = {
                "summary": {
                    "general": {"company": "Test Corp", "price": 100.0},
                    "ratio": {},
                }
            }
            mock_financials.return_value = {
                "financials": {
                    "financial_template_parameters": {"REITs": "N"},
                    "annuals": {},
                }
            }
            mock_estimates.return_value = {"annual": {}, "quarterly": {}}

            # Execute multiple tools concurrently
            tasks = [
                get_concise_stock_summary("AAPL"),
                get_concise_stock_financials("AAPL"),
                get_concise_analyst_estimates("AAPL"),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All should succeed
            for result in results:
                assert not isinstance(result, Exception), (
                    f"Concurrent execution failed: {result}"
                )
                assert result is not None

            # Verify all APIs were called (financials has default USD parameter)
            mock_summary.assert_called_once_with("AAPL")
            mock_financials.assert_called_once_with("AAPL", "USD")
            mock_estimates.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    async def test_default_parameters_integration(self):
        """Test tools with default parameters work in integration."""
        with patch(
            "app.api.client.GuruFocusClient.get_segments_data", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = {"business": {}, "geographic": {}}

            # Test default start_date parameter
            result = await get_concise_segments_data(
                "AAPL"
            )  # Should use default "201901"

            assert result is not None
            assert "geschäftsbereiche" in result
            assert "regionen" in result

            # Verify default parameter was used
            mock_api.assert_called_once_with("AAPL", "201901")

    @pytest.mark.asyncio
    async def test_data_flow_integration(self):
        """Test complete data flow from API through processors to output."""
        with patch(
            "app.api.client.GuruFocusClient.get_stock_summary", new_callable=AsyncMock
        ) as mock_api:
            # Mock complex realistic response
            mock_api.return_value = {
                "summary": {
                    "general": {
                        "company": "Apple Inc",
                        "price": 150.25,
                        "currency": "$",
                        "sector": "Technology",
                        "exchange": "NASDAQ",
                        "market_cap": 2500000000000,
                    },
                    "ratio": {
                        "P/E(ttm)": {"value": 25.5},
                        "P/B": {"value": 8.2},
                        "ROE": {"value": 0.87},
                    },
                    "company_data": {"rvn_growth_1y": 0.05, "earning_growth_1y": 0.08},
                }
            }

            result = await get_concise_stock_summary("AAPL")

            # Verify complete data transformation pipeline worked
            assert result is not None
            assert "allgemein" in result
            assert "kennzahlen" in result
            assert "wachstum" in result

            # Check specific transformations
            assert result["allgemein"]["firma"] == "Apple Inc"
            assert result["allgemein"]["preis"] == 150.25
            assert result["allgemein"]["sektor"] == "Technology"

            # Check ratios were processed
            assert "pe_ttm" in result["kennzahlen"]
            assert result["kennzahlen"]["pe_ttm"] == 25.5

            # Check growth data was processed
            assert "umsatz_wachstum_1y" in result["wachstum"]
            assert result["wachstum"]["umsatz_wachstum_1y"] == 0.05

            mock_api.assert_called_once_with("AAPL")
