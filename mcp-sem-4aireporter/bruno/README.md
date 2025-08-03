# Bruno API Collection for MCP SEM-4AI Reporter

This Bruno collection provides comprehensive testing for the MCP SEM-4AI Reporter REST API.

## Setup

1. **Install Bruno**: [Download Bruno](https://usebruno.com/)
2. **Open Collection**: File → Open Collection → Select the `bruno` folder
3. **Select Environment**: Choose between `Local` or `Docker` environment

## Environments

### Local Environment
- **Base URL**: `http://localhost:8080`
- **Use case**: Testing against locally running server

### Docker Environment  
- **Base URL**: `http://mcp-rest-api:8080`
- **Use case**: Testing from within Docker network

## Available Requests

### Core API
- **Health Check** - Test server health
- **API Root** - Get API information
- **List Tools** - Get all available MCP tools

### Data Retrieval
- **Get Requirements** - Fetch JIRA requirements/epics
- **Get Bugs** - Fetch JIRA bugs
- **Get Test Cases** - Fetch Zephyr test cases
- **Get Test Executions** - Fetch test execution data

### Test Management
- **Create Test Case** - Create new test case with steps
- **Link Test Case to Requirement** - Link test case to JIRA issue

### Analytics (AI-Powered)
- **Get Insights** - AI-generated project insights
- **Get Visual Analytics** - Chart data for dashboards
- **Get Future Outlook** - AI predictions and trends
- **Get Data Completeness** - Progress statistics

### Generic
- **Generic Tool Call** - Call any MCP tool with custom parameters

## Usage

1. **Start the server**:
   ```bash
   # Local development
   MCP_TRANSPORT=rest uv run python src/main.py
   
   # Docker deployment
   docker-compose -f docker-compose-rest.yml up -d
   ```

2. **Select environment** in Bruno (Local or Docker)

3. **Run requests** individually or as a collection

## Expected Responses

### Successful Response (200)
```json
{
  "success": true,
  "data": {
    // MCP tool response data
  }
}
```

### MCP Server Unavailable (503)
```json
{
  "detail": "MCP server not available. Please check server configuration and credentials."
}
```

## Testing Notes

- Health check and API root should always work (200)
- Other endpoints return 503 if MCP backend is not configured
- Requires valid JIRA and Zephyr credentials in `.env` file for full functionality
- All requests include automated tests for status codes and response structure

## Configuration

Update the `project_id` variable in environments to test different projects:
- Default: `SEM`
- Change to your project key as needed