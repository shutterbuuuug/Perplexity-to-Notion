#!/data/data/com.termux/files/usr/bin/bash

# Termux Shortcut for Perplexity to Notion Export
# ===============================================
# Place this file in ~/.shortcuts/ for Termux:Widget integration
# Make executable: chmod +x ~/.shortcuts/termux_shortcut.sh

# Configuration
SCRIPT_DIR="$HOME/Perplexity-to-Notion"
DEFAULT_DB_ID="your-default-database-id-here"

# Check if script directory exists
if [ ! -d "$SCRIPT_DIR" ]; then
    echo "Error: Script directory not found at $SCRIPT_DIR"
    echo "Please clone the repository first"
    exit 1
fi

# Navigate to script directory
cd "$SCRIPT_DIR" || exit 1

# Get URL from clipboard if available
CLIPBOARD=$(termux-clipboard-get 2>/dev/null)

# Check if clipboard contains Perplexity URL
if [[ $CLIPBOARD == *"perplexity.ai"* ]]; then
    echo "Found Perplexity URL in clipboard"
    echo "Exporting: $CLIPBOARD"

    # Export with default database
    python perplexity_to_notion.py \
        --source "$CLIPBOARD" \
        --destination-id "$DEFAULT_DB_ID"

    # Show notification
    if [ $? -eq 0 ]; then
        termux-notification --title "Export Success" --content "Saved to Notion"
        termux-vibrate -d 200
    else
        termux-notification --title "Export Failed" --content "Check logs for details"
        termux-vibrate -d 500
    fi
else
    # Interactive mode if no URL in clipboard
    echo "No Perplexity URL in clipboard"
    echo "Launching interactive mode..."
    python perplexity_to_notion.py
fi
