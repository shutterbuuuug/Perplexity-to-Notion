#!/bin/bash

# Batch Export Script for Perplexity to Notion
# ============================================
# Export multiple Perplexity URLs to Notion in one go
#
# Usage:
#   ./batch_export.sh urls.txt
#   ./batch_export.sh                  (reads from stdin)

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_DB_ID="${NOTION_DATABASE_ID:-your-database-id-here}"
DELAY_SECONDS=2  # Delay between exports to avoid rate limiting

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
SUCCESS_COUNT=0
FAIL_COUNT=0

echo "╔════════════════════════════════════════════════════════╗"
echo "║     Perplexity to Notion - Batch Export Tool          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Function to export single URL
export_url() {
    local url="$1"
    local index="$2"
    local total="$3"

    echo -e "${YELLOW}[$index/$total]${NC} Exporting: $url"

    if python "$SCRIPT_DIR/perplexity_to_notion.py" \
        --source "$url" \
        --destination-id "$DEFAULT_DB_ID" \
        2>&1 | grep -q "success"; then
        echo -e "${GREEN}✓${NC} Success"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}✗${NC} Failed"
        ((FAIL_COUNT++))
    fi

    # Delay to avoid rate limiting
    if [ $index -lt $total ]; then
        sleep $DELAY_SECONDS
    fi
    echo ""
}

# Read URLs from file or stdin
if [ -n "$1" ]; then
    # Read from file
    if [ ! -f "$1" ]; then
        echo -e "${RED}Error: File '$1' not found${NC}"
        exit 1
    fi

    mapfile -t urls < "$1"
else
    # Read from stdin
    echo "Enter URLs (one per line, press Ctrl+D when done):"
    mapfile -t urls
fi

# Validate URLs
total=${#urls[@]}
if [ $total -eq 0 ]; then
    echo -e "${RED}No URLs provided${NC}"
    exit 1
fi

echo "Found $total URL(s) to export"
echo ""

# Process each URL
index=1
for url in "${urls[@]}"; do
    # Skip empty lines
    if [ -z "$url" ]; then
        continue
    fi

    # Skip comments
    if [[ $url == \#* ]]; then
        continue
    fi

    export_url "$url" $index $total
    ((index++))
done

# Summary
echo "╔════════════════════════════════════════════════════════╗"
echo "║                    Export Summary                      ║"
echo "╠════════════════════════════════════════════════════════╣"
echo -e "║  ${GREEN}Success:${NC} $SUCCESS_COUNT                                        ║"
echo -e "║  ${RED}Failed:${NC}  $FAIL_COUNT                                        ║"
echo "╚════════════════════════════════════════════════════════╝"

# Exit with error if any failed
[ $FAIL_COUNT -eq 0 ] && exit 0 || exit 1
