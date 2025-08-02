#!/usr/bin/env python3
"""Minimal MCP Text Pseudonymizer Server for local testing with MCP Inspector."""

import logging
import sys
from typing import Union, List, Dict, Any, Optional
from fastmcp import FastMCP

# Configure minimal logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("Text Pseudonymizer (Minimal)")

@mcp.tool()
def pseudonymize_text(
    text: Union[str, List[str]],
    language: str = "auto",
    preserve_formatting: bool = True,
    session_id: Optional[str] = None,
    min_confidence: float = 0.5
) -> Dict[str, Any]:
    """
    Pseudonymize text by replacing sensitive entities with placeholders.
    
    NOTE: This is a minimal implementation for MCP Inspector testing.
    The full implementation requires heavy ML dependencies.
    
    Args:
        text: Single text string or list of texts to pseudonymize
        language: Language code ("auto", "de", "en") for model selection
        preserve_formatting: Whether to preserve text formatting (case, etc.)
        session_id: Optional session ID for consistent entity mappings
        min_confidence: Minimum confidence threshold for entity detection (0.0-1.0)
        
    Returns:
        Dictionary containing:
        - pseudonymized: Pseudonymized text(s) (mock implementation)
        - detected_language: Detected or specified language
        - entity_count: Number of entities replaced
        - session_id: Session ID used for mappings
    """
    logger.info(f"Mock pseudonymization request for text: {text[:50] if isinstance(text, str) else text[0][:50]}...")
    
    # Mock implementation for testing
    if isinstance(text, str):
        mock_result = text.replace("John", "PERSON_1").replace("Berlin", "LOCATION_1").replace("Google", "ORGANIZATION_1")
        entity_count = len([x for x in ["John", "Berlin", "Google"] if x in text])
    else:
        mock_result = [t.replace("John", "PERSON_1").replace("Berlin", "LOCATION_1").replace("Google", "ORGANIZATION_1") for t in text]
        entity_count = sum(len([x for x in ["John", "Berlin", "Google"] if x in t]) for t in text)
    
    return {
        "pseudonymized": mock_result,
        "detected_language": "en" if language == "auto" else language,
        "entity_count": entity_count,
        "session_id": session_id or "mock-session-123"
    }

@mcp.tool()
def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect the language of input text.
    
    Args:
        text: Text to analyze for language detection
        
    Returns:
        Dictionary containing:
        - language: Detected language code (de, en)
        - confidence: Confidence score (0.0-1.0)
    """
    logger.info(f"Mock language detection for: {text[:30]}...")
    
    # Simple mock detection
    if any(word in text.lower() for word in ["der", "die", "das", "und", "ist", "ein"]):
        return {"language": "de", "confidence": 0.85}
    else:
        return {"language": "en", "confidence": 0.90}

@mcp.tool()
def list_supported_languages() -> Dict[str, Any]:
    """
    Get information about supported languages and their NER models.
    
    Returns:
        Dictionary containing:
        - languages: List of supported languages with model information
    """
    return {
        "languages": [
            {"code": "de", "name": "German", "model": "flair/ner-german"},
            {"code": "en", "name": "English", "model": "flair/ner-english"}
        ]
    }

@mcp.tool()
def get_entity_mappings(session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get entity mappings and statistics for a session.
    
    Args:
        session_id: Optional session ID (uses most recent if not provided)
        
    Returns:
        Dictionary containing:
        - mappings: Dictionary of original entities to pseudonyms
        - statistics: Statistics about entity counts by type
    """
    return {
        "mappings": {
            "John": "PERSON_1",
            "Berlin": "LOCATION_1", 
            "Google": "ORGANIZATION_1"
        },
        "statistics": {
            "total_entities": 3,
            "by_type": {
                "PERSON": 1,
                "LOCATION": 1,
                "ORGANIZATION": 1
            },
            "unique_entities": 3,
            "session_id": session_id or "mock-session-123"
        }
    }

@mcp.tool()
def get_service_statistics() -> Dict[str, Any]:
    """
    Get overall service statistics and status.
    
    Returns:
        Dictionary containing service information
    """
    return {
        "total_sessions": 1,
        "total_entities_processed": 3,
        "supported_languages": ["de", "en"],
        "ner_models_loaded": 0,  # Mock implementation
        "extended_entity_types": ["EMAIL", "PHONE", "DATE", "ID", "IBAN"],
        "status": "operational",
        "note": "This is a minimal mock implementation for MCP Inspector testing"
    }

if __name__ == "__main__":
    logger.info("Starting Minimal MCP Text Pseudonymizer Server for testing...")
    logger.info("This is a mock implementation for MCP Inspector - use Docker for full functionality")
    mcp.run()