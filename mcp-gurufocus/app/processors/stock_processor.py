"""
Prozessor für Aktienübersichtsdaten.
"""

from typing import Dict, Any

class StockProcessor:
    """Verarbeitet Aktienübersichtsdaten."""
    
    @staticmethod
    def process_stock_summary(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet den Aktienüberblick und extrahiert wichtige Informationen.
        
        Args:
            data: Original-API-Antwort von get_stock_summary
            
        Returns:
            Dict mit komprimierten, wesentlichen Daten
        """
        if not data or not isinstance(data, dict):
            return {"error": "Keine gültigen Daten verfügbar"}
        
        # Extrahieren der wichtigsten allgemeinen Informationen
        general = data.get("summary", {}).get("general", {})
        
        # Erstellen eines vereinfachten Dictionaries mit den wichtigsten Werten
        result = {
            "allgemein": {
                "firma": general.get("company", ""),
                "preis": general.get("price", 0),
                "währung": general.get("currency", "$"),
                "gf_score": general.get("gf_score", ""),
                "bewertung": general.get("gf_valuation", ""),
                "sektor": general.get("sector", ""),
                "branche": general.get("group", ""),
                "unterbranche": general.get("subindustry", ""),
                "land": general.get("country", ""),
                "risikobewertung": general.get("risk_assessment", "")
            }
        }
        
        # Wichtige Kennzahlen
        ratio_data = data.get("summary", {}).get("ratio", {})
        result["kennzahlen"] = {
            "pe_ttm": StockProcessor.extract_ratio_value(ratio_data, "P/E(ttm)"),
            "forward_pe": StockProcessor.extract_ratio_value(ratio_data, "Forward P/E"),
            "ps": StockProcessor.extract_ratio_value(ratio_data, "P/S"),
            "pb": StockProcessor.extract_ratio_value(ratio_data, "P/B"),
            "ebitda_marge": StockProcessor.extract_ratio_value(ratio_data, "Operating margin (%)"),
            "netto_marge": StockProcessor.extract_ratio_value(ratio_data, "Net-margin (%)"),
            "roe": StockProcessor.extract_ratio_value(ratio_data, "ROE (%)"),
            "roa": StockProcessor.extract_ratio_value(ratio_data, "ROA (%)"),
            "roic": StockProcessor.extract_ratio_value(ratio_data, "ROIC (%)"),
            "schulden_zu_ebitda": StockProcessor.extract_ratio_value(ratio_data, "Debt-to-Ebitda"),
            "current_ratio": StockProcessor.extract_ratio_value(ratio_data, "Current Ratio"),
            "dividend_yield": StockProcessor.extract_ratio_value(ratio_data, "Dividend Yield"),
            "free_cashflow_yield": data.get("summary", {}).get("company_data", {}).get("FCFyield", 0),
        }
        
        # Wachstumskennzahlen
        company_data = data.get("summary", {}).get("company_data", {})
        result["wachstum"] = {
            "umsatz_wachstum_1y": company_data.get("rvn_growth_1y", 0),
            "umsatz_wachstum_3y": company_data.get("rvn_growth_3y", 0),
            "umsatz_wachstum_5y": company_data.get("rvn_growth_5y", 0),
            "gewinn_wachstum_1y": company_data.get("earning_growth_1y", 0),
            "gewinn_wachstum_3y": company_data.get("earning_growth_3y", 0),
            "gewinn_wachstum_5y": company_data.get("earning_growth_5y", 0),
            "cashflow_wachstum_1y": company_data.get("cashflow_growth_1y", 0),
            "cashflow_wachstum_3y": company_data.get("cashflow_growth_3y", 0),
            "cashflow_wachstum_5y": company_data.get("cashflow_growth_5y", 0),
        }
        
        # Bewertungskennzahlen
        chart_data = data.get("summary", {}).get("chart", {})
        result["bewertung"] = {
            "gf_value": chart_data.get("GF Value", 0),
            "dcf_fcf": chart_data.get("DCF (FCF Based)", 0),
            "dcf_earnings": chart_data.get("DCF (Earnings Based)", 0),
            "peter_lynch_value": chart_data.get("Peter Lynch Value", 0),
        }
        
        return result

    @staticmethod
    def extract_ratio_value(ratio_data: Dict[str, Any], key: str) -> float:
        """
        Extrahiert den Wert aus einem Ratio-Dictionary-Eintrag.
        
        Args:
            ratio_data: Das Ratio-Dictionary
            key: Der Schlüssel für den zu extrahierenden Wert
            
        Returns:
            Der extrahierte Wert als float
        """
        if key in ratio_data:
            try:
                return float(ratio_data[key].get("value", 0))
            except (ValueError, TypeError):
                return 0
        return 0
