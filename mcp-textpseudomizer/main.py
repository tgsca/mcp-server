#!/usr/bin/env python3
"""MCP Text Pseudonymizer Server - Automatic text pseudonymization using NER."""

import logging
import os
import sys
from typing import Union, List, Dict, Any, Optional
from pydantic import Field
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

# Configure logging to stderr to avoid interfering with MCP stdio protocol
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

try:
    from src.pseudonymizer import TextPseudonymizer
    PSEUDONYMIZER_AVAILABLE = True
except ImportError as e:
    logger.error(f"Could not import TextPseudonymizer: {e}")
    logger.info("Falling back to minimal mock implementation")
    PSEUDONYMIZER_AVAILABLE = False
    TextPseudonymizer = None

# Create the MCP server
if PSEUDONYMIZER_AVAILABLE:
    mcp = FastMCP("Text Pseudonymizer")
    # Initialize the pseudonymization service
    pseudonymizer = TextPseudonymizer()
else:
    mcp = FastMCP("Text Pseudonymizer (Mock Mode)")
    pseudonymizer = None

@mcp.tool()
def pseudonymize_text(
    text: str = Field(..., description="Text string to pseudonymize"),
    language: str = Field(default="auto", description="Language code (auto, de, en)"),
    preserve_formatting: bool = Field(default=True, description="Preserve text formatting"),
    session_id: Optional[str] = Field(default=None, description="Session ID for consistent mappings"),
    min_confidence: float = Field(default=0.5, description="Minimum confidence threshold (0.0-1.0)")
) -> Dict[str, Any]:
    """
    Pseudonymize text by replacing sensitive entities with placeholders.
    
    Automatically detects and replaces:
    - Named entities (persons, locations, organizations)
    - Email addresses, phone numbers, dates
    - ID numbers, IBANs, license numbers
    
    Args:
        text: Text string to pseudonymize
        language: Language code ("auto", "de", "en") for model selection
        preserve_formatting: Whether to preserve text formatting (case, etc.)
        session_id: Optional session ID for consistent entity mappings
        min_confidence: Minimum confidence threshold for entity detection (0.0-1.0)
        
    Returns:
        Dictionary containing:
        - pseudonymized: Pseudonymized text
        - detected_language: Detected or specified language
        - entity_count: Number of entities replaced
        - session_id: Session ID used for mappings
    """
    if not PSEUDONYMIZER_AVAILABLE:
        # Mock implementation fallback
        logger.info(f"Using mock pseudonymization for: {text[:50]}...")
        mock_result = text.replace("John", "PERSON_1").replace("Berlin", "LOCATION_1").replace("Google", "ORGANIZATION_1")
        entity_count = len([x for x in ["John", "Berlin", "Google"] if x in text])
        
        return {
            "pseudonymized": mock_result,
            "detected_language": "en" if language == "auto" else language,
            "entity_count": entity_count,
            "session_id": session_id or "mock-session-123",
            "note": "Mock implementation - install ML dependencies for full functionality"
        }
    
    try:
        result = pseudonymizer.pseudonymize_text(
            text=text,
            language=language,
            preserve_formatting=preserve_formatting,
            session_id=session_id,
            min_confidence=min_confidence
        )
        
        return {
            "pseudonymized": result.pseudonymized,
            "detected_language": result.detected_language,
            "entity_count": result.entity_count,
            "session_id": result.session_id
        }
        
    except Exception as e:
        logger.error(f"Error in pseudonymize_text: {e}")
        return {
            "error": f"Pseudonymization failed: {str(e)}",
            "pseudonymized": text,
            "detected_language": "unknown",
            "entity_count": 0,
            "session_id": session_id or ""
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
    if not PSEUDONYMIZER_AVAILABLE:
        # Simple mock detection
        if any(word in text.lower() for word in ["der", "die", "das", "und", "ist", "ein"]):
            return {"language": "de", "confidence": 0.85}
        else:
            return {"language": "en", "confidence": 0.90}
    
    try:
        result = pseudonymizer.detect_language(text)
        return {
            "language": result.language,
            "confidence": result.confidence
        }
    except Exception as e:
        logger.error(f"Error in detect_language: {e}")
        return {
            "error": f"Language detection failed: {str(e)}",
            "language": "en",
            "confidence": 0.0
        }

@mcp.tool()
def list_supported_languages() -> Dict[str, Any]:
    """
    Get information about supported languages and their NER models.
    
    Returns:
        Dictionary containing:
        - languages: List of supported languages with model information
    """
    if not PSEUDONYMIZER_AVAILABLE:
        return {
            "languages": [
                {"code": "de", "name": "German", "model": "mock-pattern-matching"},
                {"code": "en", "name": "English", "model": "mock-pattern-matching"}
            ]
        }
    
    try:
        languages_info = pseudonymizer.list_supported_languages()
        languages_list = [
            {
                "code": code,
                "name": info["name"],
                "model": info["model"]
            }
            for code, info in languages_info.items()
        ]
        
        return {"languages": languages_list}
    except Exception as e:
        logger.error(f"Error in list_supported_languages: {e}")
        return {
            "error": f"Failed to get supported languages: {str(e)}",
            "languages": []
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
    if not PSEUDONYMIZER_AVAILABLE:
        return {
            "mappings": {
                "John": "PERSON_1",
                "Berlin": "LOCATION_1",
                "Google": "ORGANIZATION_1"
            },
            "statistics": {
                "total_entities": 3,
                "by_type": {"PER": 1, "LOC": 1, "ORG": 1},
                "unique_entities": 3,
                "session_id": session_id or "mock-session-123"
            }
        }
    
    try:
        result = pseudonymizer.get_entity_mappings(session_id)
        if "error" in result:
            return result
        
        return {
            "mappings": result["mappings"],
            "statistics": result["statistics"]
        }
    except Exception as e:
        logger.error(f"Error in get_entity_mappings: {e}")
        return {
            "error": f"Failed to get entity mappings: {str(e)}",
            "mappings": {},
            "statistics": {}
        }

@mcp.tool()
def get_service_statistics() -> Dict[str, Any]:
    """
    Get overall service statistics and status.
    
    Returns:
        Dictionary containing:
        - total_sessions: Number of active sessions
        - total_entities_processed: Total entities processed across all sessions
        - supported_languages: List of supported language codes
        - ner_models_loaded: Number of NER models currently loaded
        - extended_entity_types: List of extended entity types supported
    """
    if not PSEUDONYMIZER_AVAILABLE:
        return {
            "total_sessions": 1,
            "total_entities_processed": 3,
            "supported_languages": ["de", "en"],
            "ner_models_loaded": 0,
            "extended_entity_types": ["EMAIL", "PHONE", "DATE", "ID", "IBAN"],
            "status": "mock-mode",
            "note": "Mock implementation - install ML dependencies for full functionality"
        }
    
    try:
        stats = pseudonymizer.get_statistics()
        return {
            "total_sessions": stats["total_sessions"],
            "total_entities_processed": stats["total_entities_processed"],
            "supported_languages": stats["supported_languages"],
            "ner_models_loaded": stats["ner_models_loaded"],
            "extended_entity_types": stats["extended_entity_types"],
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"Error in get_service_statistics: {e}")
        return {
            "error": f"Failed to get service statistics: {str(e)}",
            "total_sessions": 0,
            "total_entities_processed": 0,
            "supported_languages": [],
            "ner_models_loaded": 0,
            "extended_entity_types": [],
            "status": "error"
        }

if __name__ == "__main__":
    logger.info("Starting MCP Text Pseudonymizer Server...")
    
    # Check if running in Docker - use stdio but keep process alive
    import os
    if os.getenv("MCP_TRANSPORT") == "tcp":
        logger.info("Running in Docker mode - keeping process alive for stdio connections")
        # For Docker, we still use stdio but keep the process running
        # The container will be accessed via docker exec for MCP connections
        try:
            # Keep the server alive and ready to handle connections
            import signal
            import time
            
            def signal_handler(signum, frame):
                logger.info("Received shutdown signal, stopping server...")
                exit(0)
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            logger.info("MCP server ready for stdio connections via docker exec")
            # Keep the process alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
    else:
        # Default stdio transport for MCP client integration
        mcp.run()
