"""
Tests for the GuruFocusClient API client.
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock
import httpx
from app.api.client import GuruFocusClient


class TestGuruFocusClient:
    """Test cases for GuruFocusClient."""

    @pytest.mark.asyncio
    async def test_request_data_success(self, mock_httpx_client):
        """Test successful API request."""
        client_mock, response_mock = mock_httpx_client
        response_mock.json.return_value = {"test": "data"}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = client_mock
            
            result = await GuruFocusClient.request_data("https://test.com")
            
            assert result == {"test": "data"}
            client_mock.get.assert_called_once_with("https://test.com")
            response_mock.raise_for_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_data_timeout(self):
        """Test API request timeout handling."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.TimeoutException("Timeout")
            
            result = await GuruFocusClient.request_data("https://test.com")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_request_data_http_status_error(self):
        """Test HTTP status error handling."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 404
            mock_client.get.side_effect = httpx.HTTPStatusError(
                "Not Found", request=Mock(), response=mock_response
            )
            
            result = await GuruFocusClient.request_data("https://test.com")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_request_data_json_error(self, mock_httpx_client):
        """Test JSON parsing error handling."""
        client_mock, response_mock = mock_httpx_client
        response_mock.json.side_effect = ValueError("Invalid JSON")
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = client_mock
            
            result = await GuruFocusClient.request_data("https://test.com")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_stock_summary(self):
        """Test get_stock_summary method."""
        expected_data = {"summary": {"general": {"company": "Apple Inc"}}}
        
        with patch.object(GuruFocusClient, 'request_data', return_value=expected_data) as mock_request:
            result = await GuruFocusClient.get_stock_summary("AAPL")
            
            assert result == expected_data
            mock_request.assert_called_once()
            call_args = mock_request.call_args[0][0]
            assert "stock/AAPL/summary" in call_args

    @pytest.mark.asyncio
    async def test_get_stock_financials(self):
        """Test get_stock_financials method."""
        expected_data = {"annual": {"Revenue": [100000, 200000]}}
        
        with patch.object(GuruFocusClient, 'request_data', return_value=expected_data) as mock_request:
            result = await GuruFocusClient.get_stock_financials("AAPL", "EUR")
            
            assert result == expected_data
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert "stock/AAPL/financials" in call_args[0][0]
            assert "target_currency=EUR" in call_args[0][0]
            assert call_args[1]["timeout"] == 60  # Check extended timeout

    @pytest.mark.asyncio
    async def test_get_analyst_estimates(self):
        """Test get_analyst_estimates method."""
        expected_data = {"estimates": {"Revenue": {"2024": 100000}}}
        
        with patch.object(GuruFocusClient, 'request_data', return_value=expected_data) as mock_request:
            result = await GuruFocusClient.get_analyst_estimates("AAPL")
            
            assert result == expected_data
            mock_request.assert_called_once()
            call_args = mock_request.call_args[0][0]
            assert "stock/AAPL/analyst_estimate" in call_args

    @pytest.mark.asyncio
    async def test_get_segments_data(self):
        """Test get_segments_data method."""
        expected_data = {"business_segments": {"iPhone": {"2023": 200000}}}
        
        with patch.object(GuruFocusClient, 'request_data', return_value=expected_data) as mock_request:
            result = await GuruFocusClient.get_segments_data("AAPL", "202301")
            
            assert result == expected_data
            mock_request.assert_called_once()
            call_args = mock_request.call_args[0][0]
            assert "stock/AAPL/segments_data" in call_args
            assert "start_date=202301" in call_args

    @pytest.mark.asyncio
    async def test_get_news_headlines(self):
        """Test get_news_headlines method."""
        expected_data = {"news": [{"title": "Apple News"}]}
        
        with patch.object(GuruFocusClient, 'request_data', return_value=expected_data) as mock_request:
            result = await GuruFocusClient.get_news_headlines("AAPL")
            
            assert result == expected_data
            mock_request.assert_called_once()
            call_args = mock_request.call_args[0][0]
            assert "stock/news_feed" in call_args
            assert "symbol=AAPL" in call_args

    @pytest.mark.asyncio
    async def test_request_data_with_custom_timeout(self, mock_httpx_client):
        """Test request with custom timeout."""
        client_mock, response_mock = mock_httpx_client
        response_mock.json.return_value = {"test": "data"}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = client_mock
            
            await GuruFocusClient.request_data("https://test.com", timeout=60)
            
            # Verify timeout was passed to AsyncClient
            mock_client_class.assert_called_once_with(timeout=60)

    @pytest.mark.asyncio
    async def test_request_data_general_http_error(self):
        """Test handling of general HTTP errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.HTTPError("General HTTP error")
            
            result = await GuruFocusClient.request_data("https://test.com")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_request_data_unexpected_exception(self):
        """Test handling of unexpected exceptions."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.side_effect = Exception("Unexpected error")
            
            result = await GuruFocusClient.request_data("https://test.com")
            
            assert result is None