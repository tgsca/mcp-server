import os
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Environment variables
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_BASIC_AUTH_TOKEN = os.getenv("JIRA_BASIC_AUTH_TOKEN")
ZEPHYR_BASE_URL = os.getenv("ZEPHYR_BASE_URL")
ZEPHYR_BEARER_TOKEN = os.getenv("ZEPHYR_BEARER_TOKEN")

# Server configuration
SERVER_NAME = "sem-4aireporter"
PROJECT_ID = "SEM"  # Default project ID

# Initialize FastMCP server
mcp = FastMCP("mcp-sem-4aireporter")


async def request_jira(url: str, payload: Dict[str, Any]) -> Dict[str, Any] | None:
    """Make authenticated request to JIRA API"""
    # Debug: Check if environment variables are loaded
    if not JIRA_BASE_URL or not JIRA_BASIC_AUTH_TOKEN:
        print(f"DEBUG: Missing JIRA credentials - BASE_URL: {JIRA_BASE_URL}, TOKEN: {'***' if JIRA_BASIC_AUTH_TOKEN else None}")
        return None
    
    headers = {
        "authorization": f"Basic {JIRA_BASIC_AUTH_TOKEN}",
        "content-type": "application/json",
    }

    try:
        print(f"DEBUG: Making JIRA request to {url}")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            print(f"DEBUG: JIRA response status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"DEBUG: JIRA response items count: {len(result.get('issues', []))}")
                return result
            else:
                print(f"DEBUG: JIRA error response: {response.text}")
                return None
    except Exception as e:
        print(f"DEBUG: JIRA exception: {e}")
        return None


async def request_zephyr(url: str) -> Dict[str, Any] | None:
    """Make authenticated request to Zephyr API"""
    # Debug: Check if environment variables are loaded
    if not ZEPHYR_BASE_URL or not ZEPHYR_BEARER_TOKEN:
        print(f"DEBUG: Missing Zephyr credentials - BASE_URL: {ZEPHYR_BASE_URL}, TOKEN: {'***' if ZEPHYR_BEARER_TOKEN else None}")
        return None
    
    headers = {
        "authorization": f"Bearer {ZEPHYR_BEARER_TOKEN}",
        "content-type": "application/json",
    }

    try:
        print(f"DEBUG: Making Zephyr request to {url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            print(f"DEBUG: Zephyr response status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"DEBUG: Zephyr response items count: {len(result.get('values', []))}")
                return result
            else:
                print(f"DEBUG: Zephyr error response: {response.text}")
                return None
    except Exception as e:
        print(f"DEBUG: Zephyr exception: {e}")
        return None


def map_jira_priority_to_standard(jira_priority: str) -> str:
    """Map JIRA priority to standard priority"""
    mapping = {
        "Highest": "CRITICAL",
        "High": "HIGH",
        "Medium": "MEDIUM",
        "Low": "LOW",
        "Lowest": "LOW",
    }
    return mapping.get(jira_priority, "MEDIUM")


def map_jira_status_to_standard(jira_status: str) -> str:
    """Map JIRA status to standard status"""
    status_mapping = {
        "To Do": "TODO",
        "In Progress": "IN_PROGRESS",
        "Done": "DONE",
        "Closed": "CLOSED",
        "Open": "OPEN",
        "Resolved": "RESOLVED",
    }
    return status_mapping.get(jira_status, jira_status.upper().replace(" ", "_"))


def map_issue_type_to_requirement_type(issue_type: str) -> str:
    """Map JIRA issue type to requirement type"""
    mapping = {
        "Epic": "BUSINESS",
        "Story": "FUNCTIONAL",
        "Task": "FUNCTIONAL",
        "Requirement": "FUNCTIONAL",
    }
    return mapping.get(issue_type, "FUNCTIONAL")


def map_priority_to_risk_level(priority: str) -> str:
    """Map priority to risk level"""
    mapping = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}
    return mapping.get(priority, "MEDIUM")


def map_priority_to_severity(priority: str) -> str:
    """Map priority to bug severity"""
    mapping = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}
    return mapping.get(priority, "MEDIUM")


def extract_acceptance_criteria(description: str) -> List[str]:
    """Extract acceptance criteria from description"""
    if not description or not isinstance(description, str):
        return []

    criteria = []
    lines = description.split("\n")

    in_criteria_section = False
    for line in lines:
        line = line.strip()
        if any(
            keyword in line.lower()
            for keyword in ["acceptance criteria", "acceptance", "criteria"]
        ):
            in_criteria_section = True
            continue

        if in_criteria_section:
            if line.startswith("*") or line.startswith("-") or line.startswith("•"):
                criteria.append(line[1:].strip())
            elif line.startswith(("Given", "When", "Then", "And")):
                criteria.append(line)
            elif line == "" and criteria:
                break

    return criteria


def calculate_business_value(issue: Dict[str, Any]) -> int:
    """Calculate business value score"""
    priority_scores = {"CRITICAL": 100, "HIGH": 80, "MEDIUM": 60, "LOW": 40}
    type_scores = {"Epic": 20, "Story": 10, "Task": 5}

    fields = issue.get("fields", {})
    priority = fields.get("priority", {}).get("name", "MEDIUM")
    issue_type = fields.get("issuetype", {}).get("name", "Task")

    standard_priority = map_jira_priority_to_standard(priority)
    base_score = priority_scores.get(standard_priority, 60)
    type_bonus = type_scores.get(issue_type, 5)

    return min(base_score + type_bonus, 100)


def map_zephyr_execution_status(zephyr_status: str) -> str:
    """Map Zephyr execution status to standard"""
    mapping = {
        "PASS": "PASS",
        "FAIL": "FAIL",
        "WIP": "NOT_EXECUTED",
        "BLOCKED": "BLOCKED",
        "NOT_EXECUTED": "NOT_EXECUTED",
        "UNEXECUTED": "NOT_EXECUTED",
    }
    return mapping.get(zephyr_status.upper(), "NOT_EXECUTED")


async def fetch_requirements(project_id: str) -> Dict[str, Any]:
    """Fetch requirements from JIRA and transform to spec format"""
    url = f"{JIRA_BASE_URL}/search/jql"
    payload = {
        "expand": "",
        "fields": [
            "summary",
            "status",
            "priority",
            "issuetype",
            "parent",
            "description",
            "created",
            "updated",
            "labels",
            "customfield_10016",
        ],
        "fieldsByKeys": True,
        "jql": f"project = {project_id} AND issuetype IN (Epic, Story)",
        "maxResults": 100,
    }

    response = await request_jira(url, payload)
    if not response:
        return create_empty_response("requirements", project_id)

    items = []
    for issue in response.get("issues", []):
        fields = issue.get("fields", {})
        created_date = fields.get("created", datetime.now().isoformat() + "Z")
        updated_date = fields.get("updated", datetime.now().isoformat() + "Z")
        priority = fields.get("priority", {}).get("name", "MEDIUM")
        standard_priority = map_jira_priority_to_standard(priority)

        # Safely extract description
        description = fields.get("description") or ""
        if not isinstance(description, str):
            description = str(description) if description else ""
        
        item = {
            "id": issue.get("key", ""),
            "title": fields.get("summary", ""),
            "description": description,
            "status": map_jira_status_to_standard(
                fields.get("status", {}).get("name", "OPEN")
            ),
            "priority": standard_priority,
            "created_date": created_date,
            "updated_date": updated_date,
            "source_url": f"{JIRA_BASE_URL.replace('/rest/api/3', '')}/browse/{issue.get('key', '')}",
            "tags": fields.get("labels", []),
            "custom_fields": {},
            "requirement_type": map_issue_type_to_requirement_type(
                fields.get("issuetype", {}).get("name", "")
            ),
            "acceptance_criteria": extract_acceptance_criteria(description),
            "story_points": fields.get("customfield_10016"),
            "epic_id": fields.get("parent", {}).get("key")
            if fields.get("parent")
            else None,
            "linked_test_cases": [],
            "business_value": calculate_business_value(issue),
            "risk_level": map_priority_to_risk_level(standard_priority),
        }
        items.append(item)

    return create_response("requirements", project_id, items)


async def fetch_test_cases(project_id: str) -> Dict[str, Any]:
    """Fetch test cases from Zephyr and transform to spec format"""
    url = f"{ZEPHYR_BASE_URL}/testcases?projectKey={project_id}&maxResults=100"
    response = await request_zephyr(url)

    if not response:
        return create_empty_response("test_cases", project_id)

    items = []
    for test_case in response.get("values", []):
        created_date = test_case.get("createdOn", datetime.now().isoformat() + "Z")
        updated_date = test_case.get("modifiedOn", datetime.now().isoformat() + "Z")

        # Extract test steps and expected results
        test_steps = []
        expected_results = []
        if test_case.get("testScript", {}).get("steps"):
            for step in test_case["testScript"]["steps"]:
                test_steps.append(step.get("description", ""))
                expected_results.append(step.get("expectedResult", ""))

        item = {
            "id": test_case.get("key", ""),
            "title": test_case.get("name", ""),
            "description": test_case.get("objective", ""),
            "status": "ACTIVE" if test_case.get("status") == "Approved" else "DRAFT",
            "priority": test_case.get("priority", "MEDIUM"),
            "created_date": created_date,
            "updated_date": updated_date,
            "source_url": f"{ZEPHYR_BASE_URL.replace('/v2', '')}/testcase/{test_case.get('key', '')}",
            "tags": [],
            "custom_fields": {},
            "test_type": "AUTOMATED" if test_case.get("automated") else "MANUAL",
            "automation_status": "AUTOMATED"
            if test_case.get("automated")
            else "NOT_AUTOMATED",
            "requirement_id": None,  # Would need to extract from links
            "test_steps": test_steps,
            "expected_results": expected_results,
            "environment": "TESTING",
            "component": test_case.get("component", {}).get("name")
            if test_case.get("component")
            else None,
        }
        items.append(item)

    return create_response("test_cases", project_id, items)


async def fetch_test_executions(project_id: str) -> Dict[str, Any]:
    """Fetch test executions from Zephyr and transform to spec format"""
    url = f"{ZEPHYR_BASE_URL}/testexecutions?projectKey={project_id}&maxResults=100"
    response = await request_zephyr(url)

    if not response:
        return create_empty_response("test_executions", project_id)

    items = []
    for execution in response.get("values", []):
        executed_date = execution.get("executedOn", datetime.now().isoformat() + "Z")
        test_case = execution.get("testCase", {})
        execution_status = execution.get("executionStatus", {}).get(
            "name", "NOT_EXECUTED"
        )

        item = {
            "id": f"{test_case.get('key', '')}-{execution.get('id', '')}",
            "title": f"Execution of {test_case.get('name', '')}",
            "description": f"Test execution for {test_case.get('name', '')}",
            "status": "COMPLETED",
            "priority": "MEDIUM",
            "created_date": executed_date,
            "updated_date": executed_date,
            "source_url": f"{ZEPHYR_BASE_URL.replace('/v2', '')}/execution/{execution.get('id', '')}",
            "tags": [],
            "custom_fields": {},
            "test_case_id": test_case.get("key", ""),
            "execution_status": map_zephyr_execution_status(execution_status),
            "executed_by": execution.get("executedBy", {}).get("displayName", ""),
            "execution_time": executed_date,
            "duration_seconds": None,
            "environment": execution.get("environment", {}).get("name", "TESTING")
            if execution.get("environment")
            else "TESTING",
            "build_version": execution.get("testCycle", {}).get("build")
            if execution.get("testCycle")
            else None,
            "failure_reason": execution.get("comment")
            if execution_status == "FAIL"
            else None,
            "attachments": [],
        }
        items.append(item)

    return create_response("test_executions", project_id, items)


async def fetch_bugs(project_id: str) -> Dict[str, Any]:
    """Fetch bugs from JIRA and transform to spec format"""
    url = f"{JIRA_BASE_URL}/search/jql"
    payload = {
        "expand": "",
        "fields": [
            "summary",
            "status",
            "priority",
            "description",
            "parent",
            "created",
            "updated",
            "labels",
            "components",
            "environment",
            "resolution",
        ],
        "fieldsByKeys": True,
        "jql": f"project = {project_id} AND issuetype = Bug",
        "maxResults": 100,
    }

    response = await request_jira(url, payload)
    if not response:
        return create_empty_response("bugs", project_id)

    items = []
    for issue in response.get("issues", []):
        fields = issue.get("fields", {})
        created_date = fields.get("created", datetime.now().isoformat() + "Z")
        updated_date = fields.get("updated", datetime.now().isoformat() + "Z")
        priority = fields.get("priority", {}).get("name", "MEDIUM")
        standard_priority = map_jira_priority_to_standard(priority)

        # Safely extract description
        description = fields.get("description") or ""
        if not isinstance(description, str):
            description = str(description) if description else ""
        
        item = {
            "id": issue.get("key", ""),
            "title": fields.get("summary", ""),
            "description": description,
            "status": map_jira_status_to_standard(
                fields.get("status", {}).get("name", "OPEN")
            ),
            "priority": standard_priority,
            "created_date": created_date,
            "updated_date": updated_date,
            "source_url": f"{JIRA_BASE_URL.replace('/rest/api/3', '')}/browse/{issue.get('key', '')}",
            "tags": fields.get("labels", []),
            "custom_fields": {},
            "bug_type": "FUNCTIONAL",  # Default, could be enhanced based on labels/custom fields
            "severity": map_priority_to_severity(standard_priority),
            "environment": "PRODUCTION",  # Default, could be extracted from environment field
            "component": fields.get("components", [{}])[0].get("name")
            if fields.get("components")
            else None,
            "reproduction_steps": [],  # Could be extracted from description
            "expected_behavior": None,
            "actual_behavior": None,
            "resolution": fields.get("resolution", {}).get("name")
            if fields.get("resolution")
            else None,
            "found_in_version": None,
            "fixed_in_version": None,
        }
        items.append(item)

    return create_response("bugs", project_id, items)


def create_response(
    data_type: str, project_id: str, items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Create a properly formatted response according to MCP spec"""
    return {
        "uri": f"quality://{SERVER_NAME}/{data_type}/{project_id}",
        "name": f"{data_type.replace('_', ' ').title()} from {SERVER_NAME}",
        "description": f"{data_type.replace('_', ' ').title()} for project {project_id}",
        "mimeType": "application/json",
        "metadata": {
            "source_server": SERVER_NAME,
            "server_type": "jira"
            if data_type in ["requirements", "bugs"]
            else "zephyr",
            "project_id": project_id,
            "data_type": data_type,
            "sync_time": datetime.now().isoformat() + "Z",
            "total_count": len(items),
            "last_modified": max((item["updated_date"] for item in items), default=None)
            if items
            else None,
            "schema_version": "1.0",
            "additional_info": {},
        },
        "items": items,
    }


def create_empty_response(data_type: str, project_id: str) -> Dict[str, Any]:
    """Create an empty response when no data is available"""
    return create_response(data_type, project_id, [])


@mcp.tool()
async def get_requirements(project_id: str = PROJECT_ID) -> Dict[str, Any]:
    """
    Get requirements data for the specified project.

    Args:
        project_id (str): The project ID to fetch requirements for (default: SEM)

    Returns:
        Dict[str, Any]: Requirements data following MCP spec format
    """
    print(f"DEBUG: get_requirements called with project_id: {project_id}")
    try:
        result = await fetch_requirements(project_id)
        print(f"DEBUG: get_requirements returning {len(result.get('items', []))} items")
        return result
    except Exception as e:
        print(f"DEBUG: get_requirements exception: {e}")
        raise


@mcp.tool()
async def get_test_cases(project_id: str = PROJECT_ID) -> Dict[str, Any]:
    """
    Get test cases data for the specified project.

    Args:
        project_id (str): The project ID to fetch test cases for (default: SEM)

    Returns:
        Dict[str, Any]: Test cases data following MCP spec format
    """
    return await fetch_test_cases(project_id)


@mcp.tool()
async def get_bugs(project_id: str = PROJECT_ID) -> Dict[str, Any]:
    """
    Get bugs data for the specified project.

    Args:
        project_id (str): The project ID to fetch bugs for (default: SEM)

    Returns:
        Dict[str, Any]: Bugs data following MCP spec format
    """
    return await fetch_bugs(project_id)


@mcp.tool()
async def get_test_executions(project_id: str = PROJECT_ID) -> Dict[str, Any]:
    """
    Get test executions data for the specified project.

    Args:
        project_id (str): The project ID to fetch test executions for (default: SEM)

    Returns:
        Dict[str, Any]: Test executions data following MCP spec format
    """
    return await fetch_test_executions(project_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
