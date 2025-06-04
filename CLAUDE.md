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

### Testing (mcp-gurufocus only)
- `cd mcp-gurufocus && uv run --group test pytest` - Run all tests with coverage
- `cd mcp-gurufocus && uv run --group test pytest tests/unit/` - Run only unit tests
- `cd mcp-gurufocus && uv run --group test pytest tests/integration/` - Run only integration tests
- `cd mcp-gurufocus && uv run --group test pytest tests/e2e/` - Run only end-to-end tests

### Running MCP Servers
- `cd mcp-gurufocus && uv run python app/main.py` - Run GuruFocus MCP server
- `cd mcp-tg-jira-seminarapp && uv run python src/main.py` - Run JIRA/Zephyr MCP server

### Creating New MCP Servers
- `./new_mcp_server.sh <server-name>` - Bootstrap new MCP server with standard structure

## Architecture Overview

This is a **multi-service MCP (Model Context Protocol) server** repository containing independent microservices that provide structured API access through MCP tools.

### Repository Structure

**Root Level:**
- Two independent MCP servers: `mcp-gurufocus/` and `mcp-tg-jira-seminarapp/`
- `new_mcp_server.sh` - Script for bootstrapping new MCP servers
- Each service uses Python 3.12, uv package manager, and follows similar architectural patterns

### MCP GuruFocus Service (`mcp-gurufocus/`)

**Purpose:** Financial data integration service providing access to GuruFocus API

**Architecture:**
- **MCP Server** (`app/main.py`) - FastMCP framework exposing financial data tools
- **API Client** (`app/api/client.py`) - GuruFocusClient handles HTTP requests with error handling
- **Data Processors** (`app/processors/`) - Transform raw API responses into structured formats
- **Configuration** (`app/config.py`) - Environment variable management

**Key Features:**
- Stock information, financial metrics, analyst estimates, segment data, news
- Symbol format: US stocks (e.g., "AAPL"), international with exchange prefix (e.g., "XTRA:DHL.DE")
- German-labeled output formatting
- Comprehensive test suite with 94.01% coverage

### MCP TG JIRA SeminarApp Service (`mcp-tg-jira-seminarapp/`)

**Purpose:** JIRA and Zephyr integration for test management

**Architecture:**
- **MCP Server** (`src/main.py`) - Single-file service with tool definitions
- **JIRA Integration** - Project info, requirements (Epics/Stories), bug tracking
- **Zephyr Integration** - Test case and test execution management

**Key Features:**
- Project discovery, requirement/bug retrieval, test case/execution management
- Basic auth for JIRA, Bearer token for Zephyr
- Compact data transformation for efficient responses

### Common Patterns

**Technology Stack:**
- Python 3.12 with uv package management
- FastMCP framework for MCP protocol implementation
- httpx for async HTTP requests
- python-dotenv for environment configuration
- ruff for code quality

**Environment Setup:**
Each service requires `.env` file with API credentials (see respective `.env.template` files)

**Data Flow Pattern:**
1. MCP tools receive structured requests
2. HTTP clients make API calls with error handling
3. Data processors transform responses
4. Structured data returned via MCP protocol

**Development Workflow:**
- Individual virtual environments per service
- Consistent project structure with pyproject.toml
- Standard ruff configuration for code quality
- Service-specific testing strategies