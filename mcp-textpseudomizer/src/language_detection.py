"""Language detection module for text pseudonymization."""

import logging
from typing import Tuple, Optional
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)

DetectorFactory.seed = 0

class LanguageDetector:
    """Detects the language of input text to select appropriate NER models."""
    
    SUPPORTED_LANGUAGES = {
        "de": "German",
        "en": "English"
    }
    
    DEFAULT_LANGUAGE = "en"
    
    def __init__(self):
        """Initialize the language detector."""
        self._models = {
            "de": "flair/ner-german",
            "en": "flair/ner-english"
        }
    
    def detect_language(self, text: str, sample_length: int = 200) -> Tuple[str, float]:
        """
        Detect the language of the given text.
        
        Args:
            text: Input text to analyze
            sample_length: Number of characters to analyze for detection
            
        Returns:
            Tuple of (language_code, confidence_score)
        """
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided")
            return self.DEFAULT_LANGUAGE, 0.0
        
        # Use first sample_length characters for detection
        sample_text = text[:sample_length].strip()
        
        try:
            detected_lang = detect(sample_text)
            
            # Map to supported languages
            if detected_lang in self.SUPPORTED_LANGUAGES:
                confidence = self._calculate_confidence(sample_text, detected_lang)
                logger.info(f"Detected language: {detected_lang} (confidence: {confidence:.2f})")
                return detected_lang, confidence
            else:
                logger.warning(f"Unsupported language detected: {detected_lang}, falling back to {self.DEFAULT_LANGUAGE}")
                return self.DEFAULT_LANGUAGE, 0.5
                
        except LangDetectException as e:
            logger.error(f"Language detection failed: {e}, falling back to {self.DEFAULT_LANGUAGE}")
            return self.DEFAULT_LANGUAGE, 0.0
    
    def _calculate_confidence(self, text: str, detected_lang: str) -> float:
        """
        Calculate confidence score based on text characteristics.
        
        Args:
            text: Sample text used for detection
            detected_lang: Detected language code
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Basic confidence calculation based on text length and language-specific patterns
        base_confidence = 0.7
        
        # Increase confidence for longer texts
        length_factor = min(len(text) / 100, 1.0) * 0.2
        
        # Language-specific confidence adjustments
        if detected_lang == "de":
            # German-specific patterns (umlauts, common words)
            german_patterns = ["ä", "ö", "ü", "ß", "der", "die", "das", "und", "ist", "ein", "eine"]
            pattern_matches = sum(1 for pattern in german_patterns if pattern in text.lower())
            pattern_factor = min(pattern_matches / 5, 1.0) * 0.1
        elif detected_lang == "en":
            # English-specific patterns (common words)
            english_patterns = ["the", "and", "is", "a", "an", "this", "that", "with", "for"]
            pattern_matches = sum(1 for pattern in english_patterns if pattern in text.lower())
            pattern_factor = min(pattern_matches / 5, 1.0) * 0.1
        else:
            pattern_factor = 0.0
        
        confidence = base_confidence + length_factor + pattern_factor
        return min(confidence, 1.0)
    
    def get_model_for_language(self, language_code: str) -> str:
        """
        Get the NER model name for the given language.
        
        Args:
            language_code: Language code (de, en)
            
        Returns:
            Model name for the language
        """
        return self._models.get(language_code, self._models[self.DEFAULT_LANGUAGE])
    
    def is_supported_language(self, language_code: str) -> bool:
        """
        Check if the language is supported.
        
        Args:
            language_code: Language code to check
            
        Returns:
            True if language is supported
        """
        return language_code in self.SUPPORTED_LANGUAGES
    
    def get_supported_languages(self) -> dict:
        """
        Get all supported languages with their models.
        
        Returns:
            Dictionary mapping language codes to language info
        """
        return {
            code: {
                "name": self.SUPPORTED_LANGUAGES[code],
                "model": self._models[code]
            }
            for code in self.SUPPORTED_LANGUAGES
        }