"""
Tests for the ReportGenerator.
"""

from datetime import datetime
from unittest.mock import patch
from app.processors.report_generator import ReportGenerator


class TestReportGenerator:
    """Test cases for ReportGenerator."""

    def test_generate_summary_report_success(self):
        """Test successful generation of summary report."""
        # Mock data
        summary = {
            "allgemein": {
                "firma": "Apple Inc",
                "preis": 150.25,
                "währung": "$",
                "bewertung": "Fairly Valued"
            },
            "kennzahlen": {
                "pe_ttm": 25.5,
                "forward_pe": 22.1,
                "roe": 28.5,
                "roa": 15.2,
                "netto_marge": 23.4,
                "dividend_yield": 0.65,
                "free_cashflow_yield": 3.2
            },
            "bewertung": {
                "gf_value": 140.5,
                "dcf_earnings": 145.2
            }
        }
        
        estimates = {
            "jährlich": {
                "2024": {"eps": 6.15},
                "2025": {"eps": 6.85}
            },
            "wachstumsraten": {
                "revenue": 8.5,
                "per share eps": 12.2
            }
        }
        
        segments = {
            "geschäftsbereiche": {
                "ttm": {
                    "segmente": {
                        "iPhone": {"umsatz": 189968000000, "anteil": 52.4},
                        "Services": {"umsatz": 85500000000, "anteil": 23.6},
                        "Mac": {"umsatz": 24943000000, "anteil": 6.9}
                    }
                }
            },
            "regionen": {
                "jährlich": [
                    {
                        "jahr": "2023",
                        "regionen": {
                            "Americas": {"umsatz": 162560000000, "anteil": 42.4},
                            "Europe": {"umsatz": 94294000000, "anteil": 24.6},
                            "Greater China": {"umsatz": 72559000000, "anteil": 18.9}
                        }
                    }
                ]
            }
        }
        
        news = [
            {"titel": "Apple Q4 Results", "datum": "2024-01-15"},
            {"titel": "New iPhone Launch", "datum": "2024-01-14"}
        ]
        
        with patch('app.processors.report_generator.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-15 10:30:00"
            
            result = ReportGenerator.generate_summary_report(
                summary, estimates, segments, news, "AAPL"
            )
        
        # Test basic report structure
        assert result["erstellt_am"] == "2024-01-15 10:30:00"
        assert result["firma"] == "Apple Inc"
        assert result["symbol"] == "AAPL"
        assert result["aktueller_preis"] == 150.25
        assert result["währung"] == "$"
        
        # Test core metrics
        kernkennzahlen = result["kernkennzahlen"]
        assert kernkennzahlen["pe_ttm"] == 25.5
        assert kernkennzahlen["forward_pe"] == 22.1
        assert kernkennzahlen["roe"] == 28.5
        assert kernkennzahlen["roa"] == 15.2
        assert kernkennzahlen["netto_marge"] == 23.4
        assert kernkennzahlen["dividend_yield"] == 0.65
        assert kernkennzahlen["free_cashflow_yield"] == 3.2
        
        # Test valuation
        bewertung = result["bewertung"]
        assert bewertung["status"] == "Fairly Valued"
        assert bewertung["aktueller_preis"] == 150.25
        assert bewertung["gf_value"] == 140.5
        assert bewertung["dcf_wert"] == 145.2
        
        # Test growth prospects
        wachstum = result["wachstumsaussichten"]
        assert wachstum["umsatz_wachstum_prognose"] == 8.5
        assert wachstum["gewinn_wachstum_prognose"] == 12.2
        assert wachstum["eps_prognose_nächstes_jahr"] == 6.15  # First year's EPS
        
        # Test revenue structure - products
        hauptprodukte = result["umsatzstruktur"]["hauptprodukte"]
        assert "iPhone" in hauptprodukte
        assert hauptprodukte["iPhone"]["umsatz"] == 189968000000
        assert hauptprodukte["iPhone"]["anteil"] == 52.4
        assert "Services" in hauptprodukte
        assert "Mac" in hauptprodukte
        
        # Test revenue structure - regions
        hauptregionen = result["umsatzstruktur"]["hauptregionen"]
        assert "Americas" in hauptregionen
        assert hauptregionen["Americas"]["umsatz"] == 162560000000
        assert hauptregionen["Americas"]["anteil"] == 42.4
        
        # Test news (limited to 5)
        assert len(result["aktuelle_nachrichten"]) == 2
        assert result["aktuelle_nachrichten"][0]["titel"] == "Apple Q4 Results"

    def test_generate_summary_report_missing_data(self):
        """Test report generation with missing data."""
        summary = {}
        estimates = {}
        segments = {}
        news = []
        
        with patch('app.processors.report_generator.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-15 10:30:00"
            
            result = ReportGenerator.generate_summary_report(
                summary, estimates, segments, news, "TEST"
            )
        
        # Should handle missing data gracefully
        assert result["firma"] == ""
        assert result["symbol"] == "TEST"
        assert result["aktueller_preis"] == 0
        assert result["währung"] == "$"
        assert result["kernkennzahlen"]["pe_ttm"] == 0
        assert result["bewertung"]["status"] == ""
        assert result["wachstumsaussichten"]["umsatz_wachstum_prognose"] == 0
        assert len(result["umsatzstruktur"]["hauptprodukte"]) == 0
        assert len(result["umsatzstruktur"]["hauptregionen"]) == 0
        assert len(result["aktuelle_nachrichten"]) == 0

    def test_generate_summary_report_partial_segments(self):
        """Test report generation with partial segment data."""
        summary = {"allgemein": {"firma": "Test Corp"}}
        estimates = {}
        segments = {
            "geschäftsbereiche": {
                "ttm": {
                    "segmente": {
                        "Product A": {"umsatz": 100000000, "anteil": 60.0},
                        "Product B": {"umsatz": 66666667, "anteil": 40.0}
                    }
                }
            }
            # Missing regions data
        }
        news = []
        
        result = ReportGenerator.generate_summary_report(
            summary, estimates, segments, news, "TEST"
        )
        
        # Should process available segment data
        hauptprodukte = result["umsatzstruktur"]["hauptprodukte"]
        assert len(hauptprodukte) == 2
        assert "Product A" in hauptprodukte
        assert hauptprodukte["Product A"]["umsatz"] == 100000000
        
        # Should handle missing regions gracefully
        assert len(result["umsatzstruktur"]["hauptregionen"]) == 0

    def test_generate_summary_report_empty_ttm_segments(self):
        """Test report generation with empty TTM segments."""
        summary = {"allgemein": {"firma": "Test Corp"}}
        estimates = {}
        segments = {
            "geschäftsbereiche": {
                "ttm": {}  # Empty TTM data
            },
            "regionen": {
                "jährlich": [
                    {
                        "regionen": {
                            "Region A": {"umsatz": 50000000, "anteil": 100.0}
                        }
                    }
                ]
            }
        }
        news = []
        
        result = ReportGenerator.generate_summary_report(
            summary, estimates, segments, news, "TEST"
        )
        
        # Should handle empty TTM gracefully
        assert len(result["umsatzstruktur"]["hauptprodukte"]) == 0
        
        # Should still process regions
        hauptregionen = result["umsatzstruktur"]["hauptregionen"]
        assert "Region A" in hauptregionen

    def test_generate_summary_report_news_limit(self):
        """Test that news is limited to 5 items."""
        summary = {"allgemein": {"firma": "Test Corp"}}
        estimates = {}
        segments = {}
        news = [
            {"titel": f"News {i}", "datum": f"2024-01-{i:02d}"} 
            for i in range(1, 11)  # 10 news items
        ]
        
        result = ReportGenerator.generate_summary_report(
            summary, estimates, segments, news, "TEST"
        )
        
        # Should limit to 5 news items
        assert len(result["aktuelle_nachrichten"]) == 5
        assert result["aktuelle_nachrichten"][0]["titel"] == "News 1"
        assert result["aktuelle_nachrichten"][4]["titel"] == "News 5"

    def test_generate_summary_report_segment_sorting(self):
        """Test that segments are sorted by revenue (highest first)."""
        summary = {"allgemein": {"firma": "Test Corp"}}
        estimates = {}
        segments = {
            "geschäftsbereiche": {
                "ttm": {
                    "segmente": {
                        "Small Product": {"umsatz": 10000000, "anteil": 10.0},
                        "Large Product": {"umsatz": 80000000, "anteil": 80.0},
                        "Medium Product": {"umsatz": 10000000, "anteil": 10.0}
                    }
                }
            },
            "regionen": {
                "jährlich": [
                    {
                        "regionen": {
                            "Small Region": {"umsatz": 20000000, "anteil": 20.0},
                            "Large Region": {"umsatz": 60000000, "anteil": 60.0},
                            "Medium Region": {"umsatz": 20000000, "anteil": 20.0}
                        }
                    }
                ]
            }
        }
        news = []
        
        result = ReportGenerator.generate_summary_report(
            summary, estimates, segments, news, "TEST"
        )
        
        # Products should be sorted by revenue (highest first)
        product_keys = list(result["umsatzstruktur"]["hauptprodukte"].keys())
        assert product_keys[0] == "Large Product"  # Highest revenue first
        
        # Regions should be sorted by revenue (highest first)
        region_keys = list(result["umsatzstruktur"]["hauptregionen"].keys())
        assert region_keys[0] == "Large Region"  # Highest revenue first

    def test_generate_summary_report_latest_regions_year(self):
        """Test that latest year's regional data is used."""
        summary = {"allgemein": {"firma": "Test Corp"}}
        estimates = {}
        segments = {
            "regionen": {
                "jährlich": [
                    {
                        "jahr": "2022",
                        "regionen": {
                            "Old Region": {"umsatz": 30000000, "anteil": 100.0}
                        }
                    },
                    {
                        "jahr": "2023",
                        "regionen": {
                            "New Region": {"umsatz": 50000000, "anteil": 100.0}
                        }
                    }
                ]
            }
        }
        news = []
        
        result = ReportGenerator.generate_summary_report(
            summary, estimates, segments, news, "TEST"
        )
        
        # Should use the latest year's data (last in list)
        hauptregionen = result["umsatzstruktur"]["hauptregionen"]
        assert "New Region" in hauptregionen
        assert "Old Region" not in hauptregionen
        assert hauptregionen["New Region"]["umsatz"] == 50000000