"""
Generator für zusammenfassende Berichte.
"""

from typing import Dict, Any, List
from datetime import datetime


class ReportGenerator:
    """Generiert zusammenfassende Berichte aus verarbeiteten Daten."""

    @staticmethod
    def generate_summary_report(
        summary: Dict[str, Any],
        estimates: Dict[str, Any],
        segments: Dict[str, Any],
        news: List[Dict[str, str]],
        symbol: str,
    ) -> Dict[str, Any]:
        """
        Erstellt einen zusammenfassenden Bericht aus allen verarbeiteten Daten.

        Args:
            summary: Verarbeitete Summary-Daten
            estimates: Verarbeitete Analystenschätzungen
            segments: Verarbeitete Segmentdaten
            news: Verarbeitete Nachrichtenüberschriften
            symbol: Das Aktiensymbol

        Returns:
            Dict mit dem umfassenden Bericht
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = {
            "erstellt_am": now,
            "firma": summary.get("allgemein", {}).get("firma", ""),
            "symbol": symbol,
            "aktueller_preis": summary.get("allgemein", {}).get("preis", 0),
            "währung": summary.get("allgemein", {}).get("währung", "$"),
            "kernkennzahlen": {
                "pe_ttm": summary.get("kennzahlen", {}).get("pe_ttm", 0),
                "forward_pe": summary.get("kennzahlen", {}).get("forward_pe", 0),
                "roe": summary.get("kennzahlen", {}).get("roe", 0),
                "roa": summary.get("kennzahlen", {}).get("roa", 0),
                "netto_marge": summary.get("kennzahlen", {}).get("netto_marge", 0),
                "dividend_yield": summary.get("kennzahlen", {}).get(
                    "dividend_yield", 0
                ),
                "free_cashflow_yield": summary.get("kennzahlen", {}).get(
                    "free_cashflow_yield", 0
                ),
            },
            "bewertung": {
                "status": summary.get("allgemein", {}).get("bewertung", ""),
                "aktueller_preis": summary.get("allgemein", {}).get("preis", 0),
                "gf_value": summary.get("bewertung", {}).get("gf_value", 0),
                "dcf_wert": summary.get("bewertung", {}).get("dcf_earnings", 0),
            },
            "wachstumsaussichten": {
                "umsatz_wachstum_prognose": estimates.get("wachstumsraten", {}).get(
                    "revenue", 0
                ),
                "gewinn_wachstum_prognose": estimates.get("wachstumsraten", {}).get(
                    "per share eps", 0
                ),
                "eps_prognose_nächstes_jahr": next(
                    iter(estimates.get("jährlich", {}).values()), {}
                ).get("eps", 0),
            },
            "umsatzstruktur": {
                "hauptprodukte": {},  # Wird unten befüllt
                "hauptregionen": {},  # Wird unten befüllt
            },
            "aktuelle_nachrichten": news[:5],  # Nur die neuesten 5 Nachrichten
        }

        # Hauptprodukte aus dem TTM-Segment extrahieren
        ttm_segments = (
            segments.get("geschäftsbereiche", {}).get("ttm", {}).get("segmente", {})
        )
        if ttm_segments:
            # Nach Umsatz sortieren und Top-Segmente auswählen
            sorted_segments = sorted(
                ttm_segments.items(), key=lambda x: x[1].get("umsatz", 0), reverse=True
            )
            for segment, data in sorted_segments:
                report["umsatzstruktur"]["hauptprodukte"][segment] = {
                    "umsatz": data.get("umsatz", 0),
                    "anteil": data.get("anteil", 0),
                }

        # Hauptregionen aus dem letzten Jahr extrahieren
        regions_annual = segments.get("regionen", {}).get("jährlich", [])
        if regions_annual:
            # Das neueste Jahr nehmen
            latest_regions = regions_annual[-1]
            regions = latest_regions.get("regionen", {})

            # Nach Umsatz sortieren und Top-Regionen auswählen
            sorted_regions = sorted(
                regions.items(), key=lambda x: x[1].get("umsatz", 0), reverse=True
            )
            for region, data in sorted_regions:
                report["umsatzstruktur"]["hauptregionen"][region] = {
                    "umsatz": data.get("umsatz", 0),
                    "anteil": data.get("anteil", 0),
                }

        return report
