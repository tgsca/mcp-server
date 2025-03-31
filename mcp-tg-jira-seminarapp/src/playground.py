import os
from dotenv import load_dotenv
import httpx
from rich import print

load_dotenv()

# JIRA
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
# JIRA_API_USER = os.getenv("JIRA_API_USER")
# JIRA_API_KEY = os.getenv("JIRA_API_KEY")
JIRA_BASIC_AUTH_TOKEN = os.getenv("JIRA_BASIC_AUTH_TOKEN")

# JIRA
# auth = httpx.BasicAuth(JIRA_API_USER, JIRA_API_KEY)

def main():
    url = f"{JIRA_BASE_URL}/search/jql"

    # FIXME: This is a hack to get the JIRA API to work, but it should use the auth object
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
        "jql": "project = SEM AND issuetype IN (Epic, Story)"
    }

    response = httpx.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        # Show the whole request object
        print(f"Request: {response.request.content}")
        print(f"Response: {response.content}")
        return response.content

if __name__ == "__main__":
    print(main())
