"""
Unit tests for MCP tool functions.

Tests the individual MCP tool functions with mocked dependencies.
"""

import pytest
from unittest.mock import patch, AsyncMock
import asyncio


class TestMCPToolFunctions:
    """Unit tests for MCP tool functions."""

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_stock_summary")
    @patch("app.processors.stock_processor.StockProcessor.process_stock_summary")
    async def test_get_concise_stock_summary_tool(self, mock_processor, mock_client):
        """Test stock summary tool logic."""
        # Import here to avoid issues with module loading
        from app.main import get_concise_stock_summary

        # Setup mocks
        mock_client.return_value = {
            "summary": {
                "general": {"company": "Apple Inc", "price": 150.25},
                "ratio": {"P/E(ttm)": {"value": 25.5}},
            }
        }
        mock_processor.return_value = {
            "allgemein": {"firma": "Apple Inc", "preis": 150.25},
            "kennzahlen": {"pe_ttm": 25.5},
        }

        # Call the tool function
        result = await get_concise_stock_summary("AAPL")

        # Verify behavior
        mock_client.assert_called_once_with("AAPL")
        mock_processor.assert_called_once()
        assert result["allgemein"]["firma"] == "Apple Inc"
        assert result["allgemein"]["preis"] == 150.25

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_stock_summary")
    async def test_get_concise_stock_summary_api_failure(self, mock_client):
        """Test stock summary tool with API failure."""
        from app.main import get_concise_stock_summary

        # Mock API failure
        mock_client.return_value = None

        result = await get_concise_stock_summary("INVALID")

        # Should handle gracefully
        assert "error" in result
        assert "Konnte keine Daten für INVALID abrufen" in result["error"]

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_stock_financials")
    @patch(
        "app.processors.financials_processor.FinancialsProcessor.process_stock_financials"
    )
    async def test_get_concise_stock_financials_tool(self, mock_processor, mock_client):
        """Test financials tool with currency parameter."""
        from app.main import get_concise_stock_financials

        # Setup mocks
        mock_client.return_value = {
            "financials": {
                "financial_template_parameters": {"REITs": "N"},
                "annuals": {"Fiscal Year": ["2023"]},
            }
        }
        mock_processor.return_value = {
            "is_reit": False,
            "jahresabschlüsse": {"perioden": ["2023"]},
        }

        result = await get_concise_stock_financials("AAPL", "EUR")

        # Verify API called with correct parameters
        mock_client.assert_called_once_with("AAPL", "EUR")
        mock_processor.assert_called_once()
        assert result["is_reit"] is False

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_stock_financials")
    async def test_get_concise_stock_financials_default_currency(self, mock_client):
        """Test financials tool with default currency."""
        from app.main import get_concise_stock_financials

        mock_client.return_value = {
            "financials": {
                "financial_template_parameters": {"REITs": "N"},
                "annuals": {},
            }
        }

        await get_concise_stock_financials("AAPL")

        # Should use default currency USD
        mock_client.assert_called_once_with("AAPL", "USD")

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_stock_financials")
    async def test_get_concise_stock_financials_exception_handling(self, mock_client):
        """Test financials tool exception handling."""
        from app.main import get_concise_stock_financials

        # Mock exception
        mock_client.side_effect = Exception("API Error")

        result = await get_concise_stock_financials("TEST")

        # Should handle exception gracefully
        assert "error" in result
        assert "Fehler bei der Verarbeitung der Finanzdaten für TEST" in result["error"]
        assert result["is_reit"] is False
        assert "jahresabschlüsse" in result

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_analyst_estimates")
    @patch(
        "app.processors.analyst_processor.AnalystProcessor.process_analyst_estimates"
    )
    async def test_get_concise_analyst_estimates_tool(
        self, mock_processor, mock_client
    ):
        """Test analyst estimates tool."""
        from app.main import get_concise_analyst_estimates

        # Setup mocks
        mock_client.return_value = {
            "annual": {
                "date": ["2024", "2025"],
                "revenue_estimate": [400000000000, 420000000000],
            }
        }
        mock_processor.return_value = {
            "jährlich": {"2024": {"umsatz": 400000000000}},
            "quartal": {},
            "wachstumsraten": {},
        }

        result = await get_concise_analyst_estimates("AAPL")

        mock_client.assert_called_once_with("AAPL")
        mock_processor.assert_called_once()
        assert "jährlich" in result

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_analyst_estimates")
    async def test_get_concise_analyst_estimates_api_failure(self, mock_client):
        """Test analyst estimates tool with API failure."""
        from app.main import get_concise_analyst_estimates

        mock_client.return_value = None

        result = await get_concise_analyst_estimates("INVALID")

        assert "error" in result
        assert (
            "Konnte keine Analystenschätzungen für INVALID abrufen" in result["error"]
        )

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_segments_data")
    @patch("app.processors.segments_processor.SegmentsProcessor.process_segments_data")
    async def test_get_concise_segments_data_tool(self, mock_processor, mock_client):
        """Test segments data tool."""
        from app.main import get_concise_segments_data

        # Setup mocks
        mock_client.return_value = {
            "business": {"annual": [{"date": "2023", "iPhone": 200000000000}]}
        }
        mock_processor.return_value = {
            "geschäftsbereiche": {"jährlich": [], "ttm": {}},
            "regionen": {"jährlich": []},
        }

        result = await get_concise_segments_data("AAPL", "202301")

        mock_client.assert_called_once_with("AAPL", "202301")
        mock_processor.assert_called_once()
        assert "geschäftsbereiche" in result

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_segments_data")
    async def test_get_concise_segments_data_default_start_date(self, mock_client):
        """Test segments data tool with default start date."""
        from app.main import get_concise_segments_data

        mock_client.return_value = {"business": {}, "geographic": {}}

        await get_concise_segments_data("AAPL")

        # Should use default start_date
        mock_client.assert_called_once_with("AAPL", "201901")

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_segments_data")
    async def test_get_concise_segments_data_api_failure(self, mock_client):
        """Test segments data tool with API failure."""
        from app.main import get_concise_segments_data

        mock_client.return_value = None

        result = await get_concise_segments_data("INVALID", "202301")

        assert "error" in result
        assert "Konnte keine Segmentdaten für INVALID abrufen" in result["error"]

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_news_headlines")
    async def test_get_concise_news_headlines_tool(self, mock_client):
        """Test news headlines tool."""
        from app.main import get_concise_news_headlines

        # Setup mock
        mock_client.return_value = {
            "news": [
                {
                    "date": "2024-01-15",
                    "headline": "Apple Reports Strong Q4 Results",
                    "url": "https://example.com/news1",
                }
            ]
        }

        result = await get_concise_news_headlines("AAPL")

        mock_client.assert_called_once_with("AAPL")
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    @patch("app.main.GuruFocusClient.get_news_headlines")
    async def test_get_concise_news_headlines_exception_handling(self, mock_client):
        """Test news headlines tool exception handling."""
        from app.main import get_concise_news_headlines

        # Mock exception
        mock_client.side_effect = Exception("API Error")

        result = await get_concise_news_headlines("TEST")

        # Should handle exception gracefully
        assert isinstance(result, list)
        assert len(result) == 1
        assert "error" in result[0]
        assert "Fehler beim Abrufen der Nachrichten für TEST" in result[0]["error"]

    @pytest.mark.asyncio
    async def test_mcp_tools_module_imports(self):
        """Test that all MCP tool functions can be imported."""
        try:
            from app.main import (
                get_concise_stock_summary,
                get_concise_stock_financials,
                get_concise_analyst_estimates,
                get_concise_segments_data,
                get_concise_news_headlines,
            )

            # Verify functions are callable
            assert callable(get_concise_stock_summary)
            assert callable(get_concise_stock_financials)
            assert callable(get_concise_analyst_estimates)
            assert callable(get_concise_segments_data)
            assert callable(get_concise_news_headlines)

        except ImportError as e:
            pytest.fail(f"Failed to import MCP tool functions: {e}")

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test concurrent execution of multiple tool functions."""
        from app.main import get_concise_stock_summary

        with patch("app.main.GuruFocusClient.get_stock_summary") as mock_client:
            # Setup mock to return different data for different symbols
            def side_effect(symbol):
                return {
                    "summary": {
                        "general": {"company": f"{symbol} Corp", "price": 100.0},
                        "ratio": {},
                    }
                }

            mock_client.side_effect = side_effect

            # Execute multiple tools concurrently
            tasks = [
                get_concise_stock_summary("AAPL"),
                get_concise_stock_summary("MSFT"),
                get_concise_stock_summary("GOOGL"),
            ]

            results = await asyncio.gather(*tasks)

            # Verify all executed successfully
            assert len(results) == 3
            for i, result in enumerate(results):
                assert "allgemein" in result
                # Each should have different company names
                assert "Corp" in result["allgemein"]["firma"]

            # Verify all API calls were made
            assert mock_client.call_count == 3

    @pytest.mark.asyncio
    async def test_mcp_tool_parameter_validation(self):
        """Test MCP tool parameter validation."""
        from app.main import get_concise_stock_summary

        with patch("app.main.GuruFocusClient.get_stock_summary") as mock_client:
            mock_client.return_value = None

            # Test with various symbol formats
            symbols_to_test = ["AAPL", "XTRA:DHL.DE", "TEST", ""]

            for symbol in symbols_to_test:
                result = await get_concise_stock_summary(symbol)

                # Should handle all gracefully
                assert isinstance(result, dict)

                if symbol:  # Non-empty symbols should call API
                    mock_client.assert_called_with(symbol)
                else:  # Empty symbol might be handled differently
                    pass

            # Reset mock for final assertion
            mock_client.reset_mock()

    @pytest.mark.asyncio
    async def test_error_propagation_in_tools(self):
        """Test that errors are properly handled and not propagated as exceptions."""
        from app.main import (
            get_concise_stock_summary,
            get_concise_stock_financials,
            get_concise_analyst_estimates,
            get_concise_segments_data,
            get_concise_news_headlines,
        )

        # Test that all tools handle None return from API gracefully
        with (
            patch(
                "app.main.GuruFocusClient.get_stock_summary", new_callable=AsyncMock
            ) as mock_summary,
            patch(
                "app.main.GuruFocusClient.get_stock_financials", new_callable=AsyncMock
            ) as mock_financials,
            patch(
                "app.main.GuruFocusClient.get_analyst_estimates", new_callable=AsyncMock
            ) as mock_estimates,
            patch(
                "app.main.GuruFocusClient.get_segments_data", new_callable=AsyncMock
            ) as mock_segments,
            patch(
                "app.main.GuruFocusClient.get_news_headlines", new_callable=AsyncMock
            ) as mock_news,
        ):
            mock_summary.return_value = None
            mock_financials.return_value = None
            mock_estimates.return_value = None
            mock_segments.return_value = None
            mock_news.return_value = None

            # All should handle None gracefully without raising exceptions
            tools_to_test = [
                (get_concise_stock_summary, ["TEST"]),
                (get_concise_stock_financials, ["TEST"]),
                (get_concise_analyst_estimates, ["TEST"]),
                (get_concise_segments_data, ["TEST"]),
                (get_concise_news_headlines, ["TEST"]),
            ]

            for tool_func, args in tools_to_test:
                try:
                    result = await tool_func(*args)
                    # Should return result, not raise exception
                    assert result is not None
                    assert isinstance(result, (dict, list))
                except Exception as e:
                    pytest.fail(f"Tool {tool_func.__name__} raised exception: {e}")
