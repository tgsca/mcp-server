"""Main pseudonymization service combining all components."""

import logging
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass

from .language_detection import LanguageDetector
from .ner_pipeline import NERPipeline, Entity
from .entity_mapping import EntityMapper, MappingSessionManager, MappingStatistics
from .extended_patterns import ExtendedPatternMatcher, ExtendedEntity

logger = logging.getLogger(__name__)

@dataclass
class PseudonymizationResult:
    """Result of text pseudonymization."""
    pseudonymized: Union[str, List[str]]
    detected_language: str
    entity_count: int
    session_id: str
    confidence: float

@dataclass 
class LanguageDetectionResult:
    """Result of language detection."""
    language: str
    confidence: float

class TextPseudonymizer:
    """Main service for text pseudonymization using NER and pattern matching."""
    
    def __init__(self):
        """Initialize the pseudonymization service."""
        self.language_detector = LanguageDetector()
        self.ner_pipeline = NERPipeline()
        self.pattern_matcher = ExtendedPatternMatcher()
        self.session_manager = MappingSessionManager()
        
        logger.info("TextPseudonymizer initialized")
    
    def pseudonymize_text(
        self,
        text: Union[str, List[str]],
        language: str = "auto",
        preserve_formatting: bool = True,
        session_id: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> PseudonymizationResult:
        """
        Pseudonymize text by replacing entities with consistent placeholders.
        
        Args:
            text: Single text string or list of texts
            language: Language code ("auto", "de", "en") 
            preserve_formatting: Whether to preserve text formatting
            session_id: Optional session ID for consistent mappings
            min_confidence: Minimum confidence for entity detection
            
        Returns:
            PseudonymizationResult with pseudonymized text and metadata
        """
        # Handle single text vs batch
        is_single_text = isinstance(text, str)
        texts = [text] if is_single_text else text
        
        if not texts or all(not t.strip() for t in texts):
            return PseudonymizationResult(
                pseudonymized="" if is_single_text else [],
                detected_language="en",
                entity_count=0,
                session_id=session_id or "",
                confidence=0.0
            )
        
        # Get or create mapping session
        entity_mapper = self.session_manager.get_or_create_session(session_id)
        
        # Detect language if auto
        if language == "auto":
            # Use first non-empty text for language detection
            sample_text = next((t for t in texts if t.strip()), "")
            detected_language, lang_confidence = self.language_detector.detect_language(sample_text)
        else:
            detected_language = language
            lang_confidence = 1.0
        
        # Process all texts
        results = []
        total_entities = 0
        
        for text_content in texts:
            if not text_content.strip():
                results.append("")
                continue
            
            # Extract entities using NER
            ner_entities = self.ner_pipeline.extract_entities(text_content, detected_language)
            
            # Filter by confidence
            ner_entities = self.ner_pipeline.filter_entities_by_confidence(ner_entities, min_confidence)
            
            # Extract extended entities
            extended_entities = self.pattern_matcher.extract_extended_entities(text_content, detected_language)
            
            # Combine and process all entities
            all_entities = self._combine_entities(ner_entities, extended_entities)
            total_entities += len(all_entities)
            
            # Pseudonymize text
            pseudonymized_text = self._replace_entities_in_text(
                text_content, all_entities, entity_mapper, preserve_formatting
            )
            
            results.append(pseudonymized_text)
        
        # Return result
        final_result = results[0] if is_single_text else results
        
        return PseudonymizationResult(
            pseudonymized=final_result,
            detected_language=detected_language,
            entity_count=total_entities,
            session_id=entity_mapper.session_id,
            confidence=lang_confidence
        )
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detect the language of input text.
        
        Args:
            text: Text to analyze
            
        Returns:
            LanguageDetectionResult with language and confidence
        """
        language, confidence = self.language_detector.detect_language(text)
        
        return LanguageDetectionResult(
            language=language,
            confidence=confidence
        )
    
    def list_supported_languages(self) -> Dict[str, Dict]:
        """
        Get information about supported languages.
        
        Returns:
            Dictionary with language information
        """
        return self.language_detector.get_supported_languages()
    
    def get_entity_mappings(self, session_id: Optional[str] = None) -> Dict:
        """
        Get entity mappings and statistics for a session.
        
        Args:
            session_id: Optional session ID
            
        Returns:
            Dictionary with mappings and statistics
        """
        if session_id:
            entity_mapper = self.session_manager.get_session(session_id)
            if not entity_mapper:
                return {"error": f"Session {session_id} not found"}
        else:
            # Get most recent session or create new one
            sessions = self.session_manager.list_sessions()
            if sessions:
                entity_mapper = self.session_manager.get_session(sessions[-1])
            else:
                entity_mapper = self.session_manager.get_or_create_session()
        
        mappings = entity_mapper.get_all_mappings()
        statistics = entity_mapper.get_statistics()
        
        return {
            "mappings": mappings,
            "statistics": {
                "total_entities": statistics.total_entities,
                "by_type": statistics.by_type,
                "unique_entities": statistics.unique_entities,
                "session_id": statistics.session_id
            }
        }
    
    def _combine_entities(self, ner_entities: List[Entity], extended_entities: List[ExtendedEntity]) -> List[Tuple[str, str, int, int]]:
        """
        Combine NER and extended entities, resolving overlaps.
        
        Args:
            ner_entities: Entities from NER pipeline
            extended_entities: Entities from pattern matching
            
        Returns:
            List of (text, label, start, end) tuples
        """
        # Convert to common format
        all_entities = []
        
        for entity in ner_entities:
            all_entities.append((entity.text, entity.label, entity.start, entity.end, entity.confidence))
        
        for entity in extended_entities:
            all_entities.append((entity.text, entity.label, entity.start, entity.end, entity.confidence))
        
        # Sort by start position
        all_entities.sort(key=lambda x: x[2])
        
        # Remove overlaps, keeping higher confidence entities
        filtered_entities = []
        for entity in all_entities:
            text, label, start, end, confidence = entity
            
            # Check for overlap with existing entities
            overlaps = False
            for i, existing in enumerate(filtered_entities):
                existing_text, existing_label, existing_start, existing_end, existing_confidence = existing
                
                # Check if entities overlap
                if not (end <= existing_start or start >= existing_end):
                    overlaps = True
                    # Keep entity with higher confidence
                    if confidence > existing_confidence:
                        filtered_entities[i] = entity
                    # If same confidence, keep longer entity
                    elif confidence == existing_confidence and len(text) > len(existing_text):
                        filtered_entities[i] = entity
                    break
            
            if not overlaps:
                filtered_entities.append(entity)
        
        # Return simplified format
        return [(text, label, start, end) for text, label, start, end, _ in filtered_entities]
    
    def _replace_entities_in_text(
        self,
        text: str,
        entities: List[Tuple[str, str, int, int]],
        entity_mapper: EntityMapper,
        preserve_formatting: bool = True
    ) -> str:
        """
        Replace entities in text with pseudonyms.
        
        Args:
            text: Original text
            entities: List of (text, label, start, end) tuples
            entity_mapper: Entity mapper for consistent pseudonyms
            preserve_formatting: Whether to preserve formatting
            
        Returns:
            Text with entities replaced by pseudonyms
        """
        if not entities:
            return text
        
        # Sort entities by start position (descending) to avoid position shifts
        sorted_entities = sorted(entities, key=lambda x: x[2], reverse=True)
        
        result_text = text
        
        for entity_text, entity_label, start_pos, end_pos in sorted_entities:
            # Get or create pseudonym
            pseudonym = entity_mapper.get_or_create_pseudonym(entity_text, entity_label)
            
            # Replace entity in text
            if preserve_formatting:
                # Try to preserve some formatting characteristics
                if entity_text.isupper():
                    pseudonym = pseudonym.upper()
                elif entity_text.istitle():
                    pseudonym = pseudonym.title()
                elif entity_text.islower():
                    pseudonym = pseudonym.lower()
            
            # Replace the entity at the specific position
            result_text = result_text[:start_pos] + pseudonym + result_text[end_pos:]
        
        return result_text
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a mapping session.
        
        Args:
            session_id: Session to clear
            
        Returns:
            True if session was cleared
        """
        return self.session_manager.delete_session(session_id)
    
    def list_sessions(self) -> List[str]:
        """
        List all active sessions.
        
        Returns:
            List of session IDs
        """
        return self.session_manager.list_sessions()
    
    def export_session_mappings(self, session_id: str) -> Optional[str]:
        """
        Export session mappings to JSON.
        
        Args:
            session_id: Session to export
            
        Returns:
            JSON string or None if session not found
        """
        entity_mapper = self.session_manager.get_session(session_id)
        if entity_mapper:
            return entity_mapper.export_mappings()
        return None
    
    def import_session_mappings(self, json_data: str, session_id: Optional[str] = None) -> bool:
        """
        Import session mappings from JSON.
        
        Args:
            json_data: JSON string with mappings
            session_id: Optional session ID to import to
            
        Returns:
            True if import successful
        """
        entity_mapper = self.session_manager.get_or_create_session(session_id)
        return entity_mapper.import_mappings(json_data)
    
    def get_statistics(self) -> Dict:
        """
        Get overall service statistics.
        
        Returns:
            Dictionary with service statistics
        """
        sessions = self.session_manager.list_sessions()
        total_entities = 0
        total_sessions = len(sessions)
        
        for session_id in sessions:
            stats = self.session_manager.get_session_statistics(session_id)
            if stats:
                total_entities += stats.total_entities
        
        return {
            "total_sessions": total_sessions,
            "total_entities_processed": total_entities,
            "supported_languages": list(self.language_detector.SUPPORTED_LANGUAGES.keys()),
            "ner_models_loaded": len(self.ner_pipeline._models),
            "extended_entity_types": self.pattern_matcher.get_supported_entity_types()
        }
    
    def cleanup(self):
        """Clean up resources and unload models."""
        self.ner_pipeline.unload_models()
        logger.info("TextPseudonymizer cleanup completed")