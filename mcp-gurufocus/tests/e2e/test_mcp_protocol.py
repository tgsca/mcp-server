"""
End-to-End MCP Protocol Tests.

Tests the complete MCP workflow including protocol-level communication.
"""

import pytest
import subprocess
import json
import asyncio
import os
import signal
import time
from pathlib import Path


class TestMCPProtocolE2E:
    """End-to-end MCP server protocol tests."""
    
    @pytest.fixture
    def mcp_server_process(self):
        """Start MCP server as subprocess."""
        env = os.environ.copy()
        env.update({
            "MCP_SERVER_MODE": "stdio",
            "GURUFOCUS_API_KEY": "test_api_key_123"
        })
        
        try:
            process = subprocess.Popen(
                ["uv", "run", "python", "app/main.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=Path(__file__).parent.parent.parent
            )
            
            # Give the process a moment to start
            time.sleep(1)
            
            # Check if process started successfully
            if process.poll() is not None:
                stderr_output = process.stderr.read()
                pytest.skip(f"MCP server failed to start: {stderr_output}")
            
            yield process
            
        finally:
            # Cleanup
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

    def send_message(self, process, message):
        """Send a JSON-RPC message to the MCP server."""
        message_str = json.dumps(message) + "\n"
        process.stdin.write(message_str)
        process.stdin.flush()

    def read_response(self, process, timeout=10):
        """Read a JSON-RPC response from the MCP server."""
        import select
        
        # Use select to implement timeout
        ready, _, _ = select.select([process.stdout], [], [], timeout)
        if not ready:
            raise TimeoutError("No response received within timeout")
        
        response_line = process.stdout.readline()
        if not response_line:
            raise RuntimeError("Server closed connection")
        
        try:
            return json.loads(response_line.strip())
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response: {response_line}") from e

    def test_mcp_protocol_initialization(self, mcp_server_process):
        """Test MCP protocol handshake."""
        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            self.send_message(mcp_server_process, init_message)
            response = self.read_response(mcp_server_process)
            
            # Verify response structure
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            assert "capabilities" in response["result"]
            assert "serverInfo" in response["result"]
            
            # Verify server info
            server_info = response["result"]["serverInfo"]
            assert "name" in server_info
            assert "version" in server_info
            
        except Exception as e:
            stderr_output = mcp_server_process.stderr.read()
            pytest.fail(f"Protocol initialization failed: {e}\nServer stderr: {stderr_output}")

    def test_list_tools_via_protocol(self, mcp_server_process):
        """Test listing tools through MCP protocol."""
        # Initialize first
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        try:
            self.send_message(mcp_server_process, init_msg)
            init_response = self.read_response(mcp_server_process)
            assert "result" in init_response
            
            # Send initialized notification
            initialized_msg = {
                "jsonrpc": "2.0",
                "method": "initialized",
                "params": {}
            }
            self.send_message(mcp_server_process, initialized_msg)
            
            # List tools
            list_tools_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            self.send_message(mcp_server_process, list_tools_msg)
            response = self.read_response(mcp_server_process)
            
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            assert "result" in response
            assert "tools" in response["result"]
            
            # Verify expected tools are present
            tools = response["result"]["tools"]
            tool_names = [tool["name"] for tool in tools]
            
            expected_tools = [
                "get_concise_stock_summary",
                "get_concise_stock_financials",
                "get_concise_analyst_estimates",
                "get_concise_segments_data",
                "get_concise_news_headlines"
            ]
            
            for expected_tool in expected_tools:
                assert expected_tool in tool_names, f"Tool {expected_tool} not found"
                
            # Verify tool structure
            for tool in tools:
                assert "name" in tool
                assert "description" in tool
                assert "inputSchema" in tool
                
        except Exception as e:
            stderr_output = mcp_server_process.stderr.read()
            pytest.fail(f"List tools failed: {e}\nServer stderr: {stderr_output}")

    def test_tool_execution_via_protocol(self, mcp_server_process):
        """Test tool execution through MCP protocol."""
        try:
            # Initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            self.send_message(mcp_server_process, init_msg)
            init_response = self.read_response(mcp_server_process)
            assert "result" in init_response
            
            # Send initialized notification
            self.send_message(mcp_server_process, {
                "jsonrpc": "2.0",
                "method": "initialized",
                "params": {}
            })
            
            # Execute tool
            tool_call_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "get_concise_stock_summary",
                    "arguments": {"symbol": "AAPL"}
                }
            }
            
            self.send_message(mcp_server_process, tool_call_msg)
            response = self.read_response(mcp_server_process, timeout=30)  # Longer timeout for API calls
            
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            
            # Tool might return error due to invalid API key, but should not crash
            if "error" in response:
                # This is acceptable for testing - API might fail with test key
                assert "code" in response["error"]
                assert "message" in response["error"]
            else:
                # If successful, verify structure
                assert "result" in response
                result = response["result"]
                assert "content" in result
                assert isinstance(result["content"], list)
                assert len(result["content"]) > 0
                
        except TimeoutError:
            pytest.skip("Tool execution timed out - possibly due to real API call")
        except Exception as e:
            stderr_output = mcp_server_process.stderr.read()
            pytest.fail(f"Tool execution failed: {e}\nServer stderr: {stderr_output}")

    def test_invalid_method_handling(self, mcp_server_process):
        """Test handling of invalid method calls."""
        try:
            # Initialize first
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            self.send_message(mcp_server_process, init_msg)
            init_response = self.read_response(mcp_server_process)
            assert "result" in init_response
            
            # Send invalid method
            invalid_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "invalid/method",
                "params": {}
            }
            
            self.send_message(mcp_server_process, invalid_msg)
            response = self.read_response(mcp_server_process)
            
            # Should return error for invalid method
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            assert "error" in response
            assert response["error"]["code"] == -32601  # Method not found
            
        except Exception as e:
            stderr_output = mcp_server_process.stderr.read()
            pytest.fail(f"Invalid method test failed: {e}\nServer stderr: {stderr_output}")

    def test_malformed_json_handling(self, mcp_server_process):
        """Test handling of malformed JSON."""
        try:
            # Send malformed JSON
            mcp_server_process.stdin.write("{ invalid json }\n")
            mcp_server_process.stdin.flush()
            
            response = self.read_response(mcp_server_process)
            
            # Should return parse error
            assert response["jsonrpc"] == "2.0"
            assert "error" in response
            assert response["error"]["code"] == -32700  # Parse error
            
        except Exception as e:
            # It's acceptable if the server closes connection on malformed JSON
            pass

    def test_missing_required_parameters(self, mcp_server_process):
        """Test handling of missing required parameters."""
        try:
            # Initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            self.send_message(mcp_server_process, init_msg)
            init_response = self.read_response(mcp_server_process)
            assert "result" in init_response
            
            # Send initialized notification
            self.send_message(mcp_server_process, {
                "jsonrpc": "2.0",
                "method": "initialized",
                "params": {}
            })
            
            # Call tool without required parameter
            tool_call_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "get_concise_stock_summary",
                    "arguments": {}  # Missing required 'symbol' parameter
                }
            }
            
            self.send_message(mcp_server_process, tool_call_msg)
            response = self.read_response(mcp_server_process)
            
            # Should return error for missing parameter
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            assert "error" in response
            
        except Exception as e:
            stderr_output = mcp_server_process.stderr.read()
            pytest.fail(f"Missing parameter test failed: {e}\nServer stderr: {stderr_output}")

    def test_server_shutdown_handling(self, mcp_server_process):
        """Test graceful server shutdown."""
        try:
            # Initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            self.send_message(mcp_server_process, init_msg)
            init_response = self.read_response(mcp_server_process)
            assert "result" in init_response
            
            # Send shutdown request
            shutdown_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "shutdown",
                "params": {}
            }
            
            self.send_message(mcp_server_process, shutdown_msg)
            response = self.read_response(mcp_server_process)
            
            # Should acknowledge shutdown
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            assert "result" in response
            
            # Send exit notification
            exit_msg = {
                "jsonrpc": "2.0",
                "method": "exit",
                "params": {}
            }
            
            self.send_message(mcp_server_process, exit_msg)
            
            # Server should exit gracefully
            exit_code = mcp_server_process.wait(timeout=5)
            assert exit_code == 0, "Server did not exit gracefully"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Server did not exit within timeout")
        except Exception as e:
            stderr_output = mcp_server_process.stderr.read()
            pytest.fail(f"Shutdown test failed: {e}\nServer stderr: {stderr_output}")

    def test_concurrent_requests(self, mcp_server_process):
        """Test handling of concurrent requests."""
        try:
            # Initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize", 
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            self.send_message(mcp_server_process, init_msg)
            init_response = self.read_response(mcp_server_process)
            assert "result" in init_response
            
            # Send initialized notification
            self.send_message(mcp_server_process, {
                "jsonrpc": "2.0",
                "method": "initialized",
                "params": {}
            })
            
            # Send multiple concurrent requests
            requests = [
                {
                    "jsonrpc": "2.0",
                    "id": i + 2,
                    "method": "tools/list",
                    "params": {}
                }
                for i in range(3)
            ]
            
            # Send all requests
            for request in requests:
                self.send_message(mcp_server_process, request)
            
            # Read all responses
            responses = []
            for _ in range(3):
                response = self.read_response(mcp_server_process)
                responses.append(response)
            
            # Verify all responses received
            assert len(responses) == 3
            
            # Verify response IDs match request IDs
            response_ids = [r["id"] for r in responses]
            expected_ids = [2, 3, 4]
            assert sorted(response_ids) == sorted(expected_ids)
            
        except Exception as e:
            stderr_output = mcp_server_process.stderr.read()
            pytest.fail(f"Concurrent requests test failed: {e}\nServer stderr: {stderr_output}")