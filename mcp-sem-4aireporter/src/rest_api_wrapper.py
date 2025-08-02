#!/usr/bin/env python3
"""
FastAPI REST wrapper for MCP server
Provides simple REST API access to MCP tools via stdio communication
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# FastAPI app setup
app = FastAPI(
    title="MCP SEM-4AI Reporter REST API",
    description="REST API wrapper for MCP Test Management Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ToolRequest(BaseModel):
    project_id: Optional[str] = "SEM"
    parameters: Optional[Dict[str, Any]] = {}

class TestCaseRequest(BaseModel):
    project_id: str = "SEM"
    name: str
    objective: str
    precondition: Optional[str] = None
    priority: Optional[str] = "Medium"
    status: Optional[str] = "Draft"
    test_steps: Optional[list] = []
    labels: Optional[list] = []

class LinkRequest(BaseModel):
    test_case_key: str
    jira_issue_id: str
    project_id: str = "SEM"

# MCP Client for stdio communication
class MCPClient:
    """Async MCP client using stdio communication"""
    
    def __init__(self):
        self.process = None
        self.initialized = False
        
    async def start(self):
        """Start MCP server process"""
        if self.process is None:
            # Determine working directory (Docker vs local)
            import os
            if os.path.exists("/app/src/main.py"):
                cwd = "/app"
                python_cmd = ["uv", "run", "python", "src/main.py"]
            else:
                cwd = os.path.dirname(os.path.dirname(__file__))  # Go up from src/ to project root
                python_cmd = ["uv", "run", "python", "src/main.py"]
            
            # Set environment to use stdio mode for the wrapped MCP server
            env = os.environ.copy()
            env["MCP_TRANSPORT"] = "stdio"
            
            self.process = await asyncio.create_subprocess_exec(
                *python_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=env
            )
            await self._initialize_session()
            
    async def _initialize_session(self):
        """Initialize MCP session"""
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "rest-api-wrapper", "version": "1.0.0"}
            }
        }
        response = await self._send_request(init_request)
        self.initialized = True
        return response
        
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON-RPC request to MCP server"""
        if not self.process:
            await self.start()
            
        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        if response_line:
            return json.loads(response_line.decode().strip())
        else:
            raise HTTPException(status_code=500, detail="No response from MCP server")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool with arguments"""
        if not self.initialized:
            await self.start()
            
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            raise HTTPException(
                status_code=400, 
                detail=f"MCP tool error: {response['error']}"
            )
            
        return response.get("result", {})
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available MCP tools"""
        if not self.initialized:
            await self.start()
            
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list",
            "params": {}
        }
        
        response = await self._send_request(request)
        return response.get("result", {})
    
    async def stop(self):
        """Stop MCP server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
            self.initialized = False

# Global MCP client instance
mcp_client = MCPClient()

@app.on_event("startup")
async def startup_event():
    """Initialize MCP client on startup"""
    await mcp_client.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup MCP client on shutdown"""
    await mcp_client.stop()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mcp-sem-4aireporter-rest-api",
        "version": "1.0.0",
        "mcp_initialized": mcp_client.initialized
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MCP SEM-4AI Reporter REST API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "tools": "/api/tools"
    }

# List all available tools
@app.get("/api/tools")
async def list_tools():
    """List all available MCP tools"""
    try:
        result = await mcp_client.list_tools()
        return {
            "success": True,
            "tools": result.get("tools", []),
            "count": len(result.get("tools", []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get requirements
@app.get("/api/requirements/{project_id}")
async def get_requirements(project_id: str):
    """Get JIRA requirements/epics for project"""
    try:
        result = await mcp_client.call_tool("get_requirements", {"project_id": project_id})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get test cases
@app.get("/api/test-cases/{project_id}")
async def get_test_cases(project_id: str):
    """Get Zephyr test cases for project"""
    try:
        result = await mcp_client.call_tool("get_test_cases", {"project_id": project_id})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get bugs
@app.get("/api/bugs/{project_id}")
async def get_bugs(project_id: str):
    """Get JIRA bugs for project"""
    try:
        result = await mcp_client.call_tool("get_bugs", {"project_id": project_id})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get test executions
@app.get("/api/test-executions/{project_id}")
async def get_test_executions(project_id: str):
    """Get Zephyr test executions for project"""
    try:
        result = await mcp_client.call_tool("get_test_executions", {"project_id": project_id})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create test case
@app.post("/api/test-cases")
async def create_test_case(request: TestCaseRequest):
    """Create new test case in Zephyr Scale"""
    try:
        arguments = {
            "project_id": request.project_id,
            "name": request.name,
            "objective": request.objective,
            "precondition": request.precondition,
            "priority": request.priority,
            "status": request.status,
            "test_steps": request.test_steps,
            "labels": request.labels
        }
        
        result = await mcp_client.call_tool("create_test_case", arguments)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Link test case to requirement
@app.post("/api/test-cases/link")
async def link_test_case(request: LinkRequest):
    """Link test case to JIRA requirement"""
    try:
        arguments = {
            "test_case_key": request.test_case_key,
            "jira_issue_id": request.jira_issue_id,
            "project_id": request.project_id
        }
        
        result = await mcp_client.call_tool("link_test_case_to_requirement", arguments)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get analytics and insights
@app.get("/api/analytics/insights/{project_id}")
async def get_insights(project_id: str):
    """Get AI-powered insights for project"""
    try:
        result = await mcp_client.call_tool("get_intelligent_insights", {"project_id": project_id})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/visual/{project_id}")
async def get_visual_analytics(project_id: str):
    """Get visual analytics data for charts"""
    try:
        result = await mcp_client.call_tool("get_visual_analytics_data", {"project_id": project_id})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/outlook/{project_id}")
async def get_future_outlook(project_id: str):
    """Get AI-generated future outlook predictions"""
    try:
        result = await mcp_client.call_tool("get_dynamic_future_outlook", {"project_id": project_id})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/completeness/{project_id}")
async def get_data_completeness(project_id: str):
    """Get data completeness statistics"""
    try:
        result = await mcp_client.call_tool("get_data_completeness_stats", {"project_id": project_id})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Generic tool caller
@app.post("/api/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolRequest):
    """Generic endpoint to call any MCP tool"""
    try:
        arguments = {"project_id": request.project_id}
        arguments.update(request.parameters)
        
        result = await mcp_client.call_tool(tool_name, arguments)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "rest_api_wrapper:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )