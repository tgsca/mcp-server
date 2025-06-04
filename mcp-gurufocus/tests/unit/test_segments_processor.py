"""
Tests for the SegmentsProcessor.
"""

from app.processors.segments_processor import SegmentsProcessor


class TestSegmentsProcessor:
    """Test cases for SegmentsProcessor."""

    def test_process_segments_data_success(self, mock_segments_response):
        """Test successful processing of segments data."""
        result = SegmentsProcessor.process_segments_data(mock_segments_response)

        assert "geschäftsbereiche" in result
        assert "regionen" in result

        # Check business segments structure
        business = result["geschäftsbereiche"]
        assert "jährlich" in business
        assert "ttm" in business
        assert len(business["jährlich"]) == 2  # 2023 and 2022

        # Test annual business data
        annual_2023 = business["jährlich"][0]
        assert annual_2023["jahr"] == "2023"
        assert annual_2023["total"] == 383285000000  # Sum of all segments
        assert "iPhone" in annual_2023["segmente"]
        assert annual_2023["segmente"]["iPhone"]["umsatz"] == 200583000000
        # Check percentage calculation
        expected_iphone_percentage = round(200583000000 / 383285000000 * 100, 2)
        assert annual_2023["segmente"]["iPhone"]["anteil"] == expected_iphone_percentage

        # Test TTM business data
        ttm_data = business["ttm"]
        assert ttm_data["zeitraum"] == "TTM 2024-Q1"
        assert ttm_data["total"] == 362692000000  # Sum of TTM segments
        assert "iPhone" in ttm_data["segmente"]
        assert ttm_data["segmente"]["iPhone"]["umsatz"] == 189968000000

        # Check geographic segments
        regions = result["regionen"]
        assert "jährlich" in regions
        assert len(regions["jährlich"]) == 2  # 2023 and 2022

        # Test annual geographic data
        geo_2023 = regions["jährlich"][0]
        assert geo_2023["jahr"] == "2023"
        assert "Americas" in geo_2023["regionen"]
        assert geo_2023["regionen"]["Americas"]["umsatz"] == 162560000000

    def test_process_segments_data_empty_data(self):
        """Test handling of empty data."""
        result = SegmentsProcessor.process_segments_data({})

        assert "error" in result
        assert "Keine gültigen Daten verfügbar" in result["error"]

    def test_process_segments_data_none_data(self):
        """Test handling of None data."""
        result = SegmentsProcessor.process_segments_data(None)

        assert "error" in result
        assert "Keine gültigen Daten verfügbar" in result["error"]

    def test_process_segments_data_invalid_data_type(self):
        """Test handling of invalid data type."""
        result = SegmentsProcessor.process_segments_data("invalid")

        assert "error" in result
        assert "Keine gültigen Daten verfügbar" in result["error"]

    def test_process_segments_data_missing_business_segments(self):
        """Test handling of data without business segments."""
        data = {"geographical_segments": {"Americas": {"2023": 100000000000}}}
        result = SegmentsProcessor.process_segments_data(data)

        # Should handle missing business segments gracefully
        assert "geschäftsbereiche" in result
        assert "regionen" in result

    def test_process_segments_data_business_only(self):
        """Test processing with only business segments."""
        data = {
            "business": {
                "annual": [
                    {"date": "2023", "Product A": 100000000, "Product B": 50000000}
                ]
            }
        }
        result = SegmentsProcessor.process_segments_data(data)

        business = result["geschäftsbereiche"]
        assert len(business["jährlich"]) == 1
        annual = business["jährlich"][0]
        assert annual["total"] == 150000000
        assert annual["segmente"]["Product A"]["anteil"] == 66.67
        assert annual["segmente"]["Product B"]["anteil"] == 33.33

    def test_process_segments_data_geographic_only(self):
        """Test processing with only geographic segments."""
        data = {
            "geographic": {
                "annual": [
                    {
                        "date": "2023",
                        "North America": 80000000,
                        "Europe": 60000000,
                        "Asia": 40000000,
                    }
                ]
            }
        }
        result = SegmentsProcessor.process_segments_data(data)

        regions = result["regionen"]
        assert len(regions["jährlich"]) == 1
        annual = regions["jährlich"][0]
        assert annual["total"] == 180000000
        assert annual["regionen"]["North America"]["anteil"] == 44.44
        assert annual["regionen"]["Europe"]["anteil"] == 33.33
        assert annual["regionen"]["Asia"]["anteil"] == 22.22

    def test_process_segments_data_ttm_only(self):
        """Test processing with only TTM business data."""
        data = {
            "business": {
                "ttm": [
                    {"date": "TTM 2024", "Product A": 120000000, "Product B": 80000000}
                ]
            }
        }
        result = SegmentsProcessor.process_segments_data(data)

        ttm_data = result["geschäftsbereiche"]["ttm"]
        assert ttm_data["zeitraum"] == "TTM 2024"
        assert ttm_data["total"] == 200000000
        assert ttm_data["segmente"]["Product A"]["umsatz"] == 120000000
        assert ttm_data["segmente"]["Product A"]["anteil"] == 60.0

    def test_process_segments_data_zero_division_handling(self):
        """Test handling of zero total revenue (division by zero)."""
        data = {
            "business": {"annual": [{"date": "2023", "Product A": 0, "Product B": 0}]}
        }
        result = SegmentsProcessor.process_segments_data(data)

        annual = result["geschäftsbereiche"]["jährlich"][0]
        assert annual["total"] == 0
        assert annual["segmente"]["Product A"]["anteil"] == 0
        assert annual["segmente"]["Product B"]["anteil"] == 0

    def test_process_segments_data_missing_date(self):
        """Test handling of missing date field."""
        data = {
            "business": {
                "annual": [
                    {
                        "Product A": 100000000,
                        "Product B": 50000000,
                        # Missing date field
                    }
                ]
            }
        }
        result = SegmentsProcessor.process_segments_data(data)

        # Should not process entry without date
        assert len(result["geschäftsbereiche"]["jährlich"]) == 0

    def test_process_segments_data_empty_ttm_list(self):
        """Test handling of empty TTM list."""
        data = {"business": {"ttm": []}}
        result = SegmentsProcessor.process_segments_data(data)

        # TTM should remain as empty dict when no data
        assert result["geschäftsbereiche"]["ttm"] == {}

    def test_process_segments_data_missing_geographical_segments(self):
        """Test handling of data without geographical segments."""
        data = {"business_segments": {"iPhone": {"2023": 200000000000}}}
        result = SegmentsProcessor.process_segments_data(data)

        # Should handle missing geographical segments gracefully
        assert "geschäftsbereiche" in result
        assert "regionen" in result

    def test_process_segments_data_partial_data(self):
        """Test handling of partial segments data."""
        data = {
            "business_segments": {
                "iPhone": {
                    "2023": 200000000000
                    # Missing 2022
                }
            }
        }
        result = SegmentsProcessor.process_segments_data(data)

        assert "geschäftsbereiche" in result
        assert "regionen" in result
