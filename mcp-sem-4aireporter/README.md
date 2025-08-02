# MCP SEM-4AI Reporter

MCP (Model Context Protocol) server for Test Management Dashboard providing comprehensive JIRA and Zephyr Scale integration with AI-powered insights and visual analytics.

## 🎯 Overview

This MCP server provides a complete test management solution integrating JIRA requirements/bugs with Zephyr Scale test cases and executions. Features AI-powered analytics, visual dashboards, and bidirectional test case management capabilities.

## 🚀 Key Features

### Test Management Tools
- **Test Case Creation**: Create comprehensive test cases with steps in Zephyr Scale
- **Requirement Linking**: Bidirectional linking between test cases and JIRA requirements
- **Test Execution Tracking**: Monitor test execution status and results
- **Bug Analysis**: Advanced JIRA bug tracking and trend analysis

### AI-Powered Analytics
- **Dynamic Future Outlook**: AI-generated project predictions and trends
- **Visual Analytics**: Interactive charts and dashboard data
- **Intelligent Insights**: AI-driven analysis of ticket content and patterns
- **Data Completeness**: Progress statistics and completion metrics

### Available MCP Tools (11 Total)
1. **`get_requirements`** - Retrieve JIRA Epics and Stories
2. **`get_test_cases`** - Get Zephyr Scale test cases
3. **`create_test_case`** - Create new test cases with validation and steps
4. **`link_test_case_to_requirement`** - Link test cases to requirements bidirectionally
5. **`get_test_executions`** - Retrieve test execution data
6. **`get_bugs`** - Get JIRA bug reports
7. **`get_dynamic_future_outlook`** - AI-generated project predictions
8. **`get_data_completeness_stats`** - Progress and completion metrics
9. **`get_visual_analytics_data`** - Chart data for dashboards
10. **`get_intelligent_insights`** - AI insights from content analysis
11. **`get_test_case_links`** - Debug tool for link verification

## 🏁 Quick Start

### Prerequisites
- Python 3.12+
- JIRA instance with API access
- Zephyr Scale license and API access
- Docker and Docker Compose (for containerized deployment)

### Local Development

1. **Setup Environment**
   ```bash
   cd mcp-sem-4aireporter
   cp .env.template .env
   # Edit .env with your credentials
   uv sync
   ```

2. **Run Server**
   ```bash
   uv run python src/main.py
   ```

### Docker Deployment

#### Local Development Mode (MCP Protocol)
1. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your actual credentials
   ```

2. **Build and Run**
   ```bash
   docker-compose up -d
   ```

3. **Monitor**
   ```bash
   # View logs
   docker-compose logs -f
   
   # Check status
   docker-compose ps
   
   # Stop services
   docker-compose down
   ```

#### Server Deployment Mode (REST API)

**Perfect for server deployment with simple HTTP REST API access:**

1. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your actual credentials
   # Set MCP_TRANSPORT=rest for REST API mode
   ```

2. **Deploy REST API Server**
   ```bash
   # Local development
   MCP_TRANSPORT=rest uv run python src/main.py
   
   # Docker deployment
   docker-compose -f docker-compose-rest.yml up -d
   ```

3. **Use Simple REST Endpoints**
   ```bash
   # API Documentation (Swagger UI)
   curl http://your-server:8080/docs
   
   # Health check
   curl http://your-server:8080/health
   
   # Get requirements
   curl http://your-server:8080/api/requirements/SEM
   
   # Get bugs
   curl http://your-server:8080/api/bugs/SEM
   
   # Get test cases
   curl http://your-server:8080/api/test-cases/SEM
   
   # Create test case
   curl -X POST http://your-server:8080/api/test-cases \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Login Test",
       "objective": "Test user login functionality",
       "project_id": "SEM"
     }'
   
   # Link test case to requirement
   curl -X POST http://your-server:8080/api/test-cases/link \
     -H "Content-Type: application/json" \
     -d '{
       "test_case_key": "SEM-T123",
       "jira_issue_id": "SEM-456"
     }'
   
   # Get analytics
   curl http://your-server:8080/api/analytics/insights/SEM
   ```

### Available REST Endpoints

- **`GET /docs`** - Interactive API documentation (Swagger UI)
- **`GET /health`** - Health check endpoint
- **`GET /api/tools`** - List all available tools
- **`GET /api/requirements/{project_id}`** - Get JIRA requirements/epics
- **`GET /api/test-cases/{project_id}`** - Get Zephyr test cases  
- **`GET /api/bugs/{project_id}`** - Get JIRA bugs
- **`GET /api/test-executions/{project_id}`** - Get test execution data
- **`POST /api/test-cases`** - Create new test case
- **`POST /api/test-cases/link`** - Link test case to requirement
- **`GET /api/analytics/insights/{project_id}`** - AI-powered insights
- **`GET /api/analytics/visual/{project_id}`** - Visual analytics data
- **`GET /api/analytics/outlook/{project_id}`** - Future outlook predictions
- **`GET /api/analytics/completeness/{project_id}`** - Data completeness stats

4. **Server Management**
   ```bash
   # Monitor server logs
   docker-compose -f docker-compose-server.yml logs -f
   
   # Check server status
   docker-compose -f docker-compose-server.yml ps
   
   # Stop server
   docker-compose -f docker-compose-server.yml down
   
   # Restart server
   docker-compose -f docker-compose-server.yml restart
   ```

## ⚙️ Configuration

### Environment Variables

**Required Configuration:**
```env
# JIRA Configuration
JIRA_BASE_URL="https://your-domain.atlassian.net/rest/api/3"
JIRA_API_USER="your-email@domain.com"
JIRA_API_KEY="your-jira-api-token"
JIRA_BASIC_AUTH_TOKEN="your-base64-encoded-credentials"

# Zephyr Scale Configuration  
ZEPHYR_BASE_URL="https://api.zephyrscale.smartbear.com/v2"
ZEPHYR_BEARER_TOKEN="your-zephyr-bearer-token"

# Project Configuration
PROJECT_ID="SEM"
```

**Optional Configuration:**
```env
# Docker-specific
PYTHONPATH="/app"
PYTHONUNBUFFERED="1"

# Server Transport Mode
# stdio = MCP protocol via stdin/stdout (default)
# http = HTTP API server on port 8000
# sse = Server-Sent Events on port 8000
MCP_TRANSPORT="stdio"

# Logging
LOG_LEVEL="INFO"

# Performance
HTTP_TIMEOUT="30"
```

### Authentication Setup

**JIRA Authentication:**
```bash
# Generate base64 token
echo -n "your-email@domain.com:your-api-key" | base64
# Add result to JIRA_BASIC_AUTH_TOKEN
```

**Zephyr Scale Authentication:**
1. Go to Zephyr Scale → API Access Tokens
2. Generate new token with required permissions
3. Copy token to `ZEPHYR_BEARER_TOKEN`

## 🛠️ API Integration

### JIRA REST API v3
- **Authentication**: Basic Auth with API token
- **Endpoints**: Issues, Projects, Fields, Links
- **Features**: Epic/Story retrieval, Bug tracking, Issue linking

### Zephyr Scale API v2
- **Authentication**: Bearer token
- **Endpoints**: Test cases, Test executions, Test steps, Links
- **Features**: Test case creation, Requirement linking, Test step management

## 🤖 AI Agent Workflows

### Test Case Creation Workflow
1. **Planning**: Use `get_requirements()` to identify target requirements
2. **Creation**: Use `create_test_case()` with proper validation and steps
3. **Linking**: Use `link_test_case_to_requirement()` for traceability
4. **Verification**: Use `get_test_case_links()` to confirm bidirectional links

### Dashboard Analytics Workflow
1. **Data Collection**: Gather requirements, test cases, executions, and bugs
2. **AI Analysis**: Use `get_intelligent_insights()` for content analysis
3. **Future Planning**: Use `get_dynamic_future_outlook()` for predictions
4. **Visualization**: Use `get_visual_analytics_data()` for charts

## 🐳 Docker Configuration

### Container Features
- **Base Image**: Python 3.12 slim for minimal footprint
- **Package Manager**: UV for fast dependency installation
- **Security**: Non-root user execution
- **Health Checks**: Python import validation every 30s
- **Resource Limits**: 512MB memory, 0.5 CPU cores
- **Logging**: JSON format with rotation (10MB max, 3 files)

### Persistent Data
- **Memory Storage**: `/app/memories.json` for ken-you-remember integration
- **Reflection Storage**: `/app/reflections.json` for ken-you-reflect integration
- **Logs**: `/app/logs/` directory for debugging and monitoring
- **Volume Mounts**: Configured for data persistence across container restarts

### Networking
- **Internal Network**: `mcp-network` bridge for service isolation
- **Health Monitoring**: Built-in health checks with retry logic
- **Service Discovery**: Container name resolution within network

## 🧪 Development

### Code Quality
```bash
# Lint and format
ruff check .
ruff format .

# Auto-fix issues
ruff check --fix .
```

### Testing with MCP Inspector
```bash
# Interactive testing interface
npx @modelcontextprotocol/inspector@latest uv run python src/main.py
```

### Manual Testing
```bash
# Test server initialization
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | uv run python src/main.py
```

## 🔧 Troubleshooting

### Common Issues

**Authentication Errors:**
- Verify API tokens are valid and not expired
- Check base URL format includes `/rest/api/3` for JIRA
- Ensure user has proper read/write permissions

**Link Visibility Issues:**
- Enable Zephyr Scale panel in JIRA issue view
- Configure JIRA add-on settings for Zephyr integration
- Verify bidirectional linking permissions in both systems

**Docker Issues:**
- Check `.env` file exists and has correct permissions
- Verify port conflicts (default 8000)
- Monitor resource usage with `docker stats`

### Debugging

**Enable Debug Logging:**
```env
LOG_LEVEL="DEBUG"
```

**Docker Logs:**
```bash
# Real-time logs
docker-compose logs -f

# Container-specific logs
docker-compose logs mcp-sem-4aireporter

# System resource monitoring
docker stats mcp-sem-4aireporter
```

**Health Check Status:**
```bash
# Check container health
docker inspect mcp-sem-4aireporter | grep -A 10 Health
```

## 📁 Project Structure

```
mcp-sem-4aireporter/
├── src/
│   ├── __init__.py
│   └── main.py              # Main MCP server with 11 tools
├── .env.template            # Environment configuration template
├── .dockerignore           # Docker build exclusions
├── Dockerfile              # Multi-stage Python 3.12 container
├── docker-compose.yml      # Complete orchestration setup
├── pyproject.toml          # Python project configuration
├── uv.lock                 # Dependency lock file
├── memories.json           # ken-you-remember storage
├── reflections.json        # ken-you-reflect storage
├── MCP_SPEC.md            # Original specification document
└── README.md              # This file
```

## 🔗 Integration Examples

### MCP Tool Usage
```python
# Get requirements for planning
await mcp.call_tool("get_requirements", {"project_id": "SEM"})

# Create test case with steps
await mcp.call_tool("create_test_case", {
    "project_id": "SEM",
    "name": "User Login Validation",
    "objective": "Verify user authentication works correctly",
    "test_steps": [
        {"description": "Navigate to login page", "expected_result": "Login form displayed"},
        {"description": "Enter valid credentials", "expected_result": "User logged in successfully"}
    ]
})

# Link test case to requirement
await mcp.call_tool("link_test_case_to_requirement", {
    "test_case_key": "SEM-T123",
    "jira_issue_id": "SEM-456"
})
```

### Docker Health Monitoring
```bash
# Set up monitoring alerts
docker run -d --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower mcp-sem-4aireporter

# Custom health check script
curl -f http://localhost:8000/health || exit 1
```

## 📚 Documentation References

- [MCP_SPEC.md](./MCP_SPEC.md) - Original Test Reporting Dashboard specification
- [Model Context Protocol](https://github.com/modelcontextprotocol/specification) - Official MCP docs
- [JIRA REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) - JIRA integration
- [Zephyr Scale API v2](https://support.smartbear.com/zephyr-scale-cloud/api-docs/) - Zephyr integration
- [Docker Compose](https://docs.docker.com/compose/) - Container orchestration

## 🤝 Contributing

1. Follow existing code style (enforced by ruff)
2. Maintain MCP protocol compliance
3. Test with both JIRA and Zephyr data sources
4. Update documentation for new features
5. Include Docker compatibility for new tools

## 📄 License

This project follows the same license as the parent MCP server repository.