"""
Prozessor für Finanzdaten von GuruFocus.
"""

from typing import Dict, Any, List, Optional, Tuple, Union

class FinancialsProcessor:
    """Verarbeitet detaillierte Finanzdaten von Unternehmen aus der GuruFocus API."""
    
    @staticmethod
    def process_stock_financials(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet die Finanzdaten und extrahiert wichtige Informationen.
        
        Args:
            data: Original-API-Antwort von get_stock_financials
            
        Returns:
            Dict mit komprimierten, wesentlichen Finanzdaten
        """
        if not data or not isinstance(data, dict):
            return {"error": "Keine gültigen Finanzdaten verfügbar"}
        
        # Basis-Informationen
        financials_data = data.get("financials", {})
        template_params = financials_data.get("financial_template_parameters", {})
        
        # Prüfen auf REIT
        is_reit = template_params.get("REITs", "N") == "Y"
        
        # Daten aus jährlichen Abschlüssen
        annuals = financials_data.get("annuals", {})
        
        # Extrahiere die Perioden
        periods = annuals.get("Fiscal Year", [])
        
        # Ausgabe-Struktur erstellen
        result = {
            "is_reit": is_reit,
            "jahresabschlüsse": {
                "perioden": FinancialsProcessor._clean_periods(periods),
                "per_share_data": FinancialsProcessor._process_per_share_data(annuals),
                "income_statement": FinancialsProcessor._process_income_statement(annuals),
                "balance_sheet": FinancialsProcessor._process_balance_sheet(annuals),
                "cashflow_statement": FinancialsProcessor._process_cashflow_statement(annuals)
            },
            # "kennzahlen": {
            #     "rentabilität": FinancialsProcessor._process_profitability_ratios(annuals),
            #     "wachstum": FinancialsProcessor._process_growth_ratios(annuals),
            #     "cashflow": FinancialsProcessor._process_cashflow_ratios(annuals),
            #     "finanzkraft": FinancialsProcessor._process_financial_strength_ratios(annuals),
            #     "effizienz": FinancialsProcessor._process_efficiency_ratios(annuals),
            #     "bewertung": FinancialsProcessor._process_valuation_ratios(annuals)
            # }
        }
        
        # Quartalsweise Daten, falls vorhanden
        # quarterly = financials_data.get("quarterly", {})
        # if quarterly:
        #     quarterly_periods = quarterly.get("Fiscal Year", [])
        #     result["quartalsabschlüsse"] = {
        #         "perioden": FinancialsProcessor._clean_periods(quarterly_periods),
        #         "income_statement": FinancialsProcessor._process_income_statement(quarterly),
        #         "balance_sheet": FinancialsProcessor._process_balance_sheet(quarterly),
        #         "cashflow_statement": FinancialsProcessor._process_cashflow_statement(quarterly)
        #     }
        
        return result
    
    @staticmethod
    def _clean_periods(periods: List[str]) -> List[str]:
        """
        Bereinigt die Periodenangaben.
        
        Args:
            periods: Liste der Periodenangaben
            
        Returns:
            Bereinigte Liste der Periodenangaben
        """
        # Maximal 10 Perioden zurückgeben
        return periods[:10] if periods else []
    
    @staticmethod
    def _filter_data(section: Dict[str, List], exclude_keys: List[str] = None) -> Dict[str, List]:
        """
        Filtert Daten und entfernt unerwünschte Schlüssel.
        
        Args:
            section: Zu filternde Daten
            exclude_keys: Liste von Schlüsseln, die ausgeschlossen werden sollen
            
        Returns:
            Gefilterte Daten
        """
        if not exclude_keys:
            exclude_keys = ["Fiscal Year", "Preliminary"]
        else:
            exclude_keys.extend(["Fiscal Year", "Preliminary"])
            
        # Maximal 10 Perioden für jeden Wert berücksichtigen
        filtered_data = {}
        for key, values in section.items():
            if key not in exclude_keys and isinstance(values, list):
                filtered_data[key] = values[:10]
                
        return filtered_data
    
    @staticmethod
    def _process_per_share_data(annuals: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Pro-Aktie-Daten.
        
        Args:
            annuals: Die jährlichen Finanzdaten
            
        Returns:
            Verarbeitete Pro-Aktie-Daten
        """
        per_share_data = annuals.get("Per Share Data", {})
        return FinancialsProcessor._filter_data(per_share_data)
    
    @staticmethod
    def _process_income_statement(data: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Gewinn- und Verlustrechnung.
        
        Args:
            data: Die Finanzdaten
            
        Returns:
            Verarbeitete Gewinn- und Verlustrechnung
        """
        income_statement = data.get("Income Statement", {})
        return FinancialsProcessor._filter_data(income_statement)
    
    @staticmethod
    def _process_balance_sheet(data: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Bilanz.
        
        Args:
            data: Die Finanzdaten
            
        Returns:
            Verarbeitete Bilanzdaten
        """
        balance_sheet = data.get("Balance Sheet", {})
        return FinancialsProcessor._filter_data(balance_sheet)
    
    @staticmethod
    def _process_cashflow_statement(data: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Kapitalflussrechnung.
        
        Args:
            data: Die Finanzdaten
            
        Returns:
            Verarbeitete Kapitalflussdaten
        """
        cashflow_statement = data.get("Cash Flow", {})
        return FinancialsProcessor._filter_data(cashflow_statement)
    
    @staticmethod
    def _process_profitability_ratios(data: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Rentabilitätskennzahlen.
        
        Args:
            data: Die Finanzdaten
            
        Returns:
            Verarbeitete Rentabilitätskennzahlen
        """
        profitability = data.get("Profitability", {})
        return FinancialsProcessor._filter_data(profitability)
    
    @staticmethod
    def _process_growth_ratios(data: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Wachstumskennzahlen.
        
        Args:
            data: Die Finanzdaten
            
        Returns:
            Verarbeitete Wachstumskennzahlen
        """
        growth = data.get("Growth", {})
        return FinancialsProcessor._filter_data(growth)
    
    @staticmethod
    def _process_cashflow_ratios(data: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Cashflow-Kennzahlen.
        
        Args:
            data: Die Finanzdaten
            
        Returns:
            Verarbeitete Cashflow-Kennzahlen
        """
        cashflow = data.get("Cash Flow Ratios", {})
        return FinancialsProcessor._filter_data(cashflow)
    
    @staticmethod
    def _process_financial_strength_ratios(data: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Finanzkraftkennzahlen.
        
        Args:
            data: Die Finanzdaten
            
        Returns:
            Verarbeitete Finanzkraftkennzahlen
        """
        financial_strength = data.get("Financial Strength", {})
        return FinancialsProcessor._filter_data(financial_strength)
    
    @staticmethod
    def _process_efficiency_ratios(data: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Effizienzkennzahlen.
        
        Args:
            data: Die Finanzdaten
            
        Returns:
            Verarbeitete Effizienzkennzahlen
        """
        efficiency = data.get("Efficiency", {})
        return FinancialsProcessor._filter_data(efficiency)
    
    @staticmethod
    def _process_valuation_ratios(data: Dict[str, Any]) -> Dict[str, List]:
        """
        Verarbeitet die Bewertungskennzahlen.
        
        Args:
            data: Die Finanzdaten
            
        Returns:
            Verarbeitete Bewertungskennzahlen
        """
        valuation = data.get("Valuation Ratios", {})
        return FinancialsProcessor._filter_data(valuation)
