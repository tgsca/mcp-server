"""
Prozessor für Nachrichtenüberschriften.
"""

from typing import Dict, List, Union
import json


class NewsProcessor:
    """Verarbeitet Nachrichtenüberschriften."""

    @staticmethod
    def process_news_headlines(
        headlines_data: Union[str, Dict, List, None],
    ) -> List[Dict[str, str]]:
        """
        Verarbeitet die Nachrichtenüberschriften und strukturiert sie.

        Args:
            headlines_data: Original-API-Antwort von get_news_headlines (kann String, Dict, List oder None sein)

        Returns:
            Liste von Nachrichten-Dictionaries
        """
        headlines = []

        # Fehlerfall: Keine Daten
        if headlines_data is None:
            return [{"error": "Keine Nachrichtendaten verfügbar"}]

        # Fall 1: Wenn es bereits eine Liste ist
        if isinstance(headlines_data, list):
            for item in headlines_data:
                if isinstance(item, dict):
                    headlines.append(
                        {
                            "datum": item.get("date", ""),
                            "überschrift": item.get("headline", ""),
                            "url": item.get("url", ""),
                        }
                    )

            # Nach Datum sortieren (neueste zuerst)
            headlines.sort(key=lambda x: x.get("datum", ""), reverse=True)
            return headlines

        # Fall 2: Wenn es bereits ein Dictionary ist
        if isinstance(headlines_data, dict):
            return [
                {
                    "datum": headlines_data.get("date", ""),
                    "überschrift": headlines_data.get("headline", ""),
                    "url": headlines_data.get("url", ""),
                }
            ]

        # Fall 3: Wenn es ein String ist (erwartetes Format von der API)
        if isinstance(headlines_data, str):
            try:
                # Prüfen, ob der String ein JSON-Array ist
                try:
                    json_data = json.loads(headlines_data)
                    if isinstance(json_data, list):
                        for item in json_data:
                            headlines.append(
                                {
                                    "datum": item.get("date", ""),
                                    "überschrift": item.get("headline", ""),
                                    "url": item.get("url", ""),
                                }
                            )
                        headlines.sort(key=lambda x: x.get("datum", ""), reverse=True)
                        return headlines
                except json.JSONDecodeError:
                    pass

                # Wenn es kein JSON-Array ist, versuchen wir es mit dem ursprünglichen Format
                # Die API gibt manchmal mehrere JSON-Objekte zurück, die nicht in einer Liste stehen
                json_objects = headlines_data.strip().split("}{")

                for i, obj in enumerate(json_objects):
                    # JSON-Objekte wiederherstellen
                    if i > 0:
                        obj = "{" + obj
                    if i < len(json_objects) - 1:
                        obj = obj + "}"

                    try:
                        headline_data = json.loads(obj)

                        # Nur die wichtigen Informationen behalten
                        headlines.append(
                            {
                                "datum": headline_data.get("date", ""),
                                "überschrift": headline_data.get("headline", ""),
                                "url": headline_data.get("url", ""),
                            }
                        )
                    except json.JSONDecodeError:
                        continue

                # Nach Datum sortieren (neueste zuerst)
                headlines.sort(key=lambda x: x.get("datum", ""), reverse=True)

            except Exception as e:
                return [
                    {
                        "error": f"Fehler bei der Verarbeitung der Nachrichtendaten: {str(e)}"
                    }
                ]

        # Wenn keine Schlagzeilen gefunden wurden, Fehler zurückgeben
        if not headlines:
            return [
                {"error": "Keine Nachrichten gefunden oder Format nicht unterstützt"}
            ]

        return headlines
