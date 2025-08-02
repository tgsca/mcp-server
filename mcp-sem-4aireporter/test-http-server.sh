#!/bin/bash

# Test script for FastMCP HTTP server
echo "Testing FastMCP HTTP server on localhost:8000..."
echo "========================================"

# Test 1: List available tools
echo "1. Testing tools/list:"
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }' | python3 -m json.tool

echo -e "\n========================================"

# Test 2: Call a specific tool (get_requirements)
echo "2. Testing tools/call - get_requirements:"
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_requirements",
      "arguments": {
        "project_id": "SEM"
      }
    }
  }' | python3 -m json.tool

echo -e "\n========================================"

# Test 3: Invalid endpoint (should return 404)
echo "3. Testing invalid GET request (should fail with 404):"
curl -X GET http://localhost:8000/ -v

echo -e "\n========================================"
echo "Test complete!"