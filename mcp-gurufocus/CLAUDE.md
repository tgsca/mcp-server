# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management (uv)
- `uv sync` - Install/sync dependencies from uv.lock
- `uv add <package>` - Add new dependency
- `uv remove <package>` - Remove dependency
- `uv run <command>` - Run command in virtual environment

### Code Quality
- `ruff check .` - Lint code and report issues
- `ruff format .` - Format code according to style guide
- `ruff check --fix .` - Auto-fix linting issues where possible

### Testing
- `uv run --group test pytest` - Run all tests with coverage
- `uv run --group test pytest tests/unit/` - Run only unit tests
- `uv run --group test pytest tests/integration/` - Run only integration tests
- `uv run --group test pytest tests/e2e/` - Run only end-to-end tests
- `uv run --group test pytest -v` - Run tests with verbose output
- `uv run --group test pytest tests/unit/test_api_client.py` - Run specific test file
- `uv run --group test pytest tests/unit/test_mcp_tools.py` - Run MCP tool tests
- `uv run --group test pytest --cov-report=term-missing` - Show detailed coverage with missing lines
- `uv run --group test pytest --cov-report=html` - Generate HTML coverage report (htmlcov/index.html)
- `uv run --group test pytest --no-cov` - Run tests without coverage

### Docker Testing
- `./scripts/test-docker.sh all` - Run comprehensive test suite in Docker
- `./scripts/test-docker.sh unit` - Run unit tests in Docker
- `./scripts/test-docker.sh integration` - Run integration tests in Docker
- `./scripts/test-docker.sh e2e` - Run end-to-end tests in Docker
- `./scripts/test-docker.sh coverage` - Generate coverage reports in Docker
- `./scripts/test-docker.sh quality` - Run code quality checks in Docker
- `./scripts/test-docker.sh build` - Build Docker test images
- `./scripts/test-docker.sh clean` - Clean up Docker resources

### Running the Application
- `uv run python app/main.py` - Run the MCP server
- Set `MCP_SERVER_MODE=stdio` environment variable for stdio transport
- Requires `GURUFOCUS_API_KEY` environment variable (see app/.env.template)

## Architecture Overview

This is an MCP (Model Context Protocol) server that provides structured access to GuruFocus financial API data. The application follows a layered architecture:

### Core Components

**MCP Server** (`app/main.py`)
- Uses FastMCP framework to expose financial data tools
- Defines async tool functions for data retrieval and processing
- Main entry point that configures transport mode (stdio/http)

**API Client Layer** (`app/api/client.py`)
- `GuruFocusClient` class handles all HTTP requests to GuruFocus API
- Centralized error handling and timeout management
- Supports stock summary, financials, analyst estimates, segments, and news

**Data Processing Layer** (`app/processors/`)
- Separate processors for each data type (stock, financials, analyst, segments, news, reports)
- Transform raw API responses into structured, concise formats
- Handle data validation and error cases

**Configuration** (`app/config.py`)
- Loads environment variables using python-dotenv
- Constructs API URLs with user token

### Data Flow

1. MCP tools receive requests with stock symbols
2. GuruFocusClient makes HTTP requests to GuruFocus API
3. Processors transform raw responses into structured data
4. Processed data returned via MCP tools

### Key Patterns

**Symbol Format**: US stocks use simple format (e.g., "AAPL"), international stocks use exchange prefix (e.g., "XTRA:DHL.DE")

**Async Processing**: All API calls are asynchronous using httpx and asyncio

**Error Handling**: Graceful degradation with informative error messages when API calls fail

**Data Processing**: Raw API responses are transformed into German-labeled, structured formats

## Environment Setup

Copy `app/.env.template` to `app/.env` and set:
- `GURUFOCUS_API_KEY` - Your GuruFocus API token
- `MCP_SERVER_MODE` - Transport mode (stdio/http)

## Testing

The project includes comprehensive pytest test suite with 94.01% code coverage:

**Test Structure:**
- `tests/unit/` - Unit tests for individual components (134 tests)
- `tests/integration/` - Integration tests for end-to-end workflows (13 tests)  
- `tests/e2e/` - End-to-end protocol tests for MCP communication
- `tests/conftest.py` - Shared fixtures and test configuration

**Unit Test Coverage:**
- `test_api_client.py` - Tests for GuruFocusClient HTTP requests, error handling, timeouts
- `test_stock_processor.py` - Tests for stock data transformation and edge cases
- `test_financials_processor.py` - Tests for financial data processing and REIT detection
- `test_analyst_processor.py` - Tests for analyst estimates processing
- `test_segments_processor.py` - Tests for business/geographical segments processing
- `test_news_processor.py` - Tests for news headlines processing
- `test_report_generator.py` - Tests for comprehensive report generation
- `test_data_models.py` - Tests for Pydantic data model validation
- `test_mcp_tools.py` - Tests for MCP tool functions with comprehensive mocking

**MCP Server Testing:**
- **Unit Tests**: Mock-based testing of individual MCP tool functions
- **Integration Tests**: Real MCP client/server communication using stdio transport
- **End-to-End Tests**: JSON-RPC protocol compliance and message handling
- **Docker Tests**: Containerized testing environment for consistent execution
- **CI/CD Pipeline**: Automated testing with GitHub Actions including security scans

**Test Dependencies:** pytest, pytest-asyncio, pytest-mock, pytest-cov, mcp (managed via uv dependency groups)

**Coverage Reporting:**
- Automatically generates terminal, HTML, and XML coverage reports
- HTML reports available at `htmlcov/index.html` after running tests
- Coverage configuration excludes test files, virtual environments, and common utility patterns
- Shows missing line numbers for uncovered code
- Precision set to 2 decimal places for accurate coverage percentages
- Current coverage: **94.01%** across all modules

**Docker Testing Environment:**
- `docker-compose.test.yml` - Multi-service testing setup
- `scripts/test-docker.sh` - Comprehensive testing script with multiple modes
- Separate containers for unit, integration, e2e, coverage, and quality testing
- Automated CI/CD pipeline with Docker-based testing