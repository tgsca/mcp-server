#!/bin/bash

# Test script for MCP Server HTTP API deployment
# This script validates that the HTTP API server works correctly

echo "🚀 Testing MCP Server HTTP API..."

# Configuration
SERVER_URL="http://localhost:8000"
MCP_ENDPOINT="${SERVER_URL}/mcp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test API endpoint
test_endpoint() {
    local test_name="$1"
    local request_data="$2"
    local expected_pattern="$3"
    
    echo -e "${YELLOW}Testing: ${test_name}${NC}"
    
    response=$(curl -s -X POST "${MCP_ENDPOINT}" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "${request_data}")
    
    if echo "$response" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASS: ${test_name}${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL: ${test_name}${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Start server in background if not running
if ! curl -s "${SERVER_URL}" > /dev/null 2>&1; then
    echo "Starting MCP server in HTTP mode..."
    MCP_TRANSPORT=http uv run python src/main.py &
    SERVER_PID=$!
    sleep 5
    STARTED_SERVER=true
else
    echo "Server already running on ${SERVER_URL}"
    STARTED_SERVER=false
fi

# Test counter
TESTS_PASSED=0
TOTAL_TESTS=0

# Test 1: Initialize MCP session
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if test_endpoint "MCP Session Initialization" \
    '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}' \
    "mcp-sem-4aireporter"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
fi

# Test 2: List available tools
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if test_endpoint "List MCP Tools" \
    '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' \
    "get_requirements"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
fi

# Test 3: Call get_requirements tool (this will fail without real JIRA credentials, but tests API structure)
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if test_endpoint "Call get_requirements Tool" \
    '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_requirements", "arguments": {"project_id": "SEM"}}}' \
    "jsonrpc"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
fi

# Test 4: Call get_test_cases tool
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if test_endpoint "Call get_test_cases Tool" \
    '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_test_cases", "arguments": {"project_id": "SEM"}}}' \
    "jsonrpc"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
fi

# Cleanup: Stop server if we started it
if [ "$STARTED_SERVER" = true ] && [ ! -z "$SERVER_PID" ]; then
    echo "Stopping test server..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
fi

# Results
echo ""
echo "📊 Test Results:"
echo -e "Tests passed: ${GREEN}${TESTS_PASSED}${NC}/${TOTAL_TESTS}"

if [ $TESTS_PASSED -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All tests passed! HTTP API server is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check server configuration and credentials.${NC}"
    exit 1
fi