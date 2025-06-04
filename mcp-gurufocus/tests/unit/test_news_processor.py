"""
Tests for the NewsProcessor.
"""

from app.processors.news_processor import NewsProcessor


class TestNewsProcessor:
    """Test cases for NewsProcessor."""

    def test_process_news_headlines_success(self, mock_news_response):
        """Test successful processing of news headlines."""
        result = NewsProcessor.process_news_headlines(mock_news_response)
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        # Check news item structure (returns processed format)
        first_news = result[0]
        assert "datum" in first_news
        assert "überschrift" in first_news  
        assert "url" in first_news

    def test_process_news_headlines_empty_data(self):
        """Test handling of empty data."""
        result = NewsProcessor.process_news_headlines({})
        
        assert isinstance(result, list)
        # Should return empty list or error message

    def test_process_news_headlines_none_data(self):
        """Test handling of None data."""
        result = NewsProcessor.process_news_headlines(None)
        
        assert isinstance(result, list)
        # Should handle None gracefully

    def test_process_news_headlines_list_input(self):
        """Test handling of list input (alternative format)."""
        news_list = [
            {
                "title": "Apple News 1",
                "date": "2024-01-15",
                "url": "https://example.com/1"
            },
            {
                "title": "Apple News 2", 
                "date": "2024-01-14",
                "url": "https://example.com/2"
            }
        ]
        
        result = NewsProcessor.process_news_headlines(news_list)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert "datum" in result[0]
        assert "überschrift" in result[0]
        assert "url" in result[0]

    def test_process_news_headlines_string_input(self):
        """Test handling of string input."""
        result = NewsProcessor.process_news_headlines("some string")
        
        assert isinstance(result, list)
        # Should handle string input gracefully

    def test_process_news_headlines_missing_news_key(self):
        """Test handling of data without news key."""
        data = {"other_data": "value"}
        result = NewsProcessor.process_news_headlines(data)
        
        assert isinstance(result, list)
        # Should handle missing news key gracefully

    def test_process_news_headlines_empty_news_list(self):
        """Test handling of empty news list."""
        data = {"news": []}
        result = NewsProcessor.process_news_headlines(data)
        
        assert isinstance(result, list)
        # Empty news list may still return a default empty item
        assert isinstance(result, list)

    def test_process_news_headlines_malformed_news_items(self):
        """Test handling of malformed news items."""
        data = {
            "news": [
                {"title": "Complete News"},  # Missing date and url
                {"date": "2024-01-15"},      # Missing title and url
                {                            # Missing all fields
                    "unexpected_field": "value"
                }
            ]
        }
        
        result = NewsProcessor.process_news_headlines(data)
        
        assert isinstance(result, list)
        # Should handle malformed items gracefully

    def test_process_news_headlines_json_string_input(self):
        """Test handling of JSON string input."""
        json_string = '[{"date": "2024-01-15", "headline": "Test News 1", "url": "http://test1.com"}, {"date": "2024-01-14", "headline": "Test News 2", "url": "http://test2.com"}]'
        
        result = NewsProcessor.process_news_headlines(json_string)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["datum"] == "2024-01-15"
        assert result[0]["überschrift"] == "Test News 1"
        assert result[0]["url"] == "http://test1.com"
        # Should be sorted by date (newest first)
        assert result[0]["datum"] >= result[1]["datum"]

    def test_process_news_headlines_multiple_json_objects_string(self):
        """Test handling of multiple JSON objects in string format."""
        json_objects_string = '{"date": "2024-01-15", "headline": "News 1", "url": "http://test1.com"}{"date": "2024-01-14", "headline": "News 2", "url": "http://test2.com"}'
        
        result = NewsProcessor.process_news_headlines(json_objects_string)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["datum"] == "2024-01-15"
        assert result[0]["überschrift"] == "News 1"
        assert result[1]["datum"] == "2024-01-14"
        assert result[1]["überschrift"] == "News 2"

    def test_process_news_headlines_invalid_json_string(self):
        """Test handling of invalid JSON string."""
        invalid_json = '{"invalid": json string'
        
        result = NewsProcessor.process_news_headlines(invalid_json)
        
        assert isinstance(result, list)
        # Should return error message or empty result
        if len(result) > 0:
            assert "error" in result[0] or result == []

    def test_process_news_headlines_json_decode_error(self):
        """Test handling of JSON decode errors."""
        invalid_json = 'not json at all'
        
        result = NewsProcessor.process_news_headlines(invalid_json)
        
        assert isinstance(result, list)
        # Should handle decode error gracefully

    def test_process_news_headlines_partial_json_objects(self):
        """Test handling of partially malformed JSON objects."""
        partial_json = '{"date": "2024-01-15", "headline": "News 1"}{"invalid": malformed}{"date": "2024-01-14", "headline": "News 2", "url": "http://test.com"}'
        
        result = NewsProcessor.process_news_headlines(partial_json)
        
        assert isinstance(result, list)
        # Should process valid objects and skip invalid ones
        valid_items = [item for item in result if "error" not in item]
        assert len(valid_items) >= 1  # At least some valid items should be processed

    def test_process_news_headlines_exception_handling(self):
        """Test general exception handling."""
        # Test with an object that might cause unexpected errors
        problematic_input = {"unexpected": "structure", "that": {"might": "cause issues"}}
        
        result = NewsProcessor.process_news_headlines(problematic_input)
        
        assert isinstance(result, list)
        # Should handle unexpected inputs gracefully

    def test_process_news_headlines_no_headlines_found(self):
        """Test when no headlines are found."""
        empty_string = ""
        
        result = NewsProcessor.process_news_headlines(empty_string)
        
        assert isinstance(result, list)
        # Should handle empty input gracefully

    def test_process_news_headlines_sorting(self):
        """Test that headlines are sorted by date (newest first)."""
        data = [
            {"date": "2024-01-10", "headline": "Older News"},
            {"date": "2024-01-15", "headline": "Newer News"},
            {"date": "2024-01-12", "headline": "Middle News"}
        ]
        
        result = NewsProcessor.process_news_headlines(data)
        
        assert isinstance(result, list)
        assert len(result) == 3
        # Should be sorted by date (newest first)
        dates = [item["datum"] for item in result if item["datum"]]
        if len(dates) > 1:
            assert dates == sorted(dates, reverse=True)

    def test_process_news_headlines_missing_fields(self):
        """Test handling of news items with missing fields."""
        data = [
            {"headline": "Only headline"},  # Missing date and url
            {"date": "2024-01-15", "url": "http://test.com"},  # Missing headline
            {"date": "2024-01-14", "headline": "Complete item", "url": "http://test2.com"}
        ]
        
        result = NewsProcessor.process_news_headlines(data)
        
        assert isinstance(result, list)
        assert len(result) == 3
        # Should handle missing fields gracefully with empty strings
        # Check that the data is processed (list items are processed in order)
        headline_only_item = next(item for item in result if item["überschrift"] == "Only headline")
        assert headline_only_item["datum"] == ""
        assert headline_only_item["überschrift"] == "Only headline"
        assert headline_only_item["url"] == ""