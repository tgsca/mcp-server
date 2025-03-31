import os
from typing import Dict, Any
from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP

load_dotenv()

# JIRA
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
# JIRA_API_USER = os.getenv("JIRA_API_USER")
# JIRA_API_KEY = os.getenv("JIRA_API_KEY")
JIRA_BASIC_AUTH_TOKEN = os.getenv("JIRA_BASIC_AUTH_TOKEN")
ZEPHYR_BASE_URL = os.getenv("ZEPHYR_BASE_URL")
ZEPHYR_BEARER_TOKEN = os.getenv("ZEPHYR_BEARER_TOKEN")
mcp = FastMCP("tg-jira-seminarapp")

# JIRA
# auth = httpx.BasicAuth(JIRA_API_USER, JIRA_API_KEY)

""" Helper Functions """
async def request_projects() -> Dict[str, Any] | None:
    url = f"{JIRA_BASE_URL}/project/search"
    headers = {
        'authorization': f"Basic {JIRA_BASIC_AUTH_TOKEN}",
        'content-type': "application/json"
    }
    response = httpx.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

async def request_requirements(project_key: str) -> Dict[str, Any] | None:

    if not project_key:
        return None

    url = f"{JIRA_BASE_URL}/search/jql"
    headers = {
        'authorization': f"Basic {JIRA_BASIC_AUTH_TOKEN}",
        'content-type': "application/json"
    }
    payload = {
        "expand": "",
        "fields": [
            "summary",
            "status",
            "priority"
        ],
        "fieldsByKeys": True,
        "jql": f"project = {project_key} AND issuetype IN (Epic, Story)"
    }

    response = httpx.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

async def request_zephyr(url: str) -> Dict[str, Any] | None:
    if not url:
        return None

    headers = {
        'authorization': f"Bearer {ZEPHYR_BEARER_TOKEN}",
        'content-type': "application/json"
    }

    response = httpx.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

""" Tools """
@mcp.tool()
async def get_projects() -> Dict[str, Any] | None:
    """
    Get all projects from JIRA.
    This is a helper tool to get the project key for the other tools.
    """
    return await request_projects()

@mcp.tool()
async def get_requirements(project_key: str) -> Dict[str, Any] | None:
    """
    Get all requirements from JIRA.

    Args:
        project_key (str): The key of the project to get requirements from.

    Returns:
        Dict[str, Any] | None: A dictionary containing requirements or None if the request fails.
    """
    return await request_requirements(project_key)

@mcp.tool()
async def get_testcases(project_key: str) -> Dict[str, Any] | None:
    """
    Get all testcases from Zephyr.

    Args:
        project_key (str): The key of the project to get testcases from.

    Returns:
        Dict[str, Any] | None: A dictionary containing testcases or None if the request fails.
    """
    if not project_key:
        return None

    url = f"{ZEPHYR_BASE_URL}/testcases?projectKey={project_key}&maxResults=100"
    return await request_zephyr(url)

@mcp.tool()
async def get_testexecutions(project_key: str) -> Dict[str, Any] | None:
    """
    Get all testexecutions from Zephyr.

    Args:
        project_key (str): The key of the project to get testexecutions from.

    Returns:
        Dict[str, Any] | None: A dictionary containing testexecutions or None if the request fails.
    """
    if not project_key:
        return None

    url = f"{ZEPHYR_BASE_URL}/testexecutions?projectKey={project_key}&maxResults=100"
    return await request_zephyr(url)

""" Main """
if __name__ == "__main__":
    mcp.run(transport='stdio')
