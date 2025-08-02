"""Tests for the main pseudonymization service."""

import pytest
from unittest.mock import Mock, patch
from src.pseudonymizer import TextPseudonymizer, PseudonymizationResult
from src.error_handling import InvalidInputError

@pytest.fixture
def pseudonymizer():
    """Create a TextPseudonymizer instance for testing."""
    return TextPseudonymizer()

class TestTextPseudonymizer:
    """Test cases for TextPseudonymizer class."""
    
    def test_initialization(self, pseudonymizer):
        """Test that pseudonymizer initializes correctly."""
        assert pseudonymizer.language_detector is not None
        assert pseudonymizer.ner_pipeline is not None
        assert pseudonymizer.pattern_matcher is not None
        assert pseudonymizer.session_manager is not None
    
    @patch('src.pseudonymizer.TextPseudonymizer._replace_entities_in_text')
    @patch('src.ner_pipeline.NERPipeline.extract_entities')
    @patch('src.language_detection.LanguageDetector.detect_language')
    def test_pseudonymize_single_text(self, mock_detect, mock_extract, mock_replace, pseudonymizer):
        """Test pseudonymizing a single text string."""
        # Setup mocks
        mock_detect.return_value = ("de", 0.9)
        mock_extract.return_value = []
        mock_replace.return_value = "Test text with PERSON_1"
        
        # Test
        result = pseudonymizer.pseudonymize_text("Test text with Max Müller")
        
        # Assertions
        assert isinstance(result, PseudonymizationResult)
        assert result.detected_language == "de"
        assert isinstance(result.pseudonymized, str)
        assert result.confidence == 0.9
    
    def test_pseudonymize_empty_text(self, pseudonymizer):
        """Test pseudonymizing empty text."""
        result = pseudonymizer.pseudonymize_text("")
        
        assert result.pseudonymized == ""
        assert result.entity_count == 0
        assert result.detected_language == "en"
    
    def test_pseudonymize_list_of_texts(self, pseudonymizer):
        """Test pseudonymizing a list of texts."""
        with patch.object(pseudonymizer.language_detector, 'detect_language', return_value=("en", 0.8)):
            with patch.object(pseudonymizer.ner_pipeline, 'extract_entities', return_value=[]):
                result = pseudonymizer.pseudonymize_text(["Hello world", "Test text"])
                
                assert isinstance(result.pseudonymized, list)
                assert len(result.pseudonymized) == 2
                assert result.detected_language == "en"
    
    def test_detect_language(self, pseudonymizer):
        """Test language detection."""
        with patch.object(pseudonymizer.language_detector, 'detect_language', return_value=("de", 0.95)):
            result = pseudonymizer.detect_language("Das ist ein deutscher Text")
            
            assert result.language == "de"
            assert result.confidence == 0.95
    
    def test_list_supported_languages(self, pseudonymizer):
        """Test listing supported languages."""
        with patch.object(pseudonymizer.language_detector, 'get_supported_languages', 
                         return_value={"de": {"name": "German", "model": "flair/ner-german"}}):
            result = pseudonymizer.list_supported_languages()
            
            assert "de" in result
            assert result["de"]["name"] == "German"
    
    def test_get_entity_mappings_new_session(self, pseudonymizer):
        """Test getting entity mappings for new session."""
        result = pseudonymizer.get_entity_mappings()
        
        assert "mappings" in result
        assert "statistics" in result
        assert isinstance(result["mappings"], dict)
    
    def test_get_entity_mappings_nonexistent_session(self, pseudonymizer):
        """Test getting entity mappings for non-existent session."""
        result = pseudonymizer.get_entity_mappings("nonexistent-session")
        
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_clear_session(self, pseudonymizer):
        """Test clearing a session."""
        # Create a session first
        pseudonymizer.session_manager.get_or_create_session("test-session")
        
        # Clear it
        result = pseudonymizer.clear_session("test-session")
        assert result is True
        
        # Try to clear non-existent session
        result = pseudonymizer.clear_session("nonexistent")
        assert result is False
    
    def test_list_sessions(self, pseudonymizer):
        """Test listing sessions."""
        # Initially empty
        sessions = pseudonymizer.list_sessions()
        initial_count = len(sessions)
        
        # Create a session
        pseudonymizer.session_manager.get_or_create_session("test-session")
        
        # Should have one more session
        sessions = pseudonymizer.list_sessions()
        assert len(sessions) == initial_count + 1
        assert "test-session" in sessions
    
    def test_get_statistics(self, pseudonymizer):
        """Test getting service statistics."""
        stats = pseudonymizer.get_statistics()
        
        assert "total_sessions" in stats
        assert "total_entities_processed" in stats
        assert "supported_languages" in stats
        assert "ner_models_loaded" in stats
        assert "extended_entity_types" in stats
        
        assert isinstance(stats["supported_languages"], list)
        assert isinstance(stats["extended_entity_types"], list)
    
    def test_cleanup(self, pseudonymizer):
        """Test cleanup method."""
        with patch.object(pseudonymizer.ner_pipeline, 'unload_models') as mock_unload:
            pseudonymizer.cleanup()
            mock_unload.assert_called_once()

class TestPseudonymizationValidation:
    """Test input validation for pseudonymization."""
    
    def test_invalid_text_type(self, pseudonymizer):
        """Test that invalid text types raise appropriate errors."""
        with pytest.raises(Exception):  # Should raise some form of error
            pseudonymizer.pseudonymize_text(123)
    
    def test_invalid_language_parameter(self, pseudonymizer):
        """Test invalid language parameter handling."""
        # This should fall back to default behavior rather than crash
        result = pseudonymizer.pseudonymize_text("test", language="invalid")
        assert result is not None
    
    def test_confidence_bounds(self, pseudonymizer):
        """Test confidence parameter bounds."""
        # Should handle out-of-bounds confidence gracefully
        result = pseudonymizer.pseudonymize_text("test", min_confidence=1.5)
        assert result is not None
        
        result = pseudonymizer.pseudonymize_text("test", min_confidence=-0.5)
        assert result is not None

@pytest.mark.integration
class TestPseudonymizationIntegration:
    """Integration tests that require actual models (marked for optional running)."""
    
    @pytest.mark.slow
    def test_real_german_text_pseudonymization(self, pseudonymizer):
        """Test pseudonymizing real German text (requires model download)."""
        german_text = "Max Müller wohnt in Berlin und arbeitet bei Siemens."
        
        result = pseudonymizer.pseudonymize_text(german_text, language="de")
        
        assert result.detected_language == "de"
        assert result.entity_count > 0
        assert "PERSON_" in result.pseudonymized
        assert "LOCATION_" in result.pseudonymized
        assert "ORGANIZATION_" in result.pseudonymized
    
    @pytest.mark.slow
    def test_real_english_text_pseudonymization(self, pseudonymizer):
        """Test pseudonymizing real English text (requires model download)."""
        english_text = "John Smith lives in New York and works at Microsoft."
        
        result = pseudonymizer.pseudonymize_text(english_text, language="en")
        
        assert result.detected_language == "en"
        assert result.entity_count > 0
        assert "PERSON_" in result.pseudonymized
        assert "LOCATION_" in result.pseudonymized
        assert "ORGANIZATION_" in result.pseudonymized
    
    @pytest.mark.slow
    def test_consistency_across_texts(self, pseudonymizer):
        """Test that same entities get same pseudonyms across different texts."""
        texts = [
            "Max Müller lebt in Berlin.",
            "Berlin ist die Hauptstadt. Max Müller ist Ingenieur."
        ]
        
        result = pseudonymizer.pseudonymize_text(texts, language="de")
        
        # Both texts should use same pseudonyms for same entities
        assert isinstance(result.pseudonymized, list)
        assert len(result.pseudonymized) == 2
        
        # Extract pseudonyms used
        text1_pseudonyms = set(word for word in result.pseudonymized[0].split() if "_" in word)
        text2_pseudonyms = set(word for word in result.pseudonymized[1].split() if "_" in word)
        
        # Should have some overlap (same entities, same pseudonyms)
        assert len(text1_pseudonyms.intersection(text2_pseudonyms)) > 0