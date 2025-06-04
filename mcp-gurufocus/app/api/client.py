"""
API-Client für die GuruFocus API.
"""

from typing import Dict, Any, Optional, Union
import httpx
from ..config import BASE_URL


class GuruFocusClient:
    """Client für die GuruFocus API."""

    @staticmethod
    async def request_data(url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        Sendet eine Anfrage an die angegebene URL und gibt die JSON-Antwort zurück.

        Args:
            url: Die URL, an die die Anfrage gesendet wird
            timeout: Timeout in Sekunden (Standard: 30)

        Returns:
            Die JSON-Antwort als Dictionary oder None bei einem Fehler
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.json()
                except httpx.TimeoutException:
                    print(f"API request timed out: {url}")
                    return None
                except httpx.HTTPStatusError as e:
                    print(f"API HTTP error: {e.response.status_code} - {e}")
                    return None
                except httpx.HTTPError as e:
                    print(f"API HTTP error: {e}")
                    return None
                except ValueError as e:
                    print(f"API JSON parsing error: {e}")
                    return None
        except Exception as e:
            print(f"Unexpected error during API request: {e}")
            return None

    @classmethod
    async def get_stock_summary(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Ruft die Zusammenfassung einer Aktie ab.

        Args:
            symbol: Das Aktiensymbol

        Returns:
            Die API-Antwort als Dictionary oder None bei einem Fehler
        """
        url = f"{BASE_URL}/stock/{symbol}/summary"
        return await cls.request_data(url)

    @classmethod
    async def get_stock_financials(
        cls, symbol: str, target_currency: str = "USD"
    ) -> Optional[Dict[str, Any]]:
        """
        Ruft die Finanzdaten einer Aktie ab.

        Args:
            symbol: Das Aktiensymbol

        Returns:
            Die API-Antwort als Dictionary oder None bei einem Fehler
        """
        url = f"{BASE_URL}/stock/{symbol}/financials?order=desc&target_currency={target_currency}"
        # Finanzdaten können umfangreich sein, daher längeren Timeout verwenden
        return await cls.request_data(url, timeout=60)

    @classmethod
    async def get_analyst_estimates(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Ruft die Analystenschätzungen für eine Aktie ab.

        Args:
            symbol: Das Aktiensymbol

        Returns:
            Die API-Antwort als Dictionary oder None bei einem Fehler
        """
        url = f"{BASE_URL}/stock/{symbol}/analyst_estimate"
        return await cls.request_data(url)

    @classmethod
    async def get_segments_data(
        cls, symbol: str, start_date: str
    ) -> Optional[Dict[str, Any]]:
        """
        Ruft die Segmentdaten einer Aktie ab.

        Args:
            symbol: Das Aktiensymbol
            start_date: Das Startdatum im Format YYYYMM

        Returns:
            Die API-Antwort als Dictionary oder None bei einem Fehler
        """
        url = f"{BASE_URL}/stock/{symbol}/segments_data?start_date={start_date}"
        return await cls.request_data(url)

    @classmethod
    async def get_news_headlines(
        cls, symbol: str
    ) -> Optional[Union[Dict[str, Any], str, list]]:
        """
        Ruft die Nachrichtenüberschriften für eine Aktie ab.

        Args:
            symbol: Das Aktiensymbol

        Returns:
            Die API-Antwort als Dictionary, String, Liste oder None bei einem Fehler
        """
        url = f"{BASE_URL}/stock/news_feed?symbol={symbol}"
        return await cls.request_data(url)
