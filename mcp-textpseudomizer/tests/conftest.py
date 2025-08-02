"""Pytest configuration and shared fixtures."""

import pytest
import logging
import tempfile
import os
from unittest.mock import Mock, patch

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture(scope="session")
def mock_models():
    """Mock the model loading to avoid downloading models during tests."""
    with patch('flair.models.SequenceTagger.load') as mock_load:
        # Create a mock model
        mock_model = Mock()
        mock_model.predict = Mock()
        mock_model.to = Mock(return_value=mock_model)
        mock_load.return_value = mock_model
        yield mock_model

@pytest.fixture
def temp_model_dir():
    """Create a temporary directory for model cache."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_env = os.environ.get('MODEL_CACHE_DIR')
        os.environ['MODEL_CACHE_DIR'] = temp_dir
        yield temp_dir
        if original_env:
            os.environ['MODEL_CACHE_DIR'] = original_env
        else:
            os.environ.pop('MODEL_CACHE_DIR', None)

@pytest.fixture
def sample_german_text():
    """Sample German text for testing."""
    return "Max Müller wohnt in Berlin und arbeitet bei der Deutschen Bank."

@pytest.fixture
def sample_english_text():
    """Sample English text for testing."""
    return "John Smith lives in New York and works at Microsoft Corporation."

@pytest.fixture
def sample_mixed_entities_text():
    """Sample text with various entity types."""
    return """
    John Doe (john.doe@example.com) lives at 123 Main Street, New York.
    His phone number is +1-555-123-4567 and his birthday is March 15, 1985.
    His driver's license number is A1234567890.
    """

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require models)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may take longer to run)"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ["real_", "integration_", "model_"]):
            item.add_marker(pytest.mark.slow)