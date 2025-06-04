"""
Hauptanwendung für die Finanz-API.
"""

import os
from typing import Dict, Any, List
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from app.api.client import GuruFocusClient
from app.processors.stock_processor import StockProcessor
from app.processors.financials_processor import FinancialsProcessor
from app.processors.analyst_processor import AnalystProcessor
from app.processors.segments_processor import SegmentsProcessor
from app.processors.news_processor import NewsProcessor
from app.processors.report_generator import ReportGenerator

load_dotenv()

# MCP-Server erstellen
mcp = FastMCP("financials")

"""
Tools für den Zugriff auf die Finanz-API.
"""

#
# Rohdaten-Tools
#

#@mcp.tool()
async def get_stock_summary(symbol: str) -> Dict[str, Any] | None:
    """
    Get basic stock information for a given symbol.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"

    Returns:
        Dict[str, Any] | None: A dictionary containing stock information or None if the request fails.
    """
    return await GuruFocusClient.get_stock_summary(symbol)

#@mcp.tool()
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
    return await GuruFocusClient.get_stock_financials(symbol)

#@mcp.tool()
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
    return await GuruFocusClient.get_analyst_estimates(symbol)

#@mcp.tool()
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
    return await GuruFocusClient.get_segments_data(symbol, start_date)

#@mcp.tool()
async def get_news_headlines(symbol: str) -> Dict[str, Any] | None:
    """
    Get the news headlines for a given symbol.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"

    Returns:
        Dict[str, Any] | None: A dictionary containing the news headlines or None if the request fails.
    """
    return await GuruFocusClient.get_news_headlines(symbol)

#
# Verarbeitete Daten-Tools
#

@mcp.tool()
async def get_concise_stock_summary(symbol: str) -> Dict[str, Any]:
    """
    Get concise, processed stock summary information for a given symbol.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"

    Returns:
        Dict[str, Any]: A dictionary containing processed stock summary information.
    """
    # Rohdaten abrufen
    raw_data = await GuruFocusClient.get_stock_summary(symbol)
    
    # Daten verarbeiten
    if raw_data:
        return StockProcessor.process_stock_summary(raw_data)
    else:
        return {"error": f"Konnte keine Daten für {symbol} abrufen"}

@mcp.tool()
async def get_concise_stock_financials(symbol: str, target_currency: str = "USD") -> Dict[str, Any]:
    """
    Get concise, processed financial data for a given symbol.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"
        target_currency (str, optional): The target currency to convert the financial data to. Defaults to "USD".
    Returns:
        Dict[str, Any]: A dictionary containing processed financial information.
    """
    try:
        # Rohdaten abrufen
        raw_data = await GuruFocusClient.get_stock_financials(symbol, target_currency)
        
        # Daten verarbeiten
        if raw_data:
            # Wenn wir gültige Daten haben, verarbeiten wir sie
            return FinancialsProcessor.process_stock_financials(raw_data)
        else:
            # Falls keine Daten, erstellen wir eine Dummy-Struktur für das erwartete Format
            return {
                "is_reit": False,
                "jahresabschlüsse": {
                    "bilanz": {"jährlich": {"perioden": [], "daten": {}}, "quartal": {"perioden": [], "daten": {}}},
                    "gewinn_verlust": {"jährlich": {"perioden": [], "daten": {}}, "quartal": {"perioden": [], "daten": {}}},
                    "cashflow": {"jährlich": {"perioden": [], "daten": {}}, "quartal": {"perioden": [], "daten": {}}}
                },
                "kennzahlen": {
                    "pro_aktie": {"perioden": [], "daten": {}},
                    "allgemein": {"perioden": [], "daten": {}},
                    "bewertung": {"perioden": [], "daten": {}}
                },
                "qualität": {},
                "hinweis": f"Keine Finanzdaten für {symbol} verfügbar. Der API-Request hat keine Daten zurückgegeben oder ist fehlgeschlagen."
            }
    except Exception as e:
        # Bei unerwarteten Fehlern geben wir eine passende Fehlermeldung zurück
        return {
            "error": f"Fehler bei der Verarbeitung der Finanzdaten für {symbol}: {str(e)}",
            "is_reit": False,
            "jahresabschlüsse": {},
            "kennzahlen": {},
            "qualität": {}
        }

@mcp.tool()
async def get_concise_analyst_estimates(symbol: str) -> Dict[str, Any]:
    """
    Get concise, processed analyst estimates for a given symbol.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"

    Returns:
        Dict[str, Any]: A dictionary containing processed analyst estimates.
    """
    # Rohdaten abrufen
    raw_data = await GuruFocusClient.get_analyst_estimates(symbol)
    
    # Daten verarbeiten
    if raw_data:
        return AnalystProcessor.process_analyst_estimates(raw_data)
    else:
        return {"error": f"Konnte keine Analystenschätzungen für {symbol} abrufen"}

@mcp.tool()
async def get_concise_segments_data(symbol: str, start_date: str = "201901") -> Dict[str, Any]:
    """
    Get concise, processed segment data for a given symbol.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"
        start_date (str, optional): The start month from which the data are requested. Defaults to "201901".

    Returns:
        Dict[str, Any]: A dictionary containing processed segment data.
    """
    # Rohdaten abrufen
    raw_data = await GuruFocusClient.get_segments_data(symbol, start_date)
    
    # Daten verarbeiten
    if raw_data:
        return SegmentsProcessor.process_segments_data(raw_data)
    else:
        return {"error": f"Konnte keine Segmentdaten für {symbol} abrufen"}

@mcp.tool()
async def get_concise_news_headlines(symbol: str) -> List[Dict[str, str]]:
    """
    Get concise, processed news headlines for a given symbol.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"

    Returns:
        List[Dict[str, str]]: A list of processed news headline dictionaries.
    """
    try:
        # Rohdaten abrufen
        raw_data = await GuruFocusClient.get_news_headlines(symbol)
        
        # Daten verarbeiten - wir verwenden die verbesserte Methode,
        # die mit verschiedenen Eingabeformaten umgehen kann
        return NewsProcessor.process_news_headlines(raw_data)
    except Exception as e:
        return [{"error": f"Fehler beim Abrufen der Nachrichten für {symbol}: {str(e)}"}]

#@mcp.tool()
async def process_and_generate_report(symbol: str, start_date: str = "201901") -> Dict[str, Any]:
    """
    Get, process, and generate a comprehensive report for a stock.

    Args:
        symbol (str): The stock symbol to get information for. US stocks with the format "AAPL", other stocks with the format "XTRA:DHL.DE"
        start_date (str, optional): The start date for segment data. Defaults to "201901".

    Returns:
        Dict[str, Any]: A comprehensive report with processed data.
    """
    try:
        # Daten parallel abrufen, um die Gesamtantwortzeit zu reduzieren
        tasks = [
            GuruFocusClient.get_stock_summary(symbol),
            GuruFocusClient.get_analyst_estimates(symbol),
            GuruFocusClient.get_segments_data(symbol, start_date),
            GuruFocusClient.get_news_headlines(symbol)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse extrahieren und prüfen
        summary_data, estimates_data, segments_data, news_data = results
        
        # Prüfen, ob eine der Anfragen eine Exception zurückgegeben hat
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Fehler bei API-Anfrage {i}: {result}")
                results[i] = None
        
        # Daten verarbeiten, wobei wir sicherstellen, dass keine None-Werte an die Prozessoren weitergegeben werden
        processed_summary = StockProcessor.process_stock_summary(summary_data) if summary_data else {"error": "Keine Summary-Daten verfügbar"}
        processed_estimates = AnalystProcessor.process_analyst_estimates(estimates_data) if estimates_data else {"error": "Keine Estimates-Daten verfügbar"}
        processed_segments = SegmentsProcessor.process_segments_data(segments_data) if segments_data else {"error": "Keine Segment-Daten verfügbar"}
        processed_news = NewsProcessor.process_news_headlines(news_data)  # Diese Methode kann mit None-Werten umgehen
        
        # Bericht erstellen
        report = ReportGenerator.generate_summary_report(
            processed_summary,
            processed_estimates,
            processed_segments,
            processed_news,
            symbol
        )
        
        return report
    except Exception as e:
        # Fehlerbehandlung
        return {
            "error": f"Fehler bei der Erstellung des Berichts für {symbol}: {str(e)}",
            "symbol": symbol,
            "erstellt_am": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "fehlgeschlagen"
        }

if __name__ == "__main__":
    mcp.run(transport=os.getenv("MCP_SERVER_MODE", "stdio"))
