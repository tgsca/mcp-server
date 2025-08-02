"""Entity mapping system for consistent pseudonymization."""

import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import uuid
import json

logger = logging.getLogger(__name__)

@dataclass
class EntityMapping:
    """Represents a mapping between original entity and pseudonym."""
    original: str
    pseudonym: str
    entity_type: str
    session_id: str
    created_at: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class MappingStatistics:
    """Statistics about entity mappings in a session."""
    total_entities: int
    by_type: Dict[str, int] = field(default_factory=dict)
    unique_entities: int = 0
    session_id: str = ""

class EntityMapper:
    """Manages consistent entity-to-pseudonym mappings."""
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize entity mapper.
        
        Args:
            session_id: Optional session identifier for grouping mappings
        """
        self.session_id = session_id or str(uuid.uuid4())
        self._mappings: Dict[str, EntityMapping] = {}
        self._type_counters: Dict[str, int] = defaultdict(int)
        self._reverse_mappings: Dict[str, str] = {}
        
        logger.info(f"EntityMapper initialized with session_id: {self.session_id}")
    
    def get_or_create_pseudonym(self, entity_text: str, entity_type: str) -> str:
        """
        Get existing pseudonym or create new one for entity.
        
        Args:
            entity_text: Original entity text
            entity_type: Type of entity (PER, LOC, ORG, etc.)
            
        Returns:
            Consistent pseudonym for the entity
        """
        # Normalize entity text for consistent mapping
        normalized_text = self._normalize_entity_text(entity_text)
        mapping_key = f"{normalized_text}:{entity_type}"
        
        if mapping_key in self._mappings:
            return self._mappings[mapping_key].pseudonym
        
        # Create new pseudonym
        self._type_counters[entity_type] += 1
        pseudonym = self._generate_pseudonym(entity_type, self._type_counters[entity_type])
        
        # Store mapping
        mapping = EntityMapping(
            original=entity_text,
            pseudonym=pseudonym,
            entity_type=entity_type,
            session_id=self.session_id
        )
        
        self._mappings[mapping_key] = mapping
        self._reverse_mappings[pseudonym] = entity_text
        
        logger.debug(f"Created new mapping: {entity_text} -> {pseudonym}")
        return pseudonym
    
    def _normalize_entity_text(self, text: str) -> str:
        """
        Normalize entity text for consistent mapping.
        
        Args:
            text: Original entity text
            
        Returns:
            Normalized text
        """
        # Basic normalization: strip whitespace, lowercase for comparison
        return text.strip().lower()
    
    def _generate_pseudonym(self, entity_type: str, counter: int) -> str:
        """
        Generate pseudonym based on entity type and counter.
        
        Args:
            entity_type: Type of entity
            counter: Counter for this entity type
            
        Returns:
            Generated pseudonym
        """
        # Map flair entity types to readable pseudonym prefixes
        type_mapping = {
            "PER": "PERSON",
            "LOC": "LOCATION", 
            "ORG": "ORGANIZATION",
            "MISC": "MISC",
            "DATE": "DATE",
            "EMAIL": "EMAIL",
            "PHONE": "PHONE",
            "ID": "ID",
            "IBAN": "IBAN",
            "LICENSE": "LICENSE"
        }
        
        prefix = type_mapping.get(entity_type, entity_type)
        return f"{prefix}_{counter}"
    
    def batch_map_entities(self, entities_by_text: List[Tuple[str, List[Tuple[str, str]]]]) -> List[Tuple[str, str]]:
        """
        Map entities in multiple texts while maintaining consistency.
        
        Args:
            entities_by_text: List of (text, [(entity_text, entity_type), ...])
            
        Returns:
            List of (original_text, pseudonymized_text) pairs
        """
        results = []
        
        for original_text, entities in entities_by_text:
            pseudonymized_text = self._pseudonymize_text(original_text, entities)
            results.append((original_text, pseudonymized_text))
        
        return results
    
    def _pseudonymize_text(self, text: str, entities: List[Tuple[str, str]]) -> str:
        """
        Replace entities in text with their pseudonyms.
        
        Args:
            text: Original text
            entities: List of (entity_text, entity_type) tuples
            
        Returns:
            Text with entities replaced by pseudonyms
        """
        # Sort entities by position (descending) to avoid position shifts
        sorted_entities = sorted(entities, key=lambda x: text.find(x[0]), reverse=True)
        
        result_text = text
        for entity_text, entity_type in sorted_entities:
            pseudonym = self.get_or_create_pseudonym(entity_text, entity_type)
            result_text = result_text.replace(entity_text, pseudonym)
        
        return result_text
    
    def get_mapping_for_entity(self, entity_text: str, entity_type: str) -> Optional[str]:
        """
        Get existing mapping for an entity without creating new one.
        
        Args:
            entity_text: Original entity text
            entity_type: Entity type
            
        Returns:
            Existing pseudonym or None
        """
        normalized_text = self._normalize_entity_text(entity_text)
        mapping_key = f"{normalized_text}:{entity_type}"
        
        mapping = self._mappings.get(mapping_key)
        return mapping.pseudonym if mapping else None
    
    def get_original_for_pseudonym(self, pseudonym: str) -> Optional[str]:
        """
        Get original entity text for a pseudonym.
        
        Args:
            pseudonym: Pseudonym to look up
            
        Returns:
            Original entity text or None
        """
        return self._reverse_mappings.get(pseudonym)
    
    def get_all_mappings(self) -> Dict[str, str]:
        """
        Get all entity mappings as original -> pseudonym dictionary.
        
        Returns:
            Dictionary of original entities to pseudonyms
        """
        return {
            mapping.original: mapping.pseudonym 
            for mapping in self._mappings.values()
        }
    
    def get_statistics(self) -> MappingStatistics:
        """
        Get statistics about current mappings.
        
        Returns:
            Statistics about the mappings
        """
        by_type = defaultdict(int)
        for mapping in self._mappings.values():
            by_type[mapping.entity_type] += 1
        
        return MappingStatistics(
            total_entities=len(self._mappings),
            by_type=dict(by_type),
            unique_entities=len(set(mapping.original for mapping in self._mappings.values())),
            session_id=self.session_id
        )
    
    def export_mappings(self) -> str:
        """
        Export mappings to JSON string.
        
        Returns:
            JSON string containing all mappings
        """
        export_data = {
            "session_id": self.session_id,
            "mappings": [
                {
                    "original": mapping.original,
                    "pseudonym": mapping.pseudonym,
                    "entity_type": mapping.entity_type,
                    "created_at": mapping.created_at
                }
                for mapping in self._mappings.values()
            ],
            "statistics": {
                "total_entities": len(self._mappings),
                "by_type": dict(self._type_counters),
                "unique_entities": len(set(mapping.original for mapping in self._mappings.values()))
            }
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def import_mappings(self, json_data: str) -> bool:
        """
        Import mappings from JSON string.
        
        Args:
            json_data: JSON string containing mappings
            
        Returns:
            True if import successful, False otherwise
        """
        try:
            data = json.loads(json_data)
            
            # Clear existing mappings
            self._mappings.clear()
            self._reverse_mappings.clear()
            self._type_counters.clear()
            
            # Import session ID
            self.session_id = data.get("session_id", str(uuid.uuid4()))
            
            # Import mappings
            for mapping_data in data.get("mappings", []):
                original = mapping_data["original"]
                entity_type = mapping_data["entity_type"]
                
                mapping = EntityMapping(
                    original=original,
                    pseudonym=mapping_data["pseudonym"],
                    entity_type=entity_type,
                    session_id=self.session_id,
                    created_at=mapping_data.get("created_at", str(uuid.uuid4()))
                )
                
                normalized_text = self._normalize_entity_text(original)
                mapping_key = f"{normalized_text}:{entity_type}"
                
                self._mappings[mapping_key] = mapping
                self._reverse_mappings[mapping.pseudonym] = original
            
            # Rebuild type counters
            for mapping in self._mappings.values():
                # Extract counter from pseudonym (e.g., "PERSON_5" -> 5)
                try:
                    counter = int(mapping.pseudonym.split("_")[-1])
                    current_max = self._type_counters.get(mapping.entity_type, 0)
                    self._type_counters[mapping.entity_type] = max(current_max, counter)
                except ValueError:
                    # Fallback if pseudonym format is different
                    self._type_counters[mapping.entity_type] += 1
            
            logger.info(f"Successfully imported {len(self._mappings)} mappings")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import mappings: {e}")
            return False
    
    def clear_mappings(self):
        """Clear all mappings and reset counters."""
        self._mappings.clear()
        self._reverse_mappings.clear() 
        self._type_counters.clear()
        logger.info(f"Cleared all mappings for session: {self.session_id}")


class MappingSessionManager:
    """Manages multiple entity mapping sessions."""
    
    def __init__(self):
        """Initialize session manager."""
        self._sessions: Dict[str, EntityMapper] = {}
        logger.info("MappingSessionManager initialized")
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> EntityMapper:
        """
        Get existing session or create new one.
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            EntityMapper for the session
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self._sessions:
            self._sessions[session_id] = EntityMapper(session_id)
            logger.info(f"Created new mapping session: {session_id}")
        
        return self._sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[EntityMapper]:
        """
        Get existing session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            EntityMapper or None if not found
        """
        return self._sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted mapping session: {session_id}")
            return True
        return False
    
    def list_sessions(self) -> List[str]:
        """
        List all active session IDs.
        
        Returns:
            List of session IDs
        """
        return list(self._sessions.keys())
    
    def get_session_statistics(self, session_id: str) -> Optional[MappingStatistics]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Statistics or None if session not found
        """
        session = self._sessions.get(session_id)
        return session.get_statistics() if session else None