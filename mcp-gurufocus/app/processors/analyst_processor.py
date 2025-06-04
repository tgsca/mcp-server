"""
Prozessor für Analystenschätzungen.
"""

from typing import Dict, Any


class AnalystProcessor:
    """Verarbeitet Analystenschätzungen."""

    @staticmethod
    def process_analyst_estimates(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet die Analystenschätzungen und extrahiert wichtige Informationen.

        Args:
            data: Original-API-Antwort von get_analyst_estimates

        Returns:
            Dict mit komprimierten, wesentlichen Daten
        """
        if not data or not isinstance(data, dict):
            return {"error": "Keine gültigen Daten verfügbar"}

        result = {"jährlich": {}, "quartal": {}, "wachstumsraten": {}}

        # Jährliche Daten
        annual = data.get("annual", {})
        if annual:
            # Jahresdaten extrahieren
            dates = annual.get("date", [])

            # Für jedes Jahr die wichtigsten Metriken in ein neues Dictionary aufnehmen
            annual_data = {}
            for i, date in enumerate(dates):
                annual_data[date] = {
                    "umsatz": AnalystProcessor.get_value_at_index(
                        annual, "revenue_estimate", i
                    ),
                    "nettogewinn": AnalystProcessor.get_value_at_index(
                        annual, "net_income_estimate", i
                    ),
                    "eps": AnalystProcessor.get_value_at_index(
                        annual, "per_share_eps_estimate", i
                    ),
                    "dividende": AnalystProcessor.get_value_at_index(
                        annual, "dividend_estimate", i
                    ),
                    "roe": AnalystProcessor.get_value_at_index(
                        annual, "roe_estimate", i
                    ),
                    "bruttomarge": AnalystProcessor.get_value_at_index(
                        annual, "gross_margin_estimate", i
                    ),
                }

            result["jährlich"] = annual_data

        # Quartalsdaten - nur die nächsten 4 Quartale
        quarterly = data.get("quarterly", {})
        if quarterly:
            dates = quarterly.get("date", [])

            # Auf die nächsten 4 Quartale beschränken
            quarters_to_include = min(4, len(dates))
            quarterly_data = {}

            for i in range(quarters_to_include):
                quarterly_data[dates[i]] = {
                    "umsatz": AnalystProcessor.get_value_at_index(
                        quarterly, "revenue_estimate", i
                    ),
                    "nettogewinn": AnalystProcessor.get_value_at_index(
                        quarterly, "net_income_estimate", i
                    ),
                    "eps": AnalystProcessor.get_value_at_index(
                        quarterly, "per_share_eps_estimate", i
                    ),
                }

            result["quartal"] = quarterly_data

        # Langfristige Wachstumsraten
        growth_fields = [
            k
            for k in annual.keys()
            if k.startswith("future_") and k.endswith("_growth")
        ]
        for field in growth_fields:
            display_name = (
                field.replace("future_", "")
                .replace("_estimate_growth", "")
                .replace("_", " ")
            )
            result["wachstumsraten"][display_name] = annual.get(field, 0)

        return result

    @staticmethod
    def get_value_at_index(data: Dict[str, Any], key: str, index: int) -> Any:
        """
        Hilfsfunktion, um Werte an einem bestimmten Index aus einer Liste zu holen.

        Args:
            data: Das Dictionary mit den Daten
            key: Der Schlüssel für die zu extrahierende Liste
            index: Der Index innerhalb der Liste

        Returns:
            Der Wert an der angegebenen Position oder None
        """
        values = data.get(key, [])
        if index < len(values):
            try:
                return float(values[index])
            except (ValueError, TypeError):
                return values[index]
        return None
