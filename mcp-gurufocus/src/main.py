import os
from typing import Dict, Any
from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP

load_dotenv()

BASE_URL = f"https://api.gurufocus.com/public/user/{os.getenv('GURUFOCUS_API_KEY')}"

mcp = FastMCP("financials")

""" Helper Functions """
async def request_data(url: str) -> Dict[str, Any] | None:
    response = httpx.get(url)

    if response.status_code == 200:
        return response.json()

    return None

""" Request Functions """
async def request_stock_summary(symbol: str) -> Dict[str, Any] | None:
    url = f"{BASE_URL}/stock/{symbol}/summary"
    return await request_data(url)

async def request_stock_financials(symbol: str) -> Dict[str, Any] | None:
    url = f"{BASE_URL}/stock/{symbol}/financials?order=desc&target_currency=USD"
    return await request_data(url)

async def request_analyst_estimate(symbol: str) -> Dict[str, Any] | None:
    url = f"{BASE_URL}/stock/{symbol}/analyst_estimate"
    return await request_data(url)

async def request_segment_data(symbol: str, start_date: str) -> Dict[str, Any] | None:
    url = f"{BASE_URL}/stock/{symbol}/segments_data?start_date={start_date}"
    return await request_data(url)

async def request_news_headlines(symbol: str) -> Dict[str, Any] | None:
    url = f"{BASE_URL}/stock/news_feed?symbol={symbol}"
    return await request_data(url)

""" Pre-Processing Functions """
# ...

""" Tools """
@mcp.tool()
async def get_stock_summary(symbol: str) -> Dict[str, Any] | None:
    """
    Get basic stock information for a given symbol.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"

    Returns:
        Dict[str, Any] | None: A dictionary containing stock information or None if the request fails.
    """
    return await request_stock_summary(symbol)

@mcp.tool()
async def get_stock_financials(symbol: str) -> Dict[str, Any] | None:
    """
    Get financial data.
    - is it a REIT or not
    - annual and quarterly
    - balance sheet
    - income statement
    - cashflow statement
    - per share data
    - general ratios
    - valuation ratios
    - valuation and quality 

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"

    Returns:
        Dict[str, Any] | None: A dictionary containing stock financials or None if the request fails.
    """
    return await request_stock_financials(symbol)

@mcp.tool()
async def get_analyst_estimates(symbol: str) -> Dict[str, Any] | None:
    """
    Get estmiate for divers figures for the next 3 years.
    Figures are like:
    - revenue
    - ebit
    - ebitda
    - net income
    - eps
    - dividend
    - etc. 

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"

    Returns:
        Dict[str, Any] | None: A dictionary containing estimates or None if the request fails.
    """
    return await request_analyst_estimate(symbol)

@mcp.tool()
async def get_segments_data(symbol: str, start_date: str) -> Dict[str, Any] | None:
    """
    Get segment data for a given symbol.
    Segments may contain business segments as well es geographical segments.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"
        start_date (str): The start month from which the data are requested. E.g. 202701 means 'January 2017'

    Returns:
        Dict[str, Any] | None: A dictionary containing the segment data or None if the request fails.
    """
    return await request_segment_data(symbol, start_date)

@mcp.tool()
async def get_news_headlines(symbol: str) -> Dict[str, Any] | None:
    """
    Get the news headlines for a given symbol.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"

    Returns:
        Dict[str, Any] | None: A dictionary containing the news headlines or None if the request fails.
    """
    return await request_news_headlines(symbol)

if __name__ == "__main__":
    mcp.run(transport='stdio')
