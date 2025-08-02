"""Error handling and exception management for the pseudonymization service."""

import logging
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    """Error codes for different types of failures."""
    LANGUAGE_DETECTION_FAILED = "LANG_001"
    MODEL_LOADING_FAILED = "MODEL_001" 
    ENTITY_EXTRACTION_FAILED = "NER_001"
    PATTERN_MATCHING_FAILED = "PATTERN_001"
    MAPPING_CREATION_FAILED = "MAPPING_001"
    SESSION_NOT_FOUND = "SESSION_001"
    INVALID_INPUT = "INPUT_001"
    TIMEOUT_ERROR = "TIMEOUT_001"
    MEMORY_ERROR = "MEMORY_001"
    CONFIGURATION_ERROR = "CONFIG_001"
    UNKNOWN_ERROR = "UNKNOWN_001"

class PseudonymizerError(Exception):
    """Base exception for pseudonymization service errors."""
    
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR, details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            "error": True,
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }

class LanguageDetectionError(PseudonymizerError):
    """Error in language detection process."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, ErrorCode.LANGUAGE_DETECTION_FAILED, details)

class ModelLoadingError(PseudonymizerError):
    """Error loading NER models."""
    
    def __init__(self, message: str, model_name: str = "", details: Optional[Dict] = None):
        details = details or {}
        details["model_name"] = model_name
        super().__init__(message, ErrorCode.MODEL_LOADING_FAILED, details)

class EntityExtractionError(PseudonymizerError):
    """Error during entity extraction."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, ErrorCode.ENTITY_EXTRACTION_FAILED, details)

class PatternMatchingError(PseudonymizerError):
    """Error in pattern matching for extended entities."""
    
    def __init__(self, message: str, pattern_type: str = "", details: Optional[Dict] = None):
        details = details or {}
        details["pattern_type"] = pattern_type
        super().__init__(message, ErrorCode.PATTERN_MATCHING_FAILED, details)

class MappingError(PseudonymizerError):
    """Error in entity mapping operations."""
    
    def __init__(self, message: str, session_id: str = "", details: Optional[Dict] = None):
        details = details or {}
        details["session_id"] = session_id
        super().__init__(message, ErrorCode.MAPPING_CREATION_FAILED, details)

class SessionNotFoundError(PseudonymizerError):
    """Session not found error."""
    
    def __init__(self, session_id: str):
        message = f"Session '{session_id}' not found"
        details = {"session_id": session_id}
        super().__init__(message, ErrorCode.SESSION_NOT_FOUND, details)

class InvalidInputError(PseudonymizerError):
    """Invalid input provided to service."""
    
    def __init__(self, message: str, input_type: str = "", details: Optional[Dict] = None):
        details = details or {}
        details["input_type"] = input_type
        super().__init__(message, ErrorCode.INVALID_INPUT, details)

class TimeoutError(PseudonymizerError):
    """Operation timeout error."""
    
    def __init__(self, message: str, timeout_seconds: float = 0, details: Optional[Dict] = None):
        details = details or {}
        details["timeout_seconds"] = timeout_seconds
        super().__init__(message, ErrorCode.TIMEOUT_ERROR, details)

class MemoryError(PseudonymizerError):
    """Memory-related error."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, ErrorCode.MEMORY_ERROR, details)

class ConfigurationError(PseudonymizerError):
    """Configuration-related error."""
    
    def __init__(self, message: str, config_key: str = "", details: Optional[Dict] = None):
        details = details or {}
        details["config_key"] = config_key
        super().__init__(message, ErrorCode.CONFIGURATION_ERROR, details)

def handle_errors(fallback_result: Any = None, log_errors: bool = True):
    """
    Decorator for handling errors in service methods.
    
    Args:
        fallback_result: Default result to return on error
        log_errors: Whether to log caught errors
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PseudonymizerError:
                # Re-raise our custom errors
                raise
            except Exception as e:
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                # Convert to our error type
                error = PseudonymizerError(
                    message=f"Unexpected error in {func.__name__}: {str(e)}",
                    error_code=ErrorCode.UNKNOWN_ERROR,
                    details={"original_error": str(e), "function": func.__name__}
                )
                
                if fallback_result is not None:
                    logger.warning(f"Returning fallback result for {func.__name__}")
                    return fallback_result
                
                raise error
        return wrapper
    return decorator

def validate_input(text: Any, allow_empty: bool = False) -> str:
    """
    Validate and normalize text input.
    
    Args:
        text: Input to validate
        allow_empty: Whether to allow empty text
        
    Returns:
        Validated text string
        
    Raises:
        InvalidInputError: If input is invalid
    """
    if text is None:
        raise InvalidInputError("Text input cannot be None", "text")
    
    if not isinstance(text, (str, list)):
        raise InvalidInputError(
            f"Text must be string or list of strings, got {type(text).__name__}",
            "text"
        )
    
    if isinstance(text, list):
        if not all(isinstance(item, str) for item in text):
            raise InvalidInputError("All items in text list must be strings", "text_list")
        
        if not allow_empty and all(not item.strip() for item in text):
            raise InvalidInputError("Text list cannot be empty or contain only whitespace", "text_list")
        
        return text
    
    # String input
    if not allow_empty and not text.strip():
        raise InvalidInputError("Text cannot be empty or only whitespace", "text")
    
    return text

def validate_language(language: str) -> str:
    """
    Validate language parameter.
    
    Args:
        language: Language code to validate
        
    Returns:
        Validated language code
        
    Raises:
        InvalidInputError: If language is invalid
    """
    if not isinstance(language, str):
        raise InvalidInputError(
            f"Language must be string, got {type(language).__name__}",
            "language"
        )
    
    language = language.lower().strip()
    
    valid_languages = {"auto", "de", "en"}
    if language not in valid_languages:
        raise InvalidInputError(
            f"Language '{language}' not supported. Valid options: {', '.join(valid_languages)}",
            "language"
        )
    
    return language

def validate_confidence(confidence: float) -> float:
    """
    Validate confidence threshold.
    
    Args:
        confidence: Confidence value to validate
        
    Returns:
        Validated confidence value
        
    Raises:
        InvalidInputError: If confidence is invalid
    """
    if not isinstance(confidence, (int, float)):
        raise InvalidInputError(
            f"Confidence must be numeric, got {type(confidence).__name__}",
            "confidence"
        )
    
    if not 0.0 <= confidence <= 1.0:
        raise InvalidInputError(
            f"Confidence must be between 0.0 and 1.0, got {confidence}",
            "confidence"
        )
    
    return float(confidence)

def validate_session_id(session_id: Optional[str]) -> Optional[str]:
    """
    Validate session ID parameter.
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        Validated session ID or None
        
    Raises:
        InvalidInputError: If session ID is invalid
    """
    if session_id is None:
        return None
    
    if not isinstance(session_id, str):
        raise InvalidInputError(
            f"Session ID must be string, got {type(session_id).__name__}",
            "session_id"
        )
    
    session_id = session_id.strip()
    
    if not session_id:
        raise InvalidInputError("Session ID cannot be empty", "session_id")
    
    # Basic format validation
    if len(session_id) < 8 or len(session_id) > 128:
        raise InvalidInputError(
            f"Session ID must be between 8 and 128 characters, got {len(session_id)}",
            "session_id"
        )
    
    return session_id

class ErrorHandler:
    """Centralized error handling for the service."""
    
    def __init__(self, graceful_degradation: bool = True):
        """
        Initialize error handler.
        
        Args:
            graceful_degradation: Whether to attempt graceful degradation on errors
        """
        self.graceful_degradation = graceful_degradation
        self.error_counts = {}
    
    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Handle an error and return appropriate response.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            
        Returns:
            Error response dictionary
        """
        # Track error frequency
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log error
        logger.error(f"Error in {context}: {error}")
        logger.debug(f"Error traceback: {traceback.format_exc()}")
        
        # Handle known error types
        if isinstance(error, PseudonymizerError):
            return error.to_dict()
        
        # Handle unknown errors
        return PseudonymizerError(
            message=f"Unexpected error in {context}: {str(error)}",
            error_code=ErrorCode.UNKNOWN_ERROR,
            details={"context": context, "error_type": error_type}
        ).to_dict()
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics.
        
        Returns:
            Dictionary with error statistics
        """
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts_by_type": self.error_counts.copy(),
            "graceful_degradation_enabled": self.graceful_degradation
        }
    
    def reset_statistics(self):
        """Reset error statistics."""
        self.error_counts.clear()
        logger.info("Error statistics reset")

# Global error handler instance
error_handler = ErrorHandler()