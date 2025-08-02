# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management (uv)
- `uv sync` - Install/sync dependencies from pyproject.toml
- `uv add <package>` - Add new dependency
- `uv remove <package>` - Remove dependency  
- `uv run <command>` - Run command in virtual environment
- `uv run python main.py` - Run the MCP server locally

### Code Quality
- `ruff check .` - Lint code and report issues
- `ruff format .` - Format code according to style guide
- `ruff check --fix .` - Auto-fix linting issues where possible

### Running the MCP Server
- `uv run python main.py` - Start the text pseudonymization MCP server
- Server will expose MCP tools for text pseudonymization via FastMCP framework

### Docker Commands (when implemented)
- `docker build -t mcp-textpseudomizer .` - Build Docker image
- `docker-compose up` - Start containerized service
- `docker-compose down` - Stop containerized service

## Project Architecture

This is an **MCP (Model Context Protocol) server** for automatic text pseudonymization using Named Entity Recognition (NER).

### Current State
- **Early Development**: Only skeleton structure exists (placeholder main.py)
- **Specification Complete**: Comprehensive requirements documented in PROJECT.md
- **Ready for Implementation**: Tech stack and architecture fully defined

### Core Purpose
Provides privacy-compliant text processing by automatically detecting and replacing sensitive information (names, locations, organizations, dates, etc.) with consistent placeholders while preserving text readability.

### Tech Stack Architecture

**Core Framework:**
- **Python 3.12+** - Primary language (requires-python >= 3.13 in pyproject.toml)
- **FastMCP** - MCP server framework for tool exposure
- **uv** - Modern Python package manager for dependency management

**NLP/ML Pipeline:**
- **Huggingface Transformers** - Model hub integration
- **Language Detection** - Primary: HF language-detection, Fallback: langdetect
- **NER Models**: 
  - German: `flair/ner-german`
  - English: `flair/ner-english`
- **spaCy** - Extended NLP pipeline support

**Entity Detection Stack:**
- **dateparser** - Date recognition in multiple formats
- **phonenumbers** - International phone number detection
- **email-validator** - Email address validation
- **Custom Regex** - ID numbers, IBANs, license numbers

### Planned MCP Tools

When implemented, the server will expose these MCP tools:

1. **`pseudonymize_text`** - Main pseudonymization function
   - Input: text (string/array), language (auto/de/en), preserve_formatting
   - Output: pseudonymized text, detected language, entity count

2. **`detect_language`** - Language detection utility
   - Input: text string
   - Output: language code, confidence score

3. **`list_supported_languages`** - Available language models
   - Output: supported languages with model information

4. **`get_entity_mappings`** - Session mapping retrieval
   - Input: session_id (optional)
   - Output: entity mappings and statistics

### Data Flow Architecture
1. **Language Detection** - Analyze first 200 chars to select appropriate NER model
2. **Entity Recognition** - Apply language-specific NER + custom pattern matching
3. **Consistent Mapping** - Maintain entity-to-placeholder mappings within sessions
4. **Batch Processing** - Support parallel processing with shared mapping tables

### Key Implementation Notes
- **Consistency**: Same entities get same placeholders across document batches
- **Performance**: Target <2s latency for 1000-word texts, 10 texts/second batch processing
- **Memory**: Max 4GB RAM with full model loading, implement model caching
- **Language Support**: German and English with auto-detection, extensible to other languages
- **Entity Types**: Standard NER (PER/LOC/ORG) + extended (DATE/EMAIL/PHONE/ID/IBAN/LICENSE)

### Development Workflow
1. Implement core NER pipeline with language detection
2. Add entity mapping and consistency layer  
3. Build MCP tools using FastMCP framework
4. Add batch processing capabilities
5. Implement Docker containerization
6. Add comprehensive error handling and logging

### Error Handling Strategy
- Graceful degradation when models fail to load
- Clear error messages for invalid inputs
- Timeout handling for large texts
- Comprehensive logging with context information