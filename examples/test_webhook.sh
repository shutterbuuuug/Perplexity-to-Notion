#!/bin/bash

# Webhook Test Script
# ===================
# Test your Perplexity to Notion webhook server
#
# Usage:
#   ./test_webhook.sh                           # Test localhost:8080
#   ./test_webhook.sh http://example.com:8080   # Test custom endpoint
#   ./test_webhook.sh https://api.example.com   # Test production

# Configuration
WEBHOOK_URL="${1:-http://localhost:8080}"
API_KEY="${WEBHOOK_API_KEY:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════╗"
echo "║        Perplexity to Notion Webhook Tester            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Testing endpoint: $WEBHOOK_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local endpoint="$1"
    local method="$2"
    local description="$3"
    local data="$4"

    echo -e "${BLUE}Testing:${NC} $method $endpoint - $description"

    # Build curl command
    local curl_cmd="curl -s -w '\n%{http_code}' -X $method"

    if [ -n "$API_KEY" ]; then
        curl_cmd="$curl_cmd -H 'Authorization: Bearer $API_KEY'"
    fi

    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -H 'Content-Type: application/json' -d '$data'"
    fi

    curl_cmd="$curl_cmd '$WEBHOOK_URL$endpoint'"

    # Execute request
    response=$(eval $curl_cmd)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    # Check result
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓${NC} Success (HTTP $http_code)"
        echo "   Response: $body"
    else
        echo -e "${RED}✗${NC} Failed (HTTP $http_code)"
        echo "   Response: $body"
    fi

    echo ""
}

# Test 1: Root endpoint
test_endpoint "/" "GET" "API information"

# Test 2: Health check
test_endpoint "/health" "GET" "Health check"

# Test 3: Export with manual content
test_data='{
  "content": {
    "title": "Test Export",
    "content": "This is a test export from the webhook tester script.",
    "sources": ["https://example.com"],
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  },
  "destination_id": "test-database-id"
}'

test_endpoint "/export" "POST" "Export test content" "$test_data"

echo "╔════════════════════════════════════════════════════════╗"
echo "║                    Test Complete                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Notes:"
echo "  • If tests fail, check that the webhook server is running"
echo "  • Ensure firewall allows connections to the port"
echo "  • For remote testing, replace localhost with server IP"
echo "  • Set WEBHOOK_API_KEY environment variable if auth is enabled"
echo ""
