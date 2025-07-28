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
    # Check if environment variables are loaded
    if not JIRA_BASE_URL or not JIRA_BASIC_AUTH_TOKEN:
        return None

    headers = {
        "authorization": f"Basic {JIRA_BASIC_AUTH_TOKEN}",
        "content-type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return None
    except Exception:
        return None


async def request_zephyr(url: str) -> Dict[str, Any] | None:
    """Make authenticated request to Zephyr API"""
    # Check if environment variables are loaded
    if not ZEPHYR_BASE_URL or not ZEPHYR_BEARER_TOKEN:
        return None

    headers = {
        "authorization": f"Bearer {ZEPHYR_BEARER_TOKEN}",
        "content-type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return None
    except Exception:
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
    if not zephyr_status or not isinstance(zephyr_status, str):
        return "NOT_EXECUTED"

    # Handle both direct values and nested objects
    status_str = str(zephyr_status).upper().strip()

    mapping = {
        "PASS": "PASS",
        "PASSED": "PASS",
        "FAIL": "FAIL",
        "FAILED": "FAIL",
        "WIP": "NOT_EXECUTED",
        "IN_PROGRESS": "NOT_EXECUTED",
        "BLOCKED": "BLOCKED",
        "NOT_EXECUTED": "NOT_EXECUTED",
        "UNEXECUTED": "NOT_EXECUTED",
        "NOT_RUN": "NOT_EXECUTED",
        "SKIP": "SKIP",
        "SKIPPED": "SKIP",
    }

    result = mapping.get(status_str, "NOT_EXECUTED")
    return result


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
        
        # Direct field mapping from JIRA API
        created_date = fields.get("created", datetime.now().isoformat() + "Z")
        updated_date = fields.get("updated", datetime.now().isoformat() + "Z")
        
        # Map actual JIRA priority names to standard format (same as bugs)
        priority_name = fields.get("priority", {}).get("name", "")
        priority_mapping = {
            "4-Sehr hoch": "CRITICAL",
            "3-Eher hoch": "HIGH", 
            "2-Mittel": "MEDIUM",
            "1-Niedrig": "LOW",
            "0-Sehr niedrig": "LOW"
        }
        standard_priority = priority_mapping.get(priority_name, "MEDIUM")

        # Extract description from complex JSON structure
        description_raw = fields.get("description")
        description = ""
        if description_raw and isinstance(description_raw, dict):
            # Extract text from Atlassian Document Format (ADF)
            def extract_text_from_adf(content):
                text_parts = []
                if isinstance(content, dict):
                    if content.get("type") == "text":
                        text_parts.append(content.get("text", ""))
                    elif "content" in content:
                        for item in content["content"]:
                            text_parts.extend(extract_text_from_adf(item))
                elif isinstance(content, list):
                    for item in content:
                        text_parts.extend(extract_text_from_adf(item))
                return text_parts
            
            text_parts = extract_text_from_adf(description_raw)
            description = " ".join(text_parts).strip()
        else:
            description = str(description_raw) if description_raw else ""

        # Direct field mapping
        status_name = fields.get("status", {}).get("name", "")
        issue_type_name = fields.get("issuetype", {}).get("name", "")
        parent_key = fields.get("parent", {}).get("key") if fields.get("parent") else None
        story_points = fields.get("customfield_10016")
        labels = fields.get("labels", [])
        
        # Map status names to standard format
        status_mapping = {
            "Backlog": "TODO",
            "Selected for Development": "TODO", 
            "In Arbeit": "IN_PROGRESS",
            "In Progress": "IN_PROGRESS",
            "Done": "DONE",
            "Closed": "CLOSED"
        }
        mapped_status = status_mapping.get(status_name, "OPEN")
        
        # Map issue type to requirement type
        requirement_type_mapping = {
            "Epic": "BUSINESS",
            "Story": "FUNCTIONAL"
        }
        requirement_type = requirement_type_mapping.get(issue_type_name, "FUNCTIONAL")
        
        item = {
            "id": issue.get("key", ""),
            "title": fields.get("summary", ""),
            "description": description,
            "status": mapped_status,
            "priority": standard_priority,
            "created_date": created_date,
            "updated_date": updated_date,
            "source_url": f"{JIRA_BASE_URL.replace('/rest/api/3', '')}/browse/{issue.get('key', '')}",
            "tags": labels,
            "custom_fields": {},
            "requirement_type": requirement_type,
            "acceptance_criteria": [],  # Could extract from description if needed
            "story_points": story_points,
            "epic_id": parent_key,
            "linked_test_cases": [],
            "business_value": 50,  # Default value, could calculate based on priority
            "risk_level": standard_priority,  # Same as priority for simplicity
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
        # Direct field mapping from Zephyr API
        created_date = test_case.get("createdOn", datetime.now().isoformat() + "Z")
        updated_date = created_date  # Zephyr doesn't seem to have modifiedOn in this response
        
        # Map status ID to status name (based on common Zephyr status IDs)
        status_id = test_case.get("status", {}).get("id")
        status_mapping = {
            9156759: "ACTIVE",  # Active/Approved status
            9156758: "DRAFT",   # Draft status
            9156757: "INACTIVE" # Deprecated status
        }
        mapped_status = status_mapping.get(status_id, "DRAFT")
        
        # Map priority ID to priority name (based on common Zephyr priority IDs)  
        priority_id = test_case.get("priority", {}).get("id")
        priority_mapping = {
            9156760: "MEDIUM",   # Medium priority
            9156761: "HIGH",     # High priority
            9156762: "CRITICAL", # Critical priority
            9156763: "LOW"       # Low priority
        }
        mapped_priority = priority_mapping.get(priority_id, "MEDIUM")
        
        # Extract component and owner
        component_name = test_case.get("component", {}).get("name") if test_case.get("component") else None
        owner_id = test_case.get("owner", {}).get("accountId") if test_case.get("owner") else None

        item = {
            "id": test_case.get("key", ""),
            "title": test_case.get("name", ""),
            "description": test_case.get("objective", ""),
            "status": mapped_status,
            "priority": mapped_priority,
            "created_date": created_date,
            "updated_date": updated_date,
            "source_url": f"{ZEPHYR_BASE_URL.replace('/v2', '')}/testcase/{test_case.get('key', '')}",
            "tags": test_case.get("labels", []),
            "custom_fields": test_case.get("customFields", {}),
            "test_type": "MANUAL",  # Default to manual, no automated field in API response
            "automation_status": "NOT_AUTOMATED",
            "requirement_id": None,  # Could extract from links.issues if needed
            "test_steps": [],  # Would need separate API call to testScript.self
            "expected_results": [],  # Would need separate API call
            "environment": "TESTING",
            "component": component_name,
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
        # Direct field mapping from Zephyr API
        executed_date = execution.get("actualEndDate") or datetime.now().isoformat() + "Z"
        
        # Extract test case key from self URL (e.g., "SEM-T1" from the URL)
        test_case_key = ""
        if execution.get("testCase", {}).get("self"):
            test_case_url = execution["testCase"]["self"]
            # Extract key like "SEM-T1" from URL
            if "/testcases/" in test_case_url:
                test_case_key = test_case_url.split("/testcases/")[1].split("/")[0]
        
        # Map status ID to status name (corrected for German Zephyr instance)
        status_id = execution.get("testExecutionStatus", {}).get("id")
        status_mapping = {
            9156746: "NOT_EXECUTED",  # 55 executions - "nicht ausgeführt"
            9156747: "IN_PROGRESS",   # 1 execution - "im Test"  
            9156748: "PASS",          # 8 executions - "Erfolgreich" ✅
            9156749: "FAIL",          # 3 executions - "Fehlgeschlagen"
            9156750: "BLOCKED",       # 5 executions - "Blockiert" ✅
        }
        execution_status = status_mapping.get(status_id, "NOT_EXECUTED")
        
        # Direct field mapping
        executed_by_id = execution.get("executedById") or ""
        environment = execution.get("environment") or "TESTING"
        comment = execution.get("comment")
        execution_time_seconds = execution.get("executionTime")
        test_cycle_id = execution.get("testCycle", {}).get("id")

        item = {
            "id": f"{test_case_key}-{execution.get('id', '')}",
            "title": f"Execution of {test_case_key}",
            "description": f"Test execution for {test_case_key}",
            "status": "COMPLETED",
            "priority": "MEDIUM",
            "created_date": executed_date,
            "updated_date": executed_date,
            "source_url": f"{ZEPHYR_BASE_URL.replace('/v2', '')}/testexecutions/{execution.get('id', '')}",
            "tags": [],
            "custom_fields": {},
            "test_case_id": test_case_key,
            "execution_status": execution_status,
            "executed_by": executed_by_id,
            "execution_time": executed_date,
            "duration_seconds": execution_time_seconds,
            "environment": environment,
            "build_version": str(test_cycle_id) if test_cycle_id else None,
            "failure_reason": comment,
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
        
        # Direct field mapping from JIRA API
        created_date = fields.get("created", datetime.now().isoformat() + "Z")
        updated_date = fields.get("updated", datetime.now().isoformat() + "Z")
        
        # Map actual JIRA priority names to standard format
        priority_name = fields.get("priority", {}).get("name", "")
        priority_mapping = {
            "4-Sehr hoch": "CRITICAL",
            "3-Eher hoch": "HIGH", 
            "2-Mittel": "MEDIUM",
            "1-Niedrig": "LOW",
            "0-Sehr niedrig": "LOW"
        }
        standard_priority = priority_mapping.get(priority_name, "MEDIUM")

        # Direct description mapping
        description = fields.get("description") or ""
        if not isinstance(description, str):
            description = str(description) if description else ""

        # Direct field mapping - simplified
        environment = fields.get("environment") or "PRODUCTION"
        labels = fields.get("labels", [])
        components = fields.get("components", [])
        resolution = fields.get("resolution", {}).get("name") if fields.get("resolution") else None
        status_name = fields.get("status", {}).get("name", "OPEN")
        parent_key = fields.get("parent", {}).get("key") if fields.get("parent") else None

        # Map status name to standard format
        status_mapping = {
            "Backlog": "TODO",
            "Selected for Development": "TODO", 
            "In Arbeit": "IN_PROGRESS",
            "In Progress": "IN_PROGRESS",
            "Done": "DONE",
            "Closed": "CLOSED",
            "Open": "OPEN"
        }
        mapped_status = status_mapping.get(status_name, "OPEN")
        
        # Extract component name
        component_name = None
        if components and len(components) > 0:
            component_name = components[0].get("name") if isinstance(components[0], dict) else None

        item = {
            "id": issue.get("key", ""),
            "title": fields.get("summary", ""),
            "description": description,
            "status": mapped_status,
            "priority": standard_priority,
            "created_date": created_date,
            "updated_date": updated_date,
            "source_url": f"{JIRA_BASE_URL.replace('/rest/api/3', '')}/browse/{issue.get('key', '')}",
            "tags": labels,
            "custom_fields": {},
            "bug_type": "FUNCTIONAL",  # Default type
            "severity": standard_priority,  # Same as priority for simplicity
            "environment": environment,
            "component": component_name,
            "reproduction_steps": [],  # Could extract from description if needed
            "expected_behavior": None,
            "actual_behavior": None,
            "resolution": resolution,
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
    try:
        result = await fetch_requirements(project_id)
        return result
    except Exception as e:
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
async def get_test_execution_stats(project_id: str = PROJECT_ID) -> Dict[str, Any]:
    """
    Get test execution status statistics to debug mapping.
    
    Args:
        project_id (str): The project ID to analyze
        
    Returns:
        Dict[str, Any]: Statistics about execution statuses
    """
    url = f"{ZEPHYR_BASE_URL}/testexecutions?projectKey={project_id}&maxResults=100"
    response = await request_zephyr(url)
    
    if not response:
        return {"error": "No response from Zephyr API"}
    
    stats = {
        "total_executions": len(response.get("values", [])),
        "status_id_counts": {},
        "mapped_status_counts": {},
        "raw_status_samples": []
    }
    
    # Status mapping (corrected for German Zephyr instance)
    status_mapping = {
        9156746: "NOT_EXECUTED",  # 55 executions - "nicht ausgeführt"
        9156747: "IN_PROGRESS",   # 1 execution - "im Test"  
        9156748: "PASS",          # 8 executions - "Erfolgreich"
        9156749: "FAIL",          # 3 executions - "Fehlgeschlagen"
        9156750: "BLOCKED",       # 5 executions - "Blockiert"
    }
    
    for execution in response.get("values", []):
        status_id = execution.get("testExecutionStatus", {}).get("id")
        mapped_status = status_mapping.get(status_id, "NOT_EXECUTED")
        
        # Count status IDs
        stats["status_id_counts"][str(status_id)] = stats["status_id_counts"].get(str(status_id), 0) + 1
        
        # Count mapped statuses
        stats["mapped_status_counts"][mapped_status] = stats["mapped_status_counts"].get(mapped_status, 0) + 1
        
        # Sample raw data (first 3)
        if len(stats["raw_status_samples"]) < 3:
            stats["raw_status_samples"].append({
                "test_case": execution.get("testCase", {}).get("self", "").split("/")[-2] if execution.get("testCase", {}).get("self") else "unknown",
                "status_id": status_id,
                "mapped_status": mapped_status,
                "executed_date": execution.get("actualEndDate"),
                "executed_by": execution.get("executedById")
            })
    
    return stats

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
