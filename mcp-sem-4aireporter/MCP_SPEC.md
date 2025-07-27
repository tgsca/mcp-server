# MCP Server Specification for Test Reporting Dashboard

## 🎯 Overview

This specification defines the exact requirements for building MCP (Model Context Protocol) servers that integrate with the Test Reporting Dashboard. Your MCP server must implement these specifications precisely to ensure seamless data integration and AI analysis.

## 📋 Core Requirements

### Supported Data Types
Your MCP server must support one or more of these data types:
- `requirements` - User stories, epics, functional requirements
- `test_cases` - Manual and automated test cases
- `test_executions` - Test run results and execution data  
- `bugs` - Defects, issues, and bug reports

### Resource URI Pattern
```
quality://{server_name}/{data_type}/{project_id}
```

**Examples:**
- `quality://tg-jira-seminarapp/requirements/SEM`
- `quality://tg-jira-seminarapp/test_cases/SEM`
- `quality://tg-jira-seminarapp/bugs/SEM`
- `quality://tg-jira-seminarapp/test_executions/SEM`

## 🏗️ Response Structure

### Root Response Format
```json
{
  "uri": "quality://server-name/data-type/project-id",
  "name": "Human readable name",
  "description": "Description of the data resource",
  "mimeType": "application/json",
  "metadata": {
    "source_server": "server-name",
    "server_type": "jira|zephyr|github|jenkins|custom",
    "project_id": "PROJECT_ID",
    "data_type": "requirements|test_cases|test_executions|bugs",
    "sync_time": "2025-07-27T16:30:00.000Z",
    "total_count": 25,
    "last_modified": "2025-07-27T15:45:00.000Z",
    "schema_version": "1.0",
    "additional_info": {}
  },
  "items": [
    // Array of data items (see schemas below)
  ]
}
```

## 📊 Data Item Schemas

### Base Schema (All Items)
All data items must inherit these fields:
```json
{
  "id": "string (required) - Unique identifier",
  "title": "string (required) - Item title/summary",
  "description": "string (required) - Detailed description",
  "status": "string (required) - Current status",
  "priority": "string (required) - Priority level",
  "created_date": "ISO 8601 datetime (required)",
  "updated_date": "ISO 8601 datetime (required)",
  "source_url": "string (optional) - Link to original item",
  "tags": ["array of strings (optional)"],
  "custom_fields": {"object (optional) - Additional fields"}
}
```

### Requirements Schema
```json
{
  // Base fields (above) +
  "requirement_type": "FUNCTIONAL|NON_FUNCTIONAL|BUSINESS (default: FUNCTIONAL)",
  "acceptance_criteria": ["array of strings (optional)"],
  "story_points": "integer (optional) - Estimate points",
  "epic_id": "string (optional) - Parent epic ID",
  "linked_test_cases": ["array of test case IDs (optional)"],
  "business_value": "integer (optional) - Business value score",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL (default: MEDIUM)"
}
```

### Test Cases Schema
```json
{
  // Base fields (above) +
  "test_type": "MANUAL|AUTOMATED|API|UI (default: MANUAL)",
  "automation_status": "AUTOMATED|NOT_AUTOMATED|PLANNED (default: NOT_AUTOMATED)",
  "requirement_id": "string (optional) - Linked requirement ID",
  "test_steps": ["array of strings (optional)"],
  "expected_results": ["array of strings (optional)"],
  "environment": "DEVELOPMENT|TESTING|STAGING|PRODUCTION (default: TESTING)",
  "component": "string (optional) - Component/module name"
}
```

### Test Executions Schema
```json
{
  // Base fields (above) +
  "test_case_id": "string (required) - Linked test case ID",
  "execution_status": "PASS|FAIL|BLOCKED|NOT_EXECUTED|SKIP (required)",
  "executed_by": "string (required) - Executor name/email",
  "execution_time": "ISO 8601 datetime (optional) - When executed",
  "duration_seconds": "integer (optional) - Execution duration",
  "environment": "DEVELOPMENT|TESTING|STAGING|PRODUCTION (default: TESTING)",
  "build_version": "string (optional) - Build/version tested",
  "failure_reason": "string (optional) - Reason for failure",
  "attachments": ["array of attachment URLs (optional)"]
}
```

### Bugs Schema
```json
{
  // Base fields (above) +
  "bug_type": "FUNCTIONAL|PERFORMANCE|SECURITY|UI|DATA (default: FUNCTIONAL)",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW (required)",
  "environment": "DEVELOPMENT|TESTING|STAGING|PRODUCTION (required)",
  "component": "string (optional) - Affected component",
  "reproduction_steps": ["array of strings (optional)"],
  "expected_behavior": "string (optional)",
  "actual_behavior": "string (optional)",
  "resolution": "string (optional) - How it was resolved",
  "found_in_version": "string (optional)",
  "fixed_in_version": "string (optional)"
}
```

## 🔄 Data Type Mapping Guidelines

### JIRA → Requirements Mapping
```python
# JIRA Issue → Requirement
{
  "id": jira_issue.key,                    # "SEM-123"
  "title": jira_issue.fields.summary,
  "description": jira_issue.fields.description or "",
  "status": jira_issue.fields.status.name,
  "priority": jira_issue.fields.priority.name if jira_issue.fields.priority else "MEDIUM",
  "created_date": jira_issue.fields.created,
  "updated_date": jira_issue.fields.updated,
  "source_url": f"{jira_base_url}/browse/{jira_issue.key}",
  "requirement_type": map_issue_type(jira_issue.fields.issuetype.name),
  "story_points": getattr(jira_issue.fields, 'customfield_10016', None),  # Adjust field ID
  "epic_id": getattr(jira_issue.fields, 'parent', {}).get('key') if hasattr(jira_issue.fields, 'parent') else None,
  "acceptance_criteria": parse_acceptance_criteria(jira_issue.fields.description),
  "business_value": calculate_business_value(jira_issue),
  "risk_level": map_priority_to_risk(jira_issue.fields.priority.name if jira_issue.fields.priority else "MEDIUM")
}
```

### JIRA → Bugs Mapping
```python
# JIRA Bug → Bug
{
  "id": jira_issue.key,
  "title": jira_issue.fields.summary,
  "description": jira_issue.fields.description or "",
  "status": jira_issue.fields.status.name,
  "priority": jira_issue.fields.priority.name if jira_issue.fields.priority else "MEDIUM",
  "created_date": jira_issue.fields.created,
  "updated_date": jira_issue.fields.updated,
  "source_url": f"{jira_base_url}/browse/{jira_issue.key}",
  "bug_type": map_bug_type(jira_issue.fields.issuetype.name),
  "severity": map_priority_to_severity(jira_issue.fields.priority.name if jira_issue.fields.priority else "MEDIUM"),
  "environment": extract_environment(jira_issue.fields.environment or jira_issue.fields.description),
  "component": jira_issue.fields.components[0].name if jira_issue.fields.components else None,
  "reproduction_steps": parse_reproduction_steps(jira_issue.fields.description),
  "resolution": jira_issue.fields.resolution.name if jira_issue.fields.resolution else None
}
```

### Zephyr → Test Cases Mapping
```python
# Zephyr Test → Test Case
{
  "id": zephyr_test.key,
  "title": zephyr_test.name,
  "description": zephyr_test.objective or "",
  "status": "ACTIVE" if zephyr_test.status == "Approved" else "DRAFT",
  "priority": zephyr_test.priority or "MEDIUM",
  "created_date": zephyr_test.createdOn,
  "updated_date": zephyr_test.modifiedOn,
  "source_url": f"{zephyr_base_url}/testcase/{zephyr_test.key}",
  "test_type": "AUTOMATED" if zephyr_test.automated else "MANUAL",
  "automation_status": "AUTOMATED" if zephyr_test.automated else "NOT_AUTOMATED",
  "test_steps": [step.description for step in zephyr_test.testScript.steps] if zephyr_test.testScript else [],
  "expected_results": [step.expectedResult for step in zephyr_test.testScript.steps] if zephyr_test.testScript else [],
  "component": zephyr_test.component.name if zephyr_test.component else None,
  "requirement_id": extract_requirement_links(zephyr_test.links)
}
```

### Zephyr → Test Executions Mapping
```python
# Zephyr Execution → Test Execution
{
  "id": f"{zephyr_execution.testCase.key}-{zephyr_execution.id}",
  "title": f"Execution of {zephyr_execution.testCase.name}",
  "description": f"Test execution for {zephyr_execution.testCase.name}",
  "status": "COMPLETED",
  "priority": "MEDIUM",
  "created_date": zephyr_execution.executedOn,
  "updated_date": zephyr_execution.executedOn,
  "test_case_id": zephyr_execution.testCase.key,
  "execution_status": map_zephyr_status(zephyr_execution.executionStatus.name),
  "executed_by": zephyr_execution.executedBy.displayName,
  "execution_time": zephyr_execution.executedOn,
  "environment": zephyr_execution.environment.name if zephyr_execution.environment else "TESTING",
  "build_version": zephyr_execution.testCycle.build if zephyr_execution.testCycle else None,
  "failure_reason": zephyr_execution.comment if zephyr_execution.executionStatus.name == "FAIL" else None
}
```

## 🛡️ Validation Rules

### Required Field Validation
```python
def validate_base_item(item):
    required_fields = ["id", "title", "description", "status", "priority", "created_date", "updated_date"]
    for field in required_fields:
        if field not in item or not item[field]:
            raise ValueError(f"Required field '{field}' is missing or empty")
    
    # Validate datetime format
    try:
        datetime.fromisoformat(item["created_date"].replace('Z', '+00:00'))
        datetime.fromisoformat(item["updated_date"].replace('Z', '+00:00'))
    except ValueError:
        raise ValueError("Date fields must be in ISO 8601 format")

def validate_requirement(item):
    validate_base_item(item)
    if "requirement_type" in item:
        if item["requirement_type"] not in ["FUNCTIONAL", "NON_FUNCTIONAL", "BUSINESS"]:
            raise ValueError("Invalid requirement_type")
    if "risk_level" in item:
        if item["risk_level"] not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            raise ValueError("Invalid risk_level")

def validate_bug(item):
    validate_base_item(item)
    if "severity" not in item:
        raise ValueError("Bug items must have severity field")
    if item["severity"] not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        raise ValueError("Invalid severity value")
    if "environment" not in item:
        raise ValueError("Bug items must have environment field")

def validate_test_execution(item):
    validate_base_item(item)
    if "test_case_id" not in item or not item["test_case_id"]:
        raise ValueError("Test execution must have test_case_id")
    if "execution_status" not in item:
        raise ValueError("Test execution must have execution_status")
    if item["execution_status"] not in ["PASS", "FAIL", "BLOCKED", "NOT_EXECUTED", "SKIP"]:
        raise ValueError("Invalid execution_status")
    if "executed_by" not in item or not item["executed_by"]:
        raise ValueError("Test execution must have executed_by")
```

## 🔧 Implementation Examples

### Basic MCP Server Structure
```python
from mcp.server import Server
from mcp.types import Resource, TextContent
import json
from datetime import datetime
from typing import List, Dict, Any

class QualityDataMCPServer:
    def __init__(self, server_name: str, project_id: str):
        self.server_name = server_name
        self.project_id = project_id
        self.server = Server("quality-data-server")
        
    @self.server.list_resources()
    async def list_resources() -> List[Resource]:
        """List available resources"""
        return [
            Resource(
                uri=f"quality://{self.server_name}/requirements/{self.project_id}",
                name="Requirements",
                description=f"Requirements and user stories for {self.project_id}",
                mimeType="application/json"
            ),
            Resource(
                uri=f"quality://{self.server_name}/test_cases/{self.project_id}",
                name="Test Cases", 
                description=f"Test cases for {self.project_id}",
                mimeType="application/json"
            ),
            Resource(
                uri=f"quality://{self.server_name}/bugs/{self.project_id}",
                name="Bugs",
                description=f"Bugs and defects for {self.project_id}",
                mimeType="application/json"
            ),
            Resource(
                uri=f"quality://{self.server_name}/test_executions/{self.project_id}",
                name="Test Executions",
                description=f"Test execution results for {self.project_id}",
                mimeType="application/json"
            )
        ]
    
    @self.server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read resource data"""
        if not uri.startswith(f"quality://{self.server_name}/"):
            raise ValueError(f"Unknown resource: {uri}")
        
        parts = uri.split("/")
        data_type = parts[3]  # requirements, test_cases, bugs, test_executions
        project_id = parts[4]
        
        if project_id != self.project_id:
            raise ValueError(f"Unknown project: {project_id}")
        
        if data_type == "requirements":
            data = await self.fetch_requirements()
        elif data_type == "test_cases":
            data = await self.fetch_test_cases()
        elif data_type == "bugs":
            data = await self.fetch_bugs()
        elif data_type == "test_executions":
            data = await self.fetch_test_executions()
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        return json.dumps(data, default=str)
```

### Data Fetching Template
```python
async def fetch_requirements(self) -> Dict[str, Any]:
    """Fetch requirements from JIRA"""
    # Your JIRA API calls here
    jira_issues = await self.jira_client.get_issues(
        jql=f"project = {self.project_id} AND issuetype IN (Story, Epic, Requirement)"
    )
    
    items = []
    for issue in jira_issues:
        item = {
            "id": issue.key,
            "title": issue.fields.summary,
            "description": issue.fields.description or "",
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "MEDIUM",
            "created_date": issue.fields.created,
            "updated_date": issue.fields.updated,
            "source_url": f"{self.jira_base_url}/browse/{issue.key}",
            "tags": [label for label in getattr(issue.fields, 'labels', [])],
            "custom_fields": {},
            "requirement_type": self.map_issue_type_to_requirement_type(issue.fields.issuetype.name),
            "acceptance_criteria": self.parse_acceptance_criteria(issue.fields.description),
            "story_points": getattr(issue.fields, 'customfield_10016', None),
            "epic_id": getattr(issue.fields, 'parent', {}).get('key') if hasattr(issue.fields, 'parent') else None,
            "linked_test_cases": [],
            "business_value": self.calculate_business_value(issue),
            "risk_level": self.map_priority_to_risk_level(issue.fields.priority.name if issue.fields.priority else "MEDIUM")
        }
        items.append(item)
    
    return {
        "uri": f"quality://{self.server_name}/requirements/{self.project_id}",
        "name": f"Requirements from {self.server_name}",
        "description": f"Requirements and user stories for project {self.project_id}",
        "mimeType": "application/json",
        "metadata": {
            "source_server": self.server_name,
            "server_type": "jira",
            "project_id": self.project_id,
            "data_type": "requirements",
            "sync_time": datetime.now().isoformat() + "Z",
            "total_count": len(items),
            "last_modified": max(item["updated_date"] for item in items) if items else None,
            "schema_version": "1.0",
            "additional_info": {
                "jira_project_key": self.project_id,
                "issue_types": list(set(self.map_issue_type_to_requirement_type(issue.fields.issuetype.name) for issue in jira_issues))
            }
        },
        "items": items
    }
```

## 🗺️ Helper Functions

### Priority and Status Mapping
```python
def map_jira_priority_to_standard(jira_priority: str) -> str:
    """Map JIRA priority to standard priority"""
    mapping = {
        "Highest": "CRITICAL",
        "High": "HIGH", 
        "Medium": "MEDIUM",
        "Low": "LOW",
        "Lowest": "LOW"
    }
    return mapping.get(jira_priority, "MEDIUM")

def map_jira_status_to_standard(jira_status: str) -> str:
    """Map JIRA status to standard status"""
    # Keep original status but normalize common ones
    status_mapping = {
        "To Do": "TODO",
        "In Progress": "IN_PROGRESS",
        "Done": "DONE",
        "Closed": "CLOSED",
        "Open": "OPEN",
        "Resolved": "RESOLVED"
    }
    return status_mapping.get(jira_status, jira_status.upper().replace(" ", "_"))

def map_zephyr_execution_status(zephyr_status: str) -> str:
    """Map Zephyr execution status to standard"""
    mapping = {
        "PASS": "PASS",
        "FAIL": "FAIL", 
        "WIP": "NOT_EXECUTED",
        "BLOCKED": "BLOCKED",
        "NOT_EXECUTED": "NOT_EXECUTED",
        "UNEXECUTED": "NOT_EXECUTED"
    }
    return mapping.get(zephyr_status.upper(), "NOT_EXECUTED")

def extract_acceptance_criteria(description: str) -> List[str]:
    """Extract acceptance criteria from description"""
    if not description:
        return []
    
    # Look for common patterns
    criteria = []
    lines = description.split('\n')
    
    in_criteria_section = False
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['acceptance criteria', 'acceptance', 'criteria']):
            in_criteria_section = True
            continue
        
        if in_criteria_section:
            if line.startswith('*') or line.startswith('-') or line.startswith('•'):
                criteria.append(line[1:].strip())
            elif line.startswith(('Given', 'When', 'Then', 'And')):
                criteria.append(line)
            elif line == '' and criteria:
                break  # End of criteria section
    
    return criteria

def calculate_business_value(jira_issue) -> int:
    """Calculate business value score"""
    # Example scoring based on priority and issue type
    priority_scores = {"CRITICAL": 100, "HIGH": 80, "MEDIUM": 60, "LOW": 40}
    type_scores = {"Epic": 20, "Story": 10, "Task": 5}
    
    priority = jira_issue.fields.priority.name if jira_issue.fields.priority else "MEDIUM"
    issue_type = jira_issue.fields.issuetype.name
    
    base_score = priority_scores.get(priority, 60)
    type_bonus = type_scores.get(issue_type, 5)
    
    return min(base_score + type_bonus, 100)
```

## ✅ Testing Your MCP Server

### Manual Testing Commands
```bash
# Test resource listing
echo '{"jsonrpc": "2.0", "id": 1, "method": "resources/list"}' | your-mcp-server

# Test resource reading
echo '{"jsonrpc": "2.0", "id": 2, "method": "resources/read", "params": {"uri": "quality://your-server/requirements/SEM"}}' | your-mcp-server
```

### Validation Checklist
- [ ] ✅ All required fields are present
- [ ] ✅ Date fields are in ISO 8601 format
- [ ] ✅ Enum values match specification exactly
- [ ] ✅ Resource URIs follow the exact pattern
- [ ] ✅ Metadata includes all required fields
- [ ] ✅ Items array contains valid objects
- [ ] ✅ No extra/unknown fields in critical paths
- [ ] ✅ Error handling for missing data
- [ ] ✅ Proper JSON serialization

### Integration Testing
```python
# Test with Test Reporting Dashboard
import requests

# Register your server
response = requests.post("http://localhost:8000/api/mcp/servers/register", params={
    "server_name": "your-server-name",
    "project_id": "SEM"
}, json={"env_vars": {}})

# Test sync
response = requests.post("http://localhost:8000/api/mcp/projects/SEM/sync")
print(response.json())

# Check data
response = requests.get("http://localhost:8000/api/mcp/projects/SEM/summary")
print(response.json())
```

## 🚨 Common Pitfalls

### ❌ Wrong Resource URI Format
```python
# Wrong
"quality://server/SEM/requirements"

# Correct  
"quality://server/requirements/SEM"
```

### ❌ Invalid Date Format
```python
# Wrong
"created_date": "2025-07-27 16:30:00"

# Correct
"created_date": "2025-07-27T16:30:00.000Z"
```

### ❌ Missing Required Fields
```python
# Wrong - missing required fields
{
    "id": "REQ-001",
    "title": "Some requirement"
    # Missing: description, status, priority, dates
}

# Correct
{
    "id": "REQ-001",
    "title": "Some requirement",
    "description": "Detailed description",
    "status": "IN_PROGRESS", 
    "priority": "HIGH",
    "created_date": "2025-07-27T16:30:00.000Z",
    "updated_date": "2025-07-27T16:30:00.000Z"
}
```

### ❌ Invalid Enum Values
```python
# Wrong
"execution_status": "PASSED"  # Should be "PASS"
"severity": "MAJOR"           # Should be "HIGH" 
"data_type": "tests"          # Should be "test_cases"

# Correct
"execution_status": "PASS"
"severity": "HIGH"
"data_type": "test_cases"
```

## 🔗 Integration Points

Your MCP server will integrate with:

1. **MCP Registration**: `/api/mcp/servers/register`
2. **Data Sync**: `/api/mcp/projects/{project_id}/sync` 
3. **Data Retrieval**: `/api/mcp/projects/{project_id}/data/{data_type}`
4. **AI Analysis**: Data feeds into Claude for story generation
5. **Dashboard Display**: Real-time metrics and visualizations

## 📚 References

- **Schema Source**: `backend/models/mcp_models.py`
- **API Documentation**: `backend/docs/MCP_ARCHITECTURE.md`
- **Integration Examples**: `backend/services/mcp_client_manager_safe.py`

## 🎯 Success Criteria

Your MCP server is ready when:
- [ ] All resource URIs return valid data
- [ ] Data validation passes 100%
- [ ] Integration test shows real data counts
- [ ] AI story generation works with your data
- [ ] No errors in Test Reporting Dashboard logs

---

**Follow this specification exactly and your MCP server will integrate seamlessly with the Test Reporting Dashboard! 🚀**