"""Extended entity recognition patterns for dates, emails, phones, etc."""

import logging
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException
import dateparser
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass 
class ExtendedEntity:
    """Represents an extended entity detected by pattern matching."""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0

class ExtendedPatternMatcher:
    """Detects extended entities using regex patterns and specialized libraries."""
    
    def __init__(self):
        """Initialize pattern matcher with compiled regex patterns."""
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile all regex patterns for efficient matching."""
        # German ID patterns
        self._patterns = {
            "ID": [
                # German Personalausweisnummer (9 digits + 1 check digit)
                re.compile(r'\b[0-9]{9}[0-9]\b'),
                # German Reisepassnummer (9 alphanumeric characters)
                re.compile(r'\b[CFGHJKLMNPRTVWXYZ][0-9]{8}\b'),
                # Generic ID patterns
                re.compile(r'\b(?:ID|Nr\.?|Nummer)\s*:?\s*([A-Z0-9]{6,20})\b', re.IGNORECASE),
            ],
            
            "IBAN": [
                # International IBAN format
                re.compile(r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}\b'),
                # German IBAN specifically
                re.compile(r'\bDE[0-9]{20}\b'),
            ],
            
            "LICENSE": [
                # German Führerscheinnummer
                re.compile(r'\b[A-Z0-9]{11}\b'),
                # US Driver License patterns (varies by state)
                re.compile(r'\b[A-Z][0-9]{7,12}\b'),
                re.compile(r'\b[0-9]{8,12}\b'),
            ],
            
            "CREDIT_CARD": [
                # Credit card numbers (basic pattern)
                re.compile(r'\b(?:[0-9]{4}[-\s]?){3}[0-9]{4}\b'),
                re.compile(r'\b[0-9]{13,19}\b'),
            ],
            
            "TAX_ID": [
                # German Steuerliche Identifikationsnummer
                re.compile(r'\b[0-9]{11}\b'),
                # German Steuernummer
                re.compile(r'\b[0-9]{2,3}/[0-9]{3}/[0-9]{5}\b'),
            ],
            
            "SOCIAL_SECURITY": [
                # US Social Security Number
                re.compile(r'\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b'),
                re.compile(r'\b[0-9]{9}\b'),
            ]
        }
    
    def extract_extended_entities(self, text: str, language: str = "de") -> List[ExtendedEntity]:
        """
        Extract extended entities from text using various detection methods.
        
        Args:
            text: Input text to analyze
            language: Language for context-specific patterns
            
        Returns:
            List of detected extended entities
        """
        entities = []
        
        # Extract different types of entities
        entities.extend(self._extract_emails(text))
        entities.extend(self._extract_phone_numbers(text, language))
        entities.extend(self._extract_dates(text, language))
        entities.extend(self._extract_pattern_entities(text))
        
        # Remove overlapping entities
        entities = self._remove_overlaps(entities)
        
        logger.debug(f"Extracted {len(entities)} extended entities")
        return entities
    
    def _extract_emails(self, text: str) -> List[ExtendedEntity]:
        """Extract email addresses from text."""
        entities = []
        
        # Basic email regex pattern
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        for match in email_pattern.finditer(text):
            email = match.group()
            
            # Validate email using email-validator
            try:
                validate_email(email)
                entities.append(ExtendedEntity(
                    text=email,
                    label="EMAIL",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95
                ))
            except EmailNotValidError:
                # Skip invalid emails
                continue
        
        return entities
    
    def _extract_phone_numbers(self, text: str, language: str = "de") -> List[ExtendedEntity]:
        """Extract phone numbers from text."""
        entities = []
        
        # Set default region based on language
        default_region = "DE" if language == "de" else "US"
        
        # Common phone number patterns
        phone_patterns = [
            re.compile(r'\+?[0-9\s\-\(\)]{7,20}'),
            re.compile(r'\b(?:\+49|0)[0-9\s\-\(\)]{10,15}\b'),  # German numbers
            re.compile(r'\b\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),  # US format
        ]
        
        for pattern in phone_patterns:
            for match in pattern.finditer(text):
                phone_text = match.group().strip()
                
                try:
                    # Parse and validate phone number
                    parsed_number = phonenumbers.parse(phone_text, default_region)
                    
                    if phonenumbers.is_valid_number(parsed_number):
                        entities.append(ExtendedEntity(
                            text=phone_text,
                            label="PHONE",
                            start=match.start(),
                            end=match.end(),
                            confidence=0.9
                        ))
                except NumberParseException:
                    # Skip invalid phone numbers
                    continue
        
        return entities
    
    def _extract_dates(self, text: str, language: str = "de") -> List[ExtendedEntity]:
        """Extract dates from text using dateparser."""
        entities = []
        
        # Common date patterns
        date_patterns = [
            # DD.MM.YYYY (German format)
            re.compile(r'\b[0-3]?[0-9]\.[0-1]?[0-9]\.[0-9]{2,4}\b'),
            # DD/MM/YYYY or MM/DD/YYYY
            re.compile(r'\b[0-3]?[0-9]/[0-1]?[0-9]/[0-9]{2,4}\b'),
            # YYYY-MM-DD (ISO format)
            re.compile(r'\b[0-9]{4}-[0-1]?[0-9]-[0-3]?[0-9]\b'),
            # Textual dates (e.g., "15. März 2023", "March 15, 2023")
            re.compile(r'\b[0-3]?[0-9]\.?\s+(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+[0-9]{2,4}\b', re.IGNORECASE),
            re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+[0-3]?[0-9],?\s+[0-9]{2,4}\b', re.IGNORECASE),
        ]
        
        for pattern in date_patterns:
            for match in pattern.finditer(text):
                date_text = match.group().strip()
                
                # Validate date using dateparser
                try:
                    parsed_date = dateparser.parse(date_text, languages=[language, 'en'])
                    
                    if parsed_date and parsed_date.year > 1900 and parsed_date.year < 2100:
                        entities.append(ExtendedEntity(
                            text=date_text,
                            label="DATE",
                            start=match.start(),
                            end=match.end(),
                            confidence=0.85
                        ))
                except Exception:
                    # Skip unparseable dates
                    continue
        
        return entities
    
    def _extract_pattern_entities(self, text: str) -> List[ExtendedEntity]:
        """Extract entities using compiled regex patterns."""
        entities = []
        
        for entity_type, patterns in self._patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    # Additional validation based on entity type
                    if self._validate_pattern_match(match.group(), entity_type):
                        entities.append(ExtendedEntity(
                            text=match.group(),
                            label=entity_type,
                            start=match.start(),
                            end=match.end(),
                            confidence=0.8
                        ))
        
        return entities
    
    def _validate_pattern_match(self, text: str, entity_type: str) -> bool:
        """
        Additional validation for pattern matches.
        
        Args:
            text: Matched text
            entity_type: Type of entity
            
        Returns:
            True if match is valid
        """
        if entity_type == "IBAN":
            # Basic IBAN validation (length and format)
            return len(text) >= 15 and len(text) <= 34 and text[:2].isalpha()
        
        elif entity_type == "CREDIT_CARD":
            # Basic Luhn algorithm check
            return self._luhn_check(text.replace("-", "").replace(" ", ""))
        
        elif entity_type == "TAX_ID":
            # German tax ID should be 11 digits
            return len(text.replace("/", "")) >= 8
        
        elif entity_type == "SOCIAL_SECURITY":
            # US SSN format validation
            clean_text = text.replace("-", "")
            return len(clean_text) == 9 and clean_text.isdigit()
        
        return True
    
    def _luhn_check(self, card_number: str) -> bool:
        """
        Validate credit card number using Luhn algorithm.
        
        Args:
            card_number: Credit card number string
            
        Returns:
            True if valid according to Luhn algorithm
        """
        if not card_number.isdigit():
            return False
        
        digits = [int(d) for d in card_number]
        checksum = 0
        
        # Process digits from right to left, doubling every second digit
        for i in range(len(digits) - 2, -1, -1):
            if (len(digits) - i) % 2 == 0:
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            checksum += digits[i]
        
        return (checksum + digits[-1]) % 10 == 0
    
    def _remove_overlaps(self, entities: List[ExtendedEntity]) -> List[ExtendedEntity]:
        """
        Remove overlapping entities, keeping the one with higher confidence.
        
        Args:
            entities: List of entities to process
            
        Returns:
            List of non-overlapping entities
        """
        if not entities:
            return entities
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: e.start)
        result = []
        
        for entity in sorted_entities:
            if not result:
                result.append(entity)
                continue
            
            last_entity = result[-1]
            
            # Check for overlap
            if entity.start < last_entity.end:
                # Keep entity with higher confidence
                if entity.confidence > last_entity.confidence:
                    result[-1] = entity
                # If same confidence, keep the longer entity
                elif entity.confidence == last_entity.confidence:
                    if len(entity.text) > len(last_entity.text):
                        result[-1] = entity
            else:
                result.append(entity)
        
        return result
    
    def get_supported_entity_types(self) -> List[str]:
        """
        Get list of supported extended entity types.
        
        Returns:
            List of entity type labels
        """
        return ["EMAIL", "PHONE", "DATE"] + list(self._patterns.keys())
    
    def configure_patterns(self, custom_patterns: Dict[str, List[str]]):
        """
        Add or update custom regex patterns.
        
        Args:
            custom_patterns: Dictionary mapping entity types to regex pattern strings
        """
        for entity_type, pattern_strings in custom_patterns.items():
            compiled_patterns = []
            for pattern_str in pattern_strings:
                try:
                    compiled_patterns.append(re.compile(pattern_str))
                except re.error as e:
                    logger.warning(f"Invalid regex pattern for {entity_type}: {pattern_str} - {e}")
            
            if compiled_patterns:
                self._patterns[entity_type] = compiled_patterns
                logger.info(f"Updated patterns for entity type: {entity_type}")
    
    def test_pattern(self, text: str, entity_type: str) -> List[Dict]:
        """
        Test patterns against text for debugging.
        
        Args:
            text: Text to test against
            entity_type: Entity type to test
            
        Returns:
            List of match information
        """
        matches = []
        
        if entity_type in self._patterns:
            for i, pattern in enumerate(self._patterns[entity_type]):
                for match in pattern.finditer(text):
                    matches.append({
                        "pattern_index": i,
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "valid": self._validate_pattern_match(match.group(), entity_type)
                    })
        
        return matches