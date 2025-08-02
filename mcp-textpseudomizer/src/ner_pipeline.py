"""Named Entity Recognition pipeline for text pseudonymization."""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
try:
    import torch
    from flair.data import Sentence
    from flair.models import SequenceTagger
    FLAIR_AVAILABLE = True
except ImportError:
    FLAIR_AVAILABLE = False
    torch = None
    Sentence = None
    SequenceTagger = None

logger = logging.getLogger(__name__)

@dataclass
class Entity:
    """Represents a detected entity in text."""
    text: str
    label: str
    start: int
    end: int
    confidence: float

class NERPipeline:
    """Manages NER models and entity extraction."""
    
    def __init__(self):
        """Initialize the NER pipeline."""
        if not FLAIR_AVAILABLE:
            logger.warning("Flair not available - NER functionality will be limited to mock responses")
            self._models = {}
            self._model_configs = {}
            self._device = "cpu"
            return
            
        self._models = {}
        self._model_configs = {
            "de": "flair/ner-german",
            "en": "flair/ner-english"
        }
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"NER Pipeline initialized with device: {self._device}")
    
    def _load_model(self, language: str) -> SequenceTagger:
        """
        Load and cache NER model for the specified language.
        
        Args:
            language: Language code (de, en)
            
        Returns:
            Loaded NER model
        """
        if language not in self._models:
            model_name = self._model_configs.get(language, self._model_configs["en"])
            logger.info(f"Loading NER model: {model_name}")
            
            try:
                model = SequenceTagger.load(model_name)
                model.to(self._device)
                self._models[language] = model
                logger.info(f"Successfully loaded model for language: {language}")
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {e}")
                raise
        
        return self._models[language]
    
    def extract_entities(self, text: str, language: str) -> List[Entity]:
        """
        Extract named entities from text using language-specific model.
        
        Args:
            text: Input text to process
            language: Language code for model selection
            
        Returns:
            List of detected entities
        """
        if not text or not text.strip():
            return []
        
        if not FLAIR_AVAILABLE:
            # Mock extraction for basic pattern recognition
            logger.debug("Using mock NER extraction (flair not available)")
            return self._mock_extract_entities(text)
        
        try:
            model = self._load_model(language)
            sentence = Sentence(text)
            model.predict(sentence)
            
            entities = []
            for entity in sentence.get_spans('ner'):
                entities.append(Entity(
                    text=entity.text,
                    label=entity.get_label("ner").value,
                    start=entity.start_position,
                    end=entity.end_position,
                    confidence=entity.get_label("ner").score
                ))
            
            logger.debug(f"Extracted {len(entities)} entities from text")
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    def batch_extract_entities(self, texts: List[str], language: str) -> List[List[Entity]]:
        """
        Extract entities from multiple texts in batch.
        
        Args:
            texts: List of input texts
            language: Language code for model selection
            
        Returns:
            List of entity lists for each input text
        """
        if not FLAIR_AVAILABLE:
            # Use mock extraction for each text
            results = []
            for text in texts:
                if not text or not text.strip():
                    results.append([])
                else:
                    results.append(self._mock_extract_entities(text))
            logger.info(f"Mock batch processed {len(texts)} texts")
            return results
        
        results = []
        
        try:
            model = self._load_model(language)
            
            for text in texts:
                if not text or not text.strip():
                    results.append([])
                    continue
                
                sentence = Sentence(text)
                model.predict(sentence)
                
                entities = []
                for entity in sentence.get_spans('ner'):
                    entities.append(Entity(
                        text=entity.text,
                        label=entity.get_label("ner").value,
                        start=entity.start_position,
                        end=entity.end_position,
                        confidence=entity.get_label("ner").score
                    ))
                
                results.append(entities)
            
            logger.info(f"Batch processed {len(texts)} texts")
            return results
            
        except Exception as e:
            logger.error(f"Batch entity extraction failed: {e}")
            return [[] for _ in texts]
    
    def get_entity_types(self, language: str) -> List[str]:
        """
        Get supported entity types for the specified language.
        
        Args:
            language: Language code
            
        Returns:
            List of supported entity type labels
        """
        # Standard entity types supported by flair NER models
        standard_types = ["PER", "LOC", "ORG", "MISC"]
        
        # Language-specific variations
        if language == "de":
            return ["PER", "LOC", "ORG", "MISC"]
        elif language == "en":
            return ["PER", "LOC", "ORG", "MISC"]
        else:
            return standard_types
    
    def filter_entities_by_confidence(self, entities: List[Entity], min_confidence: float = 0.5) -> List[Entity]:
        """
        Filter entities by minimum confidence score.
        
        Args:
            entities: List of entities to filter
            min_confidence: Minimum confidence threshold
            
        Returns:
            Filtered list of entities
        """
        filtered = [entity for entity in entities if entity.confidence >= min_confidence]
        logger.debug(f"Filtered {len(entities)} entities to {len(filtered)} (min_confidence={min_confidence})")
        return filtered
    
    def merge_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Merge overlapping entities, keeping the one with higher confidence.
        
        Args:
            entities: List of entities to process
            
        Returns:
            List of non-overlapping entities
        """
        if not entities:
            return entities
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: e.start)
        merged = []
        
        for entity in sorted_entities:
            if not merged:
                merged.append(entity)
                continue
            
            last_entity = merged[-1]
            
            # Check for overlap
            if entity.start < last_entity.end:
                # Keep entity with higher confidence
                if entity.confidence > last_entity.confidence:
                    merged[-1] = entity
                # If same confidence, keep the longer entity
                elif entity.confidence == last_entity.confidence:
                    if len(entity.text) > len(last_entity.text):
                        merged[-1] = entity
            else:
                merged.append(entity)
        
        logger.debug(f"Merged {len(entities)} entities to {len(merged)} non-overlapping entities")
        return merged
    
    def unload_models(self):
        """Unload all cached models to free memory."""
        for language in list(self._models.keys()):
            del self._models[language]
        self._models.clear()
        
        # Clear GPU cache if using CUDA
        if self._device == "cuda":
            torch.cuda.empty_cache()
        
        logger.info("All NER models unloaded")
    
    def _mock_extract_entities(self, text: str) -> List[Entity]:
        """
        Mock entity extraction using simple pattern matching.
        Used when flair is not available.
        """
        entities = []
        import re
        
        # Simple patterns for common entities (for testing purposes)
        patterns = {
            "PER": [r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", r"\bJohn\b", r"\bMary\b", r"\bMax\b"],
            "LOC": [r"\bBerlin\b", r"\bLondon\b", r"\bParis\b", r"\bNew York\b"],
            "ORG": [r"\bGoogle\b", r"\bMicrosoft\b", r"\bApple\b", r"\bSiemens\b"]
        }
        
        for label, pattern_list in patterns.items():
            for pattern in pattern_list:
                for match in re.finditer(pattern, text):
                    entities.append(Entity(
                        text=match.group(),
                        label=label,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.8  # Mock confidence
                    ))
        
        return entities
    
    def get_model_info(self) -> Dict[str, Dict]:
        """
        Get information about available models.
        
        Returns:
            Dictionary with model information
        """
        info = {}
        for lang, model_name in self._model_configs.items():
            info[lang] = {
                "model_name": model_name,
                "loaded": lang in self._models,
                "entity_types": self.get_entity_types(lang)
            }
        return info