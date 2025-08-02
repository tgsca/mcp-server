"""MCP tools for the text pseudonymization server."""

import logging
from typing import List, Dict, Optional, Union, Any
from fastmcp import FastMCP
from .pseudonymizer import TextPseudonymizer

logger = logging.getLogger(__name__)

class MCPTools:
    """MCP tools implementation for text pseudonymization."""
    
    def __init__(self, pseudonymizer: TextPseudonymizer):
        """
        Initialize MCP tools.
        
        Args:
            pseudonymizer: TextPseudonymizer service instance
        """
        self.pseudonymizer = pseudonymizer
        logger.info("MCP tools initialized")
    
    def register_tools(self, mcp: FastMCP):
        """
        Register all MCP tools with the FastMCP server.
        
        Args:
            mcp: FastMCP server instance
        """
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
            
            Automatically detects and replaces:
            - Named entities (persons, locations, organizations)
            - Email addresses, phone numbers, dates
            - ID numbers, IBANs, license numbers
            
            Args:
                text: Single text string or list of texts to pseudonymize
                language: Language code ("auto", "de", "en") for model selection
                preserve_formatting: Whether to preserve text formatting (case, etc.)
                session_id: Optional session ID for consistent entity mappings
                min_confidence: Minimum confidence threshold for entity detection (0.0-1.0)
                
            Returns:
                Dictionary containing:
                - pseudonymized: Pseudonymized text(s)
                - detected_language: Detected or specified language
                - entity_count: Number of entities replaced
                - session_id: Session ID used for mappings
            """
            return self.pseudonymize_text(text, language, preserve_formatting, session_id, min_confidence)
        
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
            return self.detect_language(text)
        
        @mcp.tool()
        def list_supported_languages() -> Dict[str, Any]:
            """
            Get information about supported languages and their NER models.
            
            Returns:
                Dictionary containing:
                - languages: List of supported languages with model information
            """
            return self.list_supported_languages()
        
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
            return self.get_entity_mappings(session_id)
        
        @mcp.tool()
        def clear_session(session_id: str) -> Dict[str, Any]:
            """
            Clear all mappings for a session.
            
            Args:
                session_id: Session ID to clear
                
            Returns:
                Dictionary containing:
                - success: Whether the operation succeeded
                - message: Status message
            """
            return self.clear_session(session_id)
        
        @mcp.tool()
        def list_sessions() -> Dict[str, Any]:
            """
            List all active pseudonymization sessions.
            
            Returns:
                Dictionary containing:
                - sessions: List of active session IDs
                - count: Number of active sessions
            """
            return self.list_sessions()
        
        @mcp.tool()
        def export_mappings(session_id: str) -> Dict[str, Any]:
            """
            Export entity mappings from a session as JSON.
            
            Args:
                session_id: Session ID to export
                
            Returns:
                Dictionary containing:
                - mappings_json: JSON string with all mappings and metadata
                - session_id: Session ID that was exported
            """
            return self.export_mappings(session_id)
        
        @mcp.tool()
        def import_mappings(
            mappings_json: str,
            session_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Import entity mappings from JSON data.
            
            Args:
                mappings_json: JSON string containing mappings to import
                session_id: Optional session ID to import to (creates new if not provided)
                
            Returns:
                Dictionary containing:
                - success: Whether the import succeeded
                - session_id: Session ID where mappings were imported
                - message: Status message
            """
            return self.import_mappings(mappings_json, session_id)
        
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
            return self.get_service_statistics()
        
        logger.info("All MCP tools registered")
    
    def pseudonymize_text(
        self,
        text: Union[str, List[str]],
        language: str = "auto",
        preserve_formatting: bool = True,
        session_id: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Pseudonymize text by replacing sensitive entities with placeholders.
        
        Automatically detects and replaces:
        - Named entities (persons, locations, organizations)
        - Email addresses, phone numbers, dates
        - ID numbers, IBANs, license numbers
        
        Args:
            text: Single text string or list of texts to pseudonymize
            language: Language code ("auto", "de", "en") for model selection
            preserve_formatting: Whether to preserve text formatting (case, etc.)
            session_id: Optional session ID for consistent entity mappings
            min_confidence: Minimum confidence threshold for entity detection (0.0-1.0)
            
        Returns:
            Dictionary containing:
            - pseudonymized: Pseudonymized text(s)
            - detected_language: Detected or specified language
            - entity_count: Number of entities replaced
            - session_id: Session ID used for mappings
        """
        try:
            result = self.pseudonymizer.pseudonymize_text(
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
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of input text.
        
        Args:
            text: Text to analyze for language detection
            
        Returns:
            Dictionary containing:
            - language: Detected language code (de, en)
            - confidence: Confidence score (0.0-1.0)
        """
        try:
            result = self.pseudonymizer.detect_language(text)
            
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
    
    def list_supported_languages(self) -> Dict[str, Any]:
        """
        Get information about supported languages and their NER models.
        
        Returns:
            Dictionary containing:
            - languages: List of supported languages with model information
        """
        try:
            languages_info = self.pseudonymizer.list_supported_languages()
            
            # Format for MCP response
            languages_list = [
                {
                    "code": code,
                    "name": info["name"],
                    "model": info["model"]
                }
                for code, info in languages_info.items()
            ]
            
            return {
                "languages": languages_list
            }
            
        except Exception as e:
            logger.error(f"Error in list_supported_languages: {e}")
            return {
                "error": f"Failed to get supported languages: {str(e)}",
                "languages": []
            }
    
    def get_entity_mappings(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get entity mappings and statistics for a session.
        
        Args:
            session_id: Optional session ID (uses most recent if not provided)
            
        Returns:
            Dictionary containing:
            - mappings: Dictionary of original entities to pseudonyms
            - statistics: Statistics about entity counts by type
        """
        try:
            result = self.pseudonymizer.get_entity_mappings(session_id)
            
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
    
    def clear_session(self, session_id: str) -> Dict[str, Any]:
        """
        Clear all mappings for a session.
        
        Args:
            session_id: Session ID to clear
            
        Returns:
            Dictionary containing:
            - success: Whether the operation succeeded
            - message: Status message
        """
        try:
            success = self.pseudonymizer.clear_session(session_id)
            
            return {
                "success": success,
                "message": f"Session {session_id} cleared" if success else f"Session {session_id} not found"
            }
            
        except Exception as e:
            logger.error(f"Error in clear_session: {e}")
            return {
                "success": False,
                "error": f"Failed to clear session: {str(e)}"
            }
    
    def list_sessions(self) -> Dict[str, Any]:
        """
        List all active pseudonymization sessions.
        
        Returns:
            Dictionary containing:
            - sessions: List of active session IDs
            - count: Number of active sessions
        """
        try:
            sessions = self.pseudonymizer.list_sessions()
            
            return {
                "sessions": sessions,
                "count": len(sessions)
            }
            
        except Exception as e:
            logger.error(f"Error in list_sessions: {e}")
            return {
                "error": f"Failed to list sessions: {str(e)}",
                "sessions": [],
                "count": 0
            }
    
    def export_mappings(self, session_id: str) -> Dict[str, Any]:
        """
        Export entity mappings from a session as JSON.
        
        Args:
            session_id: Session ID to export
            
        Returns:
            Dictionary containing:
            - mappings_json: JSON string with all mappings and metadata
            - session_id: Session ID that was exported
        """
        try:
            json_data = self.pseudonymizer.export_session_mappings(session_id)
            
            if json_data is None:
                return {
                    "error": f"Session {session_id} not found",
                    "mappings_json": "",
                    "session_id": session_id
                }
            
            return {
                "mappings_json": json_data,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error in export_mappings: {e}")
            return {
                "error": f"Failed to export mappings: {str(e)}",
                "mappings_json": "",
                "session_id": session_id
            }
    
    def import_mappings(
        self,
        mappings_json: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import entity mappings from JSON data.
        
        Args:
            mappings_json: JSON string containing mappings to import
            session_id: Optional session ID to import to (creates new if not provided)
            
        Returns:
            Dictionary containing:
            - success: Whether the import succeeded
            - session_id: Session ID where mappings were imported
            - message: Status message
        """
        try:
            success = self.pseudonymizer.import_session_mappings(mappings_json, session_id)
            
            # Get the actual session ID used
            if session_id is None:
                sessions = self.pseudonymizer.list_sessions()
                actual_session_id = sessions[-1] if sessions else "unknown"
            else:
                actual_session_id = session_id
            
            return {
                "success": success,
                "session_id": actual_session_id,
                "message": "Mappings imported successfully" if success else "Failed to import mappings"
            }
            
        except Exception as e:
            logger.error(f"Error in import_mappings: {e}")
            return {
                "success": False,
                "session_id": session_id or "",
                "error": f"Failed to import mappings: {str(e)}"
            }
    
    def get_service_statistics(self) -> Dict[str, Any]:
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
        try:
            stats = self.pseudonymizer.get_statistics()
            
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