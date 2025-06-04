"""
Prozessor für Segmentdaten.
"""

from typing import Dict, Any


class SegmentsProcessor:
    """Verarbeitet Segmentdaten."""

    @staticmethod
    def process_segments_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet die Segmentdaten und bereitet sie für die Analyse auf.

        Args:
            data: Original-API-Antwort von get_segments_data

        Returns:
            Dict mit aufbereiteten Segment-Daten
        """
        if not data or not isinstance(data, dict):
            return {"error": "Keine gültigen Daten verfügbar"}

        result = {
            "geschäftsbereiche": {"jährlich": [], "ttm": {}},
            "regionen": {"jährlich": []},
        }

        # Geschäftsbereiche verarbeiten
        business = data.get("business", {})

        # Jährliche Daten für Geschäftsbereiche
        annual_business = business.get("annual", [])
        for year_data in annual_business:
            date = year_data.pop("date", "")
            if date:
                # Berechnen des Gesamtumsatzes für dieses Jahr
                total_revenue = sum(value for key, value in year_data.items())

                # Prozentuale Anteile berechnen
                segments_with_percentage = {
                    "jahr": date,
                    "total": total_revenue,
                    "segmente": {},
                }

                for segment, value in year_data.items():
                    segments_with_percentage["segmente"][segment] = {
                        "umsatz": value,
                        "anteil": round((value / total_revenue * 100), 2)
                        if total_revenue
                        else 0,
                    }

                result["geschäftsbereiche"]["jährlich"].append(segments_with_percentage)

        # TTM-Daten für Geschäftsbereiche
        ttm_business = business.get("ttm", [])
        if ttm_business and len(ttm_business) > 0:
            ttm_data = ttm_business[0]
            date = ttm_data.pop("date", "")

            # Gesamtumsatz berechnen
            total_revenue = sum(
                value for key, value in ttm_data.items() if key != "date"
            )

            result["geschäftsbereiche"]["ttm"] = {
                "zeitraum": date,
                "total": total_revenue,
                "segmente": {},
            }

            for segment, value in ttm_data.items():
                if segment != "date":
                    result["geschäftsbereiche"]["ttm"]["segmente"][segment] = {
                        "umsatz": value,
                        "anteil": round((value / total_revenue * 100), 2)
                        if total_revenue
                        else 0,
                    }

        # Regionen verarbeiten
        geographic = data.get("geographic", {})
        annual_geographic = geographic.get("annual", [])

        for year_data in annual_geographic:
            date = year_data.pop("date", "")
            if date:
                # Berechnen des Gesamtumsatzes für diese Region
                total_revenue = sum(value for key, value in year_data.items())

                # Prozentuale Anteile berechnen
                regions_with_percentage = {
                    "jahr": date,
                    "total": total_revenue,
                    "regionen": {},
                }

                for region, value in year_data.items():
                    regions_with_percentage["regionen"][region] = {
                        "umsatz": value,
                        "anteil": round((value / total_revenue * 100), 2)
                        if total_revenue
                        else 0,
                    }

                result["regionen"]["jährlich"].append(regions_with_percentage)

        return result
