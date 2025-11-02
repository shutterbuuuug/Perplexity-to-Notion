#!/bin/bash

# Perplexity to Notion - macOS Quick Installer
# =============================================
#
# Quick one-command installation for macOS (both Intel and Apple Silicon)
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/yourusername/Perplexity-to-Notion/main/install_macos.sh | bash
#
# Or download and run:
#   bash install_macos.sh
#
# Author: Claude Code
# License: MIT

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    IS_M1=true
    ARCH_NAME="Apple Silicon (M1/M2/M3)"
else
    IS_M1=false
    ARCH_NAME="Intel"
fi

echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BOLD}Perplexity to Notion - macOS Installer${NC}       ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${ARCH_NAME}                                ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}❌ This installer is for macOS only${NC}"
    exit 1
fi

# Check if Python 3.8+ is installed
echo -e "${BLUE}🔍 Checking Python installation...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  • Download from: https://www.python.org/downloads/"
    echo "  • Or use Homebrew: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Found Python $PYTHON_VERSION${NC}"

# Check Python version is 3.8+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ Python 3.8 or higher is required${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Ask for installation directory
echo ""
echo -e "${CYAN}📁 Where would you like to install?${NC}"
echo "   Default: $HOME/Perplexity-to-Notion"
read -p "   Location (press Enter for default): " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-"$HOME/Perplexity-to-Notion"}

# Create directory if it doesn't exist
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo ""
echo -e "${BLUE}📦 Installation directory: ${INSTALL_DIR}${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo ""
    echo -e "${YELLOW}⚠️  Git not found. Downloading archive instead...${NC}"

    # Download as archive
    curl -L "https://github.com/shutterbuuuug/Perplexity-to-Notion/archive/refs/heads/main.zip" -o temp.zip
    unzip -q temp.zip
    mv Perplexity-to-Notion-main/* .
    rm -rf Perplexity-to-Notion-main temp.zip
else
    echo ""
    echo -e "${BLUE}📥 Cloning repository...${NC}"

    if [ -d ".git" ]; then
        git pull
    else
        git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git .
    fi
fi

echo -e "${GREEN}✅ Repository downloaded${NC}"

# Check if setup wizard already exists
if [ -f "setup_wizard.py" ]; then
    echo ""
    echo -e "${CYAN}🚀 Launching setup wizard...${NC}"
    echo ""
    sleep 1

    python3 setup_wizard.py
else
    echo -e "${RED}❌ Setup wizard not found${NC}"
    echo "Please run manually: cd $INSTALL_DIR && python3 setup_wizard.py"
    exit 1
fi

echo ""
echo -e "${GREEN}${BOLD}✨ Installation complete! ✨${NC}"
echo ""
