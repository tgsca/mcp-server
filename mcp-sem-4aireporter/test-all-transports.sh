#!/bin/bash

# Comprehensive test script for all MCP transport modes
# Tests stdio, http, sse, and rest transport modes

echo "🧪 Testing All MCP Transport Modes..."

# Configuration
SERVER_URL_HTTP="http://localhost:8000"
SERVER_URL_REST="http://localhost:8080"
MCP_ENDPOINT_HTTP="${SERVER_URL_HTTP}/mcp"
MCP_ENDPOINT_SSE_STREAM="${SERVER_URL_HTTP}/sse"
MCP_ENDPOINT_SSE_MSG="${SERVER_URL_HTTP}/messages"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to test endpoint
test_endpoint() {
    local test_name="$1"
    local url="$2"
    local method="$3"
    local data="$4"
    local expected_pattern="$5"
    local headers="$6"
    
    echo -e "${YELLOW}Testing: ${test_name}${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s "$url" $headers)
    else
        response=$(curl -s -X "$method" "$url" $headers -d "$data")
    fi
    
    if echo "$response" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASS: ${test_name}${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL: ${test_name}${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Function to start server and wait
start_server() {
    local transport="$1"
    local port="$2"
    local wait_time="${3:-5}"
    
    echo -e "${BLUE}Starting server in $transport mode...${NC}"
    MCP_TRANSPORT="$transport" uv run python src/main.py &
    SERVER_PID=$!
    sleep $wait_time
    
    # Check if server is responding
    if curl -s "http://localhost:$port" > /dev/null 2>&1; then
        echo -e "${GREEN}Server started successfully on port $port${NC}"
        return 0
    else
        echo -e "${RED}Server failed to start on port $port${NC}"
        return 1
    fi
}

# Function to stop server
stop_server() {
    if [ ! -z "$SERVER_PID" ]; then
        echo "Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
        sleep 2
    fi
    # Kill any remaining processes
    pkill -f "python src/main.py" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
}

# Cleanup function
cleanup() {
    echo -e "${BLUE}Cleaning up...${NC}"
    stop_server
}

# Set trap for cleanup on exit
trap cleanup EXIT

echo "=========================================="
echo "🚀 TEST 1: HTTP Transport Mode (port 8000)"
echo "=========================================="

if start_server "http" "8000"; then
    # Test HTTP JSON-RPC endpoints
    test_endpoint "HTTP Tools List" \
        "$MCP_ENDPOINT_HTTP" \
        "POST" \
        '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' \
        "jsonrpc" \
        '-H "Content-Type: application/json"'
    
    test_endpoint "HTTP Initialize Session" \
        "$MCP_ENDPOINT_HTTP" \
        "POST" \
        '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' \
        "mcp-sem-4aireporter" \
        '-H "Content-Type: application/json"'
    
    test_endpoint "HTTP Call get_requirements" \
        "$MCP_ENDPOINT_HTTP" \
        "POST" \
        '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_requirements", "arguments": {"project_id": "SEM"}}}' \
        "jsonrpc" \
        '-H "Content-Type: application/json"'
fi

stop_server
sleep 3

echo ""
echo "=========================================="
echo "📡 TEST 2: SSE Transport Mode (port 8000)"
echo "=========================================="

if start_server "sse" "8000"; then
    # Test SSE endpoints
    test_endpoint "SSE Stream Endpoint" \
        "$MCP_ENDPOINT_SSE_STREAM" \
        "GET" \
        "" \
        "text/event-stream" \
        '-H "Accept: text/event-stream"'
    
    test_endpoint "SSE Messages Endpoint" \
        "$MCP_ENDPOINT_SSE_MSG" \
        "POST" \
        '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' \
        "jsonrpc" \
        '-H "Content-Type: application/json"'
fi

stop_server
sleep 3

echo ""
echo "=========================================="
echo "🌐 TEST 3: REST API Mode (port 8080)"
echo "=========================================="

if start_server "rest" "8080" "10"; then
    # Test REST API endpoints
    test_endpoint "REST Health Check" \
        "${SERVER_URL_REST}/health" \
        "GET" \
        "" \
        "healthy" \
        ""
    
    test_endpoint "REST API Root" \
        "${SERVER_URL_REST}/" \
        "GET" \
        "" \
        "MCP SEM-4AI Reporter REST API" \
        ""
    
    test_endpoint "REST List Tools" \
        "${SERVER_URL_REST}/api/tools" \
        "GET" \
        "" \
        "success" \
        ""
    
    test_endpoint "REST Get Requirements" \
        "${SERVER_URL_REST}/api/requirements/SEM" \
        "GET" \
        "" \
        "success" \
        ""
    
    test_endpoint "REST Create Test Case" \
        "${SERVER_URL_REST}/api/test-cases" \
        "POST" \
        '{"name": "Test API Test Case", "objective": "Test REST API functionality", "project_id": "SEM"}' \
        "success" \
        '-H "Content-Type: application/json"'
    
    test_endpoint "REST Analytics Insights" \
        "${SERVER_URL_REST}/api/analytics/insights/SEM" \
        "GET" \
        "" \
        "success" \
        ""
fi

stop_server

echo ""
echo "=========================================="
echo "💻 TEST 4: Stdio Mode (Default)"
echo "=========================================="

# Test stdio mode with a simple echo test
echo -e "${YELLOW}Testing: Stdio Mode Initialization${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Create test JSON-RPC request
stdio_test='{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}'

# Test stdio mode with timeout
if timeout 10s bash -c "echo '$stdio_test' | MCP_TRANSPORT=stdio uv run python src/main.py | grep -q 'mcp-sem-4aireporter'"; then
    echo -e "${GREEN}✅ PASS: Stdio Mode Initialization${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAIL: Stdio Mode Initialization${NC}"
fi

# Final results
echo ""
echo "=========================================="
echo "📊 FINAL TEST RESULTS"
echo "=========================================="
echo -e "Total tests run: ${BLUE}${TOTAL_TESTS}${NC}"
echo -e "Tests passed: ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Tests failed: ${RED}$((TOTAL_TESTS - PASSED_TESTS))${NC}"
echo -e "Success rate: ${BLUE}$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%${NC}"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All tests passed! All transport modes are working correctly.${NC}"
    exit 0
elif [ $PASSED_TESTS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Some tests passed. Check individual transport modes for issues.${NC}"
    exit 1
else
    echo -e "${RED}💥 All tests failed. Check server configuration and dependencies.${NC}"
    exit 2
fi