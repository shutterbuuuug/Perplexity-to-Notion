#!/data/data/com.termux/files/usr/bin/bash

# Perplexity to Notion - Android/Termux Installation Wizard
# ===========================================================
#
# A guided, step-by-step installer for Android devices using Termux.
# Handles everything from package installation to secure credential storage.
#
# Usage:
#   bash android_installer.sh
#
# Or if you're already in Termux:
#   curl -sSL https://raw.githubusercontent.com/yourusername/Perplexity-to-Notion/main/android_installer.sh | bash
#
# Author: Claude Code
# License: MIT

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Progress tracking
CURRENT_STEP=0
TOTAL_STEPS=10

# Installation directory
INSTALL_DIR="$HOME/Perplexity-to-Notion"

# Function to print colored output
print_color() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Function to print headers
print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to show progress
show_progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local percentage=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    local filled=$((CURRENT_STEP * 30 / TOTAL_STEPS))
    local empty=$((30 - filled))

    echo ""
    printf "${CYAN}Step %d/%d [%3d%%] " "$CURRENT_STEP" "$TOTAL_STEPS" "$percentage"
    printf "${GREEN}█%.0s" $(seq 1 $filled)
    printf "${NC}░%.0s" $(seq 1 $empty)
    echo -e "${NC}"
    echo ""
}

# Function to ask yes/no questions
ask_yes_no() {
    local prompt="$1"
    local default="${2:-y}"

    while true; do
        if [ "$default" = "y" ]; then
            read -p "$(echo -e ${CYAN}$prompt [Y/n]: ${NC})" response
            response=${response:-y}
        else
            read -p "$(echo -e ${CYAN}$prompt [y/N]: ${NC})" response
            response=${response:-n}
        fi

        case "$response" in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# Function to ask for input
ask_input() {
    local prompt="$1"
    local default="$2"
    local secret="${3:-false}"

    if [ "$secret" = "true" ]; then
        read -s -p "$(echo -e ${CYAN}$prompt: ${NC})" value
        echo ""  # New line after secret input
    else
        if [ -n "$default" ]; then
            read -p "$(echo -e ${CYAN}$prompt [$default]: ${NC})" value
            value=${value:-$default}
        else
            read -p "$(echo -e ${CYAN}$prompt: ${NC})" value
        fi
    fi

    echo "$value"
}

# Welcome screen
show_welcome() {
    clear
    print_header "🎉 Perplexity to Notion - Android Installer"

    cat << 'EOF'
    ╔════════════════════════════════════════════╗
    ║  Welcome to the Android Setup Wizard!     ║
    ║                                            ║
    ║  This wizard will guide you through:      ║
    ║                                            ║
    ║  ✓ Installing Termux packages             ║
    ║  ✓ Setting up Python environment          ║
    ║  ✓ Cloning the repository                 ║
    ║  ✓ Configuring API credentials            ║
    ║  ✓ Setting up secure storage              ║
    ║  ✓ Creating home screen shortcuts         ║
    ║  ✓ Testing the installation                ║
    ║                                            ║
    ║  Estimated time: 10-15 minutes            ║
    ╚════════════════════════════════════════════╝

EOF

    print_color $YELLOW "Requirements:"
    echo "  • Termux app (from F-Droid, NOT Google Play)"
    echo "  • ~200MB free storage"
    echo "  • Internet connection"
    echo ""

    read -p "$(echo -e ${CYAN}Press Enter to begin the installation...${NC})"
}

# Step 1: System check
step_system_check() {
    show_progress
    print_header "Step 1: System Requirements Check"

    print_color $BLUE "Checking your Android environment..."
    echo ""

    # Check if running in Termux
    if [ -z "$TERMUX_VERSION" ]; then
        print_color $RED "❌ Not running in Termux!"
        echo "Please install Termux from F-Droid and run this script inside it."
        exit 1
    else
        print_color $GREEN "✅ Termux version: $TERMUX_VERSION"
    fi

    # Check Android version
    if command -v getprop &> /dev/null; then
        ANDROID_VERSION=$(getprop ro.build.version.release)
        print_color $GREEN "✅ Android version: $ANDROID_VERSION"
    fi

    # Check storage space
    AVAILABLE_SPACE=$(df -h $HOME | tail -1 | awk '{print $4}')
    print_color $GREEN "✅ Available storage: $AVAILABLE_SPACE"

    # Check internet connection
    if ping -c 1 google.com &> /dev/null; then
        print_color $GREEN "✅ Internet connection"
    else
        print_color $RED "❌ No internet connection"
        exit 1
    fi

    echo ""
    print_color $GREEN "✅ All system checks passed!"

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Step 2: Update package list
step_update_packages() {
    show_progress
    print_header "Step 2: Updating Package Lists"

    print_color $BLUE "Updating Termux packages..."
    echo ""

    pkg update -y

    print_color $GREEN "✅ Package lists updated!"

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Step 3: Install required packages
step_install_packages() {
    show_progress
    print_header "Step 3: Installing Required Packages"

    print_color $BLUE "Installing Python, Git, and dependencies..."
    echo ""

    # Install packages one by one to show progress
    PACKAGES=("python" "git" "openssl" "libffi")

    for package in "${PACKAGES[@]}"; do
        echo -e "${BLUE}Installing $package...${NC}"
        pkg install -y "$package"
    done

    print_color $GREEN "✅ All packages installed!"

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Step 4: Install Termux:API (optional)
step_install_termux_api() {
    show_progress
    print_header "Step 4: Termux:API Setup (Optional)"

    cat << 'EOF'
Termux:API enables:
  • Biometric authentication (fingerprint)
  • Clipboard access
  • Notifications
  • Better Android integration

Note: Termux:API must be installed from F-Droid (not Google Play)
EOF

    echo ""

    if ask_yes_no "Do you want to install Termux:API support?" "y"; then
        print_color $BLUE "Installing Termux:API package..."
        pkg install -y termux-api

        print_color $YELLOW "⚠️  Important: You must also install the Termux:API app from F-Droid"
        print_color $YELLOW "    URL: https://f-droid.org/packages/com.termux.api/"
        echo ""

        if ask_yes_no "Have you installed the Termux:API app from F-Droid?" "n"; then
            # Test if it works
            if termux-fingerprint -h &> /dev/null; then
                print_color $GREEN "✅ Termux:API is working!"
            else
                print_color $YELLOW "⚠️  Termux:API app might not be installed properly"
            fi
        fi
    else
        print_color $YELLOW "Skipping Termux:API. You can install it later."
    fi

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Step 5: Clone repository
step_clone_repository() {
    show_progress
    print_header "Step 5: Downloading Perplexity to Notion"

    if [ -d "$INSTALL_DIR" ]; then
        print_color $YELLOW "⚠️  Directory already exists: $INSTALL_DIR"

        if ask_yes_no "Do you want to update it?" "y"; then
            cd "$INSTALL_DIR"
            git pull
            print_color $GREEN "✅ Repository updated!"
        fi
    else
        print_color $BLUE "Cloning repository..."
        echo ""

        git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git "$INSTALL_DIR"

        print_color $GREEN "✅ Repository cloned to $INSTALL_DIR"
    fi

    cd "$INSTALL_DIR"

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Step 6: Install Python dependencies
step_install_python_deps() {
    show_progress
    print_header "Step 6: Installing Python Dependencies"

    print_color $BLUE "Installing required Python packages..."
    echo ""

    pip install --upgrade pip
    pip install -r requirements.txt

    print_color $GREEN "✅ Python dependencies installed!"

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Step 7: Configure Notion
step_configure_notion() {
    show_progress
    print_header "Step 7: Notion Integration Setup"

    cat << 'EOF'
To export to Notion, you need an Integration Token.

📝 Follow these steps:

1. Open browser and go to: https://www.notion.so/my-integrations
2. Click "+ New integration"
3. Give it a name (e.g., "Perplexity Exporter")
4. Select your workspace
5. Click "Submit"
6. Copy the "Internal Integration Token" (starts with "secret_")
7. Important: Share your target database/page with this integration

EOF

    if ask_yes_no "Open Notion integrations page in browser?" "y"; then
        termux-open-url "https://www.notion.so/my-integrations"
    fi

    echo ""
    while true; do
        NOTION_TOKEN=$(ask_input "Paste your Notion Integration Token" "" "true")

        if [[ $NOTION_TOKEN == secret_* ]] && [ ${#NOTION_TOKEN} -gt 40 ]; then
            print_color $GREEN "✅ Token accepted!"
            break
        else
            print_color $RED "❌ Invalid token format. It should start with 'secret_'"
        fi
    done

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Step 8: Configure Perplexity (optional)
step_configure_perplexity() {
    show_progress
    print_header "Step 8: Perplexity API Setup (Optional)"

    cat << 'EOF'
The Perplexity API key enables programmatic searches.

To get your API key:
1. Go to: https://www.perplexity.ai/settings/api
2. Generate a new API key
3. Copy the key (starts with "pplx-")

If you don't have an API key, you can still use URL-based exports.
EOF

    echo ""

    if ask_yes_no "Do you have a Perplexity API key?" "n"; then
        if ask_yes_no "Open Perplexity API settings?" "y"; then
            termux-open-url "https://www.perplexity.ai/settings/api"
        fi

        PERPLEXITY_KEY=$(ask_input "Paste your Perplexity API key (or press Enter to skip)" "" "true")

        if [ -n "$PERPLEXITY_KEY" ]; then
            print_color $GREEN "✅ API key saved!"
        fi
    else
        print_color $YELLOW "Skipping Perplexity API setup"
    fi

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Step 9: Save configuration
step_save_configuration() {
    show_progress
    print_header "Step 9: Saving Configuration"

    print_color $BLUE "Creating secure configuration..."
    echo ""

    # Generate webhook API key
    WEBHOOK_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

    # Use secure storage if Termux:API is available
    if command -v termux-fingerprint &> /dev/null; then
        print_color $CYAN "🔒 Setting up biometric authentication..."

        python << EOF
from security.secure_storage_android import SecureCredentialManager

manager = SecureCredentialManager(use_biometric=True)
manager.save('NOTION_TOKEN', '$NOTION_TOKEN')
if '$PERPLEXITY_KEY':
    manager.save('PERPLEXITY_API_KEY', '$PERPLEXITY_KEY')
manager.save('WEBHOOK_API_KEY', '$WEBHOOK_KEY')

print('✅ Credentials stored securely with biometric protection')
EOF

        # Create .env with reference
        cat > .env << EOF
# Credentials are stored in secure storage
# Access them using: python security/secure_storage_android.py get KEY_NAME
EOF

        print_color $GREEN "✅ Credentials stored with biometric protection!"

    else
        # Fallback to .env file
        cat > .env << EOF
# Perplexity to Notion Configuration
# Generated by Android installer

NOTION_TOKEN=$NOTION_TOKEN
PERPLEXITY_API_KEY=$PERPLEXITY_KEY
WEBHOOK_API_KEY=$WEBHOOK_KEY
WEBHOOK_PORT=8080
EOF

        chmod 600 .env
        print_color $YELLOW "⚠️  Credentials stored in .env file (not biometric protected)"
        print_color $YELLOW "    Consider installing Termux:API for better security"
    fi

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Step 10: Create shortcuts
step_create_shortcuts() {
    show_progress
    print_header "Step 10: Creating Shortcuts"

    print_color $BLUE "Setting up convenient access..."
    echo ""

    # Create shortcuts directory for Termux:Widget
    mkdir -p ~/.shortcuts

    # Create export shortcut
    cat > ~/.shortcuts/export-to-notion << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

cd ~/Perplexity-to-Notion

# Get URL from clipboard
URL=$(termux-clipboard-get 2>/dev/null)

if [[ $URL == *"perplexity.ai"* ]]; then
    echo "📤 Exporting: $URL"
    python perplexity_to_notion.py --source "$URL"

    if [ $? -eq 0 ]; then
        termux-notification --title "Export Success" --content "Saved to Notion"
        termux-vibrate -d 200
    else
        termux-notification --title "Export Failed" --content "Check logs"
        termux-vibrate -d 500
    fi
else
    echo "❌ No Perplexity URL in clipboard"
    termux-toast "Copy a Perplexity URL first"
fi
EOF

    chmod +x ~/.shortcuts/export-to-notion

    # Create webhook server shortcut
    cat > ~/.shortcuts/start-webhook << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

cd ~/Perplexity-to-Notion
python perplexity_to_notion.py --webhook --port 8080
EOF

    chmod +x ~/.shortcuts/start-webhook

    # Create alias in bashrc
    if ! grep -q "Perplexity to Notion" ~/.bashrc 2>/dev/null; then
        cat >> ~/.bashrc << 'EOF'

# Perplexity to Notion Aliases
alias ptn='cd ~/Perplexity-to-Notion && python perplexity_to_notion.py'
alias ptn-export='cd ~/Perplexity-to-Notion && bash ~/.shortcuts/export-to-notion'
alias ptn-webhook='cd ~/Perplexity-to-Notion && bash ~/.shortcuts/start-webhook'
EOF
    fi

    print_color $GREEN "✅ Shortcuts created!"
    echo ""
    print_color $CYAN "Available shortcuts:"
    echo "  • ~/.shortcuts/export-to-notion"
    echo "  • ~/.shortcuts/start-webhook"
    echo ""
    print_color $CYAN "Terminal aliases (after restart):"
    echo "  • ptn - Interactive mode"
    echo "  • ptn-export - Export from clipboard"
    echo "  • ptn-webhook - Start webhook server"

    echo ""
    if ask_yes_no "Install Termux:Widget for home screen shortcuts?" "y"; then
        print_color $YELLOW "📱 To add home screen widgets:"
        echo "  1. Install Termux:Widget from F-Droid"
        echo "  2. Long-press home screen → Widgets"
        echo "  3. Add 'Termux:Widget' widget"
        echo "  4. Tap widget to select shortcuts"
    fi

    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Final summary
show_completion() {
    clear
    print_header "🎉 Installation Complete!"

    cat << 'EOF'
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║  Your Perplexity to Notion setup is ready to use! 🚀      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

📱 How to Use:

1. Interactive Mode:
   $ ptn

2. Export from Clipboard:
   - Copy a Perplexity URL
   - Run: ptn-export
   - Or use the home screen widget

3. Start Webhook Server:
   $ ptn-webhook

4. Export Specific URL:
   $ ptn --source "https://perplexity.ai/search/..."

📱 Home Screen Widgets:

Install Termux:Widget from F-Droid to add shortcuts to your
home screen for one-tap exports!

🔒 Security:

✅ Credentials stored securely
EOF

    if command -v termux-fingerprint &> /dev/null; then
        echo "✅ Biometric authentication enabled"
    else
        echo "⚠️  Install Termux:API for biometric protection"
    fi

    cat << 'EOF'

📚 Documentation:

- README: ~/Perplexity-to-Notion/README.md
- Android Guide: ~/Perplexity-to-Notion/ANDROID_GUIDE.md
- Security: ~/Perplexity-to-Notion/SECURITY_HARDENING.md

🆘 Need Help?

Visit the GitHub repository or check the documentation.

═══════════════════════════════════════════════════════════

EOF

    if ask_yes_no "🧪 Test the installation now?" "y"; then
        print_color $CYAN "Launching interactive mode..."
        echo ""
        python perplexity_to_notion.py
    fi

    print_color $GREEN "\n✨ Thank you for using Perplexity to Notion! ✨\n"
}

# Main installation flow
main() {
    show_welcome
    step_system_check
    step_update_packages
    step_install_packages
    step_install_termux_api
    step_clone_repository
    step_install_python_deps
    step_configure_notion
    step_configure_perplexity
    step_save_configuration
    step_create_shortcuts
    show_completion
}

# Run main installation
main
