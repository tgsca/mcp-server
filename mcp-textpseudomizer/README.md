# MCP Text Pseudonymizer

An MCP (Model Context Protocol) server for automatic text pseudonymization using Named Entity Recognition. This service automatically detects and replaces sensitive information (names, locations, organizations, emails, phone numbers, etc.) with consistent placeholders while preserving text readability.

## Features

- **Automatic Language Detection**: Supports German and English with auto-detection
- **Named Entity Recognition**: Uses state-of-the-art flair models for person, location, and organization detection
- **Extended Entity Recognition**: Detects emails, phone numbers, dates, IDs, IBANs, license numbers
- **Consistent Mapping**: Same entities get same pseudonyms within and across documents
- **Session Management**: Persistent entity mappings with import/export functionality
- **Batch Processing**: Efficient processing of multiple texts
- **Docker Ready**: Production containerization with health checks

## Installation

### Prerequisites

- Python 3.12 or higher
- uv package manager (recommended) or pip
- Huggingface account (optional, but recommended)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mcp-textpseudomizer
   ```

2. **Install dependencies:**

   **Option A: Basic installation (works on all platforms):**
   ```bash
   uv sync
   ```
   This installs core dependencies without heavy ML packages. The server will run in mock mode with basic pattern matching.

   **Option B: Full ML functionality (may require compilation):**
   ```bash
   uv sync --extra ml
   ```
   This installs flair and spacy for full NER capabilities. Note: May fail on some platforms (e.g., macOS ARM64 with Python 3.13) due to `sentencepiece` compilation issues.

   **Option C: With pip:**
   ```bash
   # Basic installation
   pip install -e .
   
   # Full ML functionality  
   pip install -e .[ml]
   ```

3. **Configure Huggingface token (recommended):**
   - Create a free account at [huggingface.co](https://huggingface.co)
   - Get your access token from [Settings > Access Tokens](https://huggingface.co/settings/tokens)
   - This improves model download reliability and avoids rate limits

4. **Create environment configuration:**
   ```bash
   cp .env.template .env
   # Edit .env and add your Huggingface token:
   # HF_TOKEN=your_actual_token_here
   ```

5. **Run the MCP server:**
   
   **Basic mode (mock functionality):**
   ```bash
   uv run python main.py
   ```
   
   **Full ML mode (after installing ML dependencies):**
   ```bash
   uv sync --extra ml
   uv run python main.py
   ```
   
   **Minimal testing mode (for MCP Inspector):**
   ```bash
   uv run python main-minimal.py
   ```

## Deployment Modes

The MCP Text Pseudonymizer supports three deployment modes:

### 1. **Mock Mode** (Default - Always Works)
- Uses basic pattern matching for entity detection
- No compilation required, works on all platforms
- Suitable for development, testing, and platforms with compilation issues
- Install: `uv sync`

### 2. **Full ML Mode** (Production)
- Uses advanced flair NER models for accurate entity detection
- Requires compilation of ML dependencies
- Best accuracy and performance
- Install: `uv sync --extra ml`

### 3. **Docker Mode** (Production)
- Pre-compiled ML models in container
- No local compilation needed
- Best for production deployment
- Install: `docker-compose up -d`

### Docker Installation

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

2. **Or build manually:**
   ```bash
   docker build -t mcp-textpseudomizer .
   docker run -d -p 3000:3000 --name mcp-textpseudomizer mcp-textpseudomizer
   ```

## MCP Client Configuration

### Claude Desktop Configuration

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "textpseudomizer": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/path/to/mcp-textpseudomizer/main.py"
      ],
      "cwd": "/path/to/mcp-textpseudomizer"
    }
  }
}
```

### Docker-based Configuration

For Docker deployment, the container runs with TCP transport. Configure Claude Desktop to connect via TCP:

```json
{
  "mcpServers": {
    "textpseudomizer": {
      "command": "docker",
      "args": [
        "exec",
        "mcp-textpseudomizer",
        "python",
        "main.py"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Alternatively, for direct TCP connection (if supported):

```json
{
  "mcpServers": {
    "textpseudomizer": {
      "transport": "tcp",
      "host": "localhost",
      "port": 3000
    }
  }
}
```

### Alternative: Direct Python Configuration

If you have the dependencies installed globally:

```json
{
  "mcpServers": {
    "textpseudomizer": {
      "command": "python",
      "args": ["/path/to/mcp-textpseudomizer/main.py"],
      "cwd": "/path/to/mcp-textpseudomizer"
    }
  }
}
```

### MCP Inspector Configuration

For testing with [@modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector), use the minimal implementation:

```json
{
  "mcpServers": {
    "textpseudomizer": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "main-minimal.py"
      ],
      "cwd": "/path/to/mcp-textpseudomizer"
    }
  }
}
```

Or if you have fastmcp installed locally:

```json
{
  "mcpServers": {
    "textpseudomizer": {
      "command": "python",
      "args": ["main-minimal.py"],
      "cwd": "/path/to/mcp-textpseudomizer"
    }
  }
}
```

**Note**: The minimal implementation (`main-minimal.py`) provides mock functionality for testing the MCP protocol without requiring heavy ML dependencies. For full functionality, use the Docker container.

### Environment Variables

Configure the server behavior by setting these environment variables in your `.env` file:

```bash
# Huggingface Configuration (recommended)
HF_TOKEN=your_huggingface_token_here

# Logging
LOG_LEVEL=INFO

# Model Settings
MODEL_CACHE_DIR=./models
TORCH_DEVICE=auto
MIN_CONFIDENCE_THRESHOLD=0.5

# Language Settings
DEFAULT_LANGUAGE=auto
SUPPORTED_LANGUAGES=de,en

# Performance
MAX_TEXT_LENGTH=10000
BATCH_SIZE=10
TIMEOUT_SECONDS=30

# Features
ENABLE_EMAIL_DETECTION=true
ENABLE_PHONE_DETECTION=true
ENABLE_DATE_DETECTION=true
ENABLE_ID_DETECTION=true
ENABLE_IBAN_DETECTION=true
```

**Important**: The `HF_TOKEN` is optional but highly recommended. It provides:
- Better reliability when downloading NER models
- Avoids rate limits on Huggingface Hub
- Faster model downloads
- Future-proofing for potential private model access

## Available MCP Tools

Once configured, the following tools will be available in Claude:

### `pseudonymize_text`
Main pseudonymization function that replaces sensitive entities with placeholders.
- **Input**: text (string or array), language, preserve_formatting, session_id, min_confidence
- **Output**: pseudonymized text, detected language, entity count, session_id

### `detect_language`
Detects the language of input text.
- **Input**: text string
- **Output**: detected language code and confidence score

### `list_supported_languages`
Lists all supported languages and their NER models.
- **Output**: array of supported languages with model information

### `get_entity_mappings`
Retrieves entity mappings and statistics for a session.
- **Input**: optional session_id
- **Output**: mappings dictionary and statistics

### `clear_session`
Clears all mappings for a specific session.
- **Input**: session_id
- **Output**: success status and message

### `list_sessions`
Lists all active pseudonymization sessions.
- **Output**: array of session IDs and count

### `export_mappings`
Exports entity mappings from a session as JSON.
- **Input**: session_id
- **Output**: JSON string with mappings and metadata

### `import_mappings`
Imports entity mappings from JSON data.
- **Input**: mappings_json, optional session_id
- **Output**: success status and actual session_id used

### `get_service_statistics`
Gets overall service statistics and status.
- **Output**: session count, entities processed, loaded models, status

## Usage Examples

### Basic Text Pseudonymization

```
User: Please pseudonymize this German text: "Max M�ller wohnt in Berlin und arbeitet bei Siemens."

Claude will use the pseudonymize_text tool and return:
"PERSON_1 wohnt in LOCATION_1 und arbeitet bei ORGANIZATION_1."
```

### Batch Processing

```
User: Pseudonymize these texts while keeping entity mappings consistent:
1. "John Smith works at Microsoft in Seattle."
2. "Microsoft's headquarters are in Seattle, where John Smith is employed."

Claude will process both texts with consistent mappings:
1. "PERSON_1 works at ORGANIZATION_1 in LOCATION_1."  
2. "ORGANIZATION_1's headquarters are in LOCATION_1, where PERSON_1 is employed."
```

### Session Management

```
User: Export the entity mappings from my current session.

Claude will use export_mappings to provide a JSON with all entity-to-pseudonym mappings.
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run only unit tests (fast)
uv run pytest -m "not slow"

# Run with coverage
uv run pytest --cov=src
```

### Code Quality

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

## Architecture

The service is built with a modular architecture:

- **Language Detection**: Auto-detects German/English from text samples
- **NER Pipeline**: Manages flair models for entity extraction
- **Entity Mapping**: Ensures consistent pseudonym assignment
- **Extended Patterns**: Regex-based detection for emails, phones, dates, etc.
- **MCP Tools**: FastMCP integration layer
- **Error Handling**: Comprehensive exception management

## Performance

- **Latency**: < 2s for texts up to 1000 words
- **Throughput**: 10+ texts/second in batch mode
- **Memory**: ~4GB RAM with full model loading
- **Model Caching**: Models stay loaded after first use

## Security & Privacy

- All processing happens locally - no external API calls
- Entity mappings are session-scoped and not persisted by default
- Original text never leaves the processing pipeline
- Comprehensive input validation and error handling
- Docker containers run as non-root user

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]