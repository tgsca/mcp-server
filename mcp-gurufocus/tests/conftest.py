"""
Pytest configuration and shared fixtures.
"""

import pytest
from unittest.mock import AsyncMock, Mock


@pytest.fixture
def mock_stock_summary_response():
    """Mock response for stock summary API call."""
    return {
        "summary": {
            "general": {
                "company": "Apple Inc",
                "price": 150.25,
                "currency": "$",
                "gf_score": "85",
                "gf_valuation": "Fairly Valued",
                "sector": "Technology",
                "group": "Hardware",
                "subindustry": "Consumer Electronics",
                "country": "USA",
                "risk_assessment": "Medium"
            },
            "ratio": {
                "P/E(ttm)": {"value": 25.5},
                "Forward P/E": {"value": 22.1},
                "P/S": {"value": 7.2},
                "P/B": {"value": 8.9},
                "Operating margin (%)": {"value": 30.1}
            }
        }
    }


@pytest.fixture
def mock_financials_response():
    """Mock response for stock financials API call."""
    return {
        "is_reit": False,
        "annual": {
            "Fiscal Year": ["2023-09", "2022-09", "2021-09"],
            "Revenue": [394328000000, 365817000000, 274515000000],
            "Net Income": [97001000000, 99803000000, 94680000000]
        },
        "quarterly": {
            "Fiscal Year": ["2024-03", "2023-12", "2023-09"],
            "Revenue": [90753000000, 119575000000, 89498000000]
        }
    }


@pytest.fixture
def mock_analyst_estimates_response():
    """Mock response for analyst estimates API call."""
    return {
        "annual": {
            "date": ["2024", "2025", "2026"],
            "revenue_estimate": [385000000000, 410000000000, 435000000000],
            "net_income_estimate": [95000000000, 105000000000, 115000000000],
            "per_share_eps_estimate": [6.15, 6.85, 7.50],
            "dividend_estimate": [0.95, 1.05, 1.15],
            "roe_estimate": [28.5, 30.2, 32.1],
            "gross_margin_estimate": [42.5, 43.1, 43.8],
            "future_revenue_estimate_growth": 8.5,
            "future_eps_estimate_growth": 12.2
        },
        "quarterly": {
            "date": ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4", "2025-Q1"],
            "revenue_estimate": [95000000000, 98000000000, 92000000000, 100000000000, 102000000000],
            "net_income_estimate": [23000000000, 24500000000, 22000000000, 25500000000, 26000000000],
            "per_share_eps_estimate": [1.48, 1.58, 1.42, 1.65, 1.68]
        }
    }


@pytest.fixture
def mock_segments_response():
    """Mock response for segments data API call."""
    return {
        "business": {
            "annual": [
                {
                    "date": "2023",
                    "iPhone": 200583000000,
                    "Services": 85200000000,
                    "Mac": 29357000000,
                    "iPad": 28300000000,
                    "Wearables": 39845000000
                },
                {
                    "date": "2022", 
                    "iPhone": 205489000000,
                    "Services": 78129000000,
                    "Mac": 40177000000,
                    "iPad": 29292000000,
                    "Wearables": 41241000000
                }
            ],
            "ttm": [
                {
                    "date": "TTM 2024-Q1",
                    "iPhone": 189968000000,
                    "Services": 85500000000,
                    "Mac": 24943000000,
                    "iPad": 24814000000,
                    "Wearables": 37467000000
                }
            ]
        },
        "geographic": {
            "annual": [
                {
                    "date": "2023",
                    "Americas": 162560000000,
                    "Europe": 94294000000,
                    "Greater China": 72559000000,
                    "Japan": 24257000000,
                    "Rest of Asia Pacific": 29615000000
                },
                {
                    "date": "2022",
                    "Americas": 169658000000,
                    "Europe": 95118000000,
                    "Greater China": 74200000000,
                    "Japan": 25977000000,
                    "Rest of Asia Pacific": 29375000000
                }
            ]
        }
    }


@pytest.fixture
def mock_news_response():
    """Mock response for news headlines API call."""
    return {
        "news": [
            {
                "title": "Apple Reports Strong Q4 Results",
                "date": "2024-01-15",
                "url": "https://example.com/news1"
            },
            {
                "title": "New iPhone Sales Exceed Expectations",
                "date": "2024-01-14",
                "url": "https://example.com/news2"
            }
        ]
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for API calls."""
    client = AsyncMock()
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock()
    client.get.return_value = response
    return client, response