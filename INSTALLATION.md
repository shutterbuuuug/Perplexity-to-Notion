# Installation Guide

**Quick, guided setup for desktop and mobile**

This guide covers multiple installation methods for different platforms. Choose the one that fits your needs.

---

## 🚀 Quick Installation

### macOS (M1/Intel)

**One-command installation:**

```bash
curl -sSL https://raw.githubusercontent.com/shutterbuuuug/Perplexity-to-Notion/main/install_macos.sh | bash
```

Or download and run:

```bash
git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git
cd Perplexity-to-Notion
python3 setup_wizard.py
```

### Android (Termux)

**One-command installation:**

```bash
curl -sSL https://raw.githubusercontent.com/shutterbuuuug/Perplexity-to-Notion/main/android_installer.sh | bash
```

Or manual installation:

```bash
# 1. Install Termux from F-Droid
# 2. Open Termux and run:
pkg update && pkg install git
git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git
cd Perplexity-to-Notion
bash android_installer.sh
```

### Linux

```bash
git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git
cd Perplexity-to-Notion
python3 setup_wizard.py
```

### Windows

```powershell
git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git
cd Perplexity-to-Notion
python setup_wizard.py
```

---

## 📋 What the Setup Wizard Does

The interactive setup wizard guides you through:

### Step 1: System Requirements Check ✅
- Verifies Python 3.8+
- Checks internet connection
- Validates platform compatibility

### Step 2: Install Dependencies 📦
- Installs all required Python packages
- Sets up security modules
- Configures environment

### Step 3: Notion Integration 🔑
- Opens Notion integrations page in browser
- Guides you through creating integration
- Securely stores your token
- Tests the connection

### Step 4: Perplexity API (Optional) 🔍
- Links to API key generation
- Stores key securely
- Validates format

### Step 5: Security Configuration 🔒
- Generates HTTPS certificates
- Creates webhook API key
- Sets up encryption
- Configures permissions

### Step 6: Save Configuration 💾
- Creates `.env` file with secure permissions
- Saves setup information
- Encrypts sensitive data (mobile)

### Step 7: Test Connection 🧪
- Verifies Notion access
- Lists accessible databases
- Confirms setup works

### Step 8: Create Shortcuts 🚀
- Desktop application (macOS)
- Terminal aliases (all platforms)
- Home screen widgets (Android)
- Quick-launch scripts

---

## 🎯 Platform-Specific Details

### macOS Setup

**What you'll get:**

1. **Application Bundle** (`/Applications/Perplexity to Notion.app`)
   - Double-click to launch
   - Appears in Spotlight search
   - Dock integration

2. **Terminal Aliases**
   ```bash
   ptn              # Interactive mode
   ptn-webhook      # Start webhook server
   ```

3. **Secure Storage**
   - Credentials in `~/.perplexity-notion/`
   - Proper file permissions (600)
   - Keychain integration (optional)

**M1-Specific Considerations:**
- Native ARM64 Python recommended
- Install via official Python.org installer or Homebrew
- Rosetta 2 not required

**Homebrew Users:**
```bash
# If you use Homebrew Python
brew install python3
pip3 install -r requirements.txt
```

---

### Android Setup (Termux)

**Prerequisites:**

1. **Termux** from F-Droid (NOT Google Play)
   - Download: https://f-droid.org/packages/com.termux/
   - Why F-Droid: Google Play version is outdated

2. **Termux:API** (optional but recommended)
   - Download: https://f-droid.org/packages/com.termux.api/
   - Enables biometric authentication
   - Clipboard access
   - Notifications

3. **Termux:Widget** (optional)
   - Download: https://f-droid.org/packages/com.termux.widget/
   - Adds home screen shortcuts

**What you'll get:**

1. **Home Screen Shortcuts**
   - Export from clipboard (one-tap)
   - Start webhook server
   - Interactive mode

2. **Secure Credential Storage**
   - Biometric authentication (if Termux:API installed)
   - Encrypted file storage
   - Knox Vault integration (Samsung)

3. **Terminal Aliases**
   ```bash
   ptn              # Interactive mode
   ptn-export       # Export from clipboard
   ptn-webhook      # Start webhook
   ```

**Biometric Setup:**

The installer will prompt to set up fingerprint authentication:

```
🔒 Setting up biometric authentication...
   Touch fingerprint sensor...
   ✅ Credentials stored securely with biometric protection
```

**Samsung One UI 7 Users:**

If you have a Samsung device with Knox:
- Knox Vault automatically detected
- Hardware-backed credential storage
- Enhanced security features

---

### Linux Setup

**Distribution-Specific Notes:**

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-pip git
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip git
```

**Arch:**
```bash
sudo pacman -S python python-pip git
```

**What you'll get:**

1. **Desktop Launcher** (`~/.local/share/applications/perplexity-notion.desktop`)
   - Appears in application menu
   - Searchable in GNOME/KDE

2. **Terminal Aliases**
3. **Systemd Service** (optional)
   - Auto-start webhook on boot
   - See `examples/systemd_service.txt`

---

## 🔑 API Key Setup Guide

### Notion Integration Token

**Step-by-step with screenshots:**

1. **Go to Integrations Page**
   - URL: https://www.notion.so/my-integrations
   - Login if needed

2. **Create New Integration**
   - Click "+ New integration"
   - Name: "Perplexity Exporter" (or your choice)
   - Associated workspace: Select your workspace
   - Capabilities: Leave defaults (Read content, Update content, Insert content)
   - Click "Submit"

3. **Copy Token**
   - You'll see "Internal Integration Token"
   - Click "Show" then "Copy"
   - Token looks like: `secret_abc123...`
   - **Keep this secret!**

4. **Share Databases**
   - Open any database/page you want to export to
   - Click "Share" (top right)
   - Click "Invite"
   - Find your integration name
   - Click "Invite"
   - Repeat for all target databases

**Troubleshooting:**
- **"No databases found"**: You forgot to share databases with integration
- **"Invalid token"**: Token should start with `secret_`
- **"Unauthorized"**: Check workspace association

### Perplexity API Key (Optional)

1. **Go to API Settings**
   - URL: https://www.perplexity.ai/settings/api
   - Login if needed

2. **Generate API Key**
   - Click "Generate API Key"
   - Copy the key (starts with `pplx-`)

3. **Usage Limits**
   - Free tier: Limited requests
   - Pro: More requests
   - Check current usage in settings

**Note:** API key is optional. Without it, you can still export by:
- Pasting URLs
- Manual content input

---

## ⚙️ Configuration Options

### Environment Variables (.env)

```env
# Required
NOTION_TOKEN=secret_your_token_here

# Optional
PERPLEXITY_API_KEY=pplx-your-key-here
WEBHOOK_API_KEY=auto-generated-key
WEBHOOK_PORT=8080
USE_HTTPS=true
```

### Custom Configuration (config.json)

For advanced users:

```json
{
  "notion_token": "secret_...",
  "webhook": {
    "port": 8080,
    "bind": "127.0.0.1",
    "https": true
  },
  "security": {
    "rate_limit": 10,
    "require_device_auth": true
  }
}
```

---

## 🔍 Post-Installation Verification

### Test 1: Check Installation

```bash
python3 perplexity_to_notion.py --help
```

Expected output:
```
usage: perplexity_to_notion.py [-h] [--source SOURCE] ...
Export Perplexity research to Notion
...
```

### Test 2: Test Notion Connection

```bash
python3 -c "
from notion_client import Client
notion = Client(auth='your-token')
result = notion.search(filter={'property': 'object', 'value': 'page'})
print(f'Connected! Found {len(result[\"results\"])} pages')
"
```

### Test 3: Test Security Module

```bash
python3 security/auth_manager.py
```

Expected: All tests pass with ✓

### Test 4: Run Interactive Mode

```bash
python3 perplexity_to_notion.py
```

Try exporting a test page.

---

## 🛠️ Troubleshooting

### "Setup wizard not found"

```bash
# Re-download the repository
git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git
cd Perplexity-to-Notion
```

### "Python 3.8+ required"

**macOS:**
- Download from https://www.python.org/downloads/
- Or: `brew install python3`

**Linux:**
- Ubuntu: `sudo apt install python3.10`
- Fedora: `sudo dnf install python3.10`

**Check version:**
```bash
python3 --version
```

### "Module not found" errors

```bash
# Reinstall dependencies
pip3 install -r requirements.txt --upgrade
```

### "Permission denied" on .env

```bash
# Fix permissions
chmod 600 .env
```

### Android: "Termux:API not working"

1. Ensure both packages installed:
   - Termux (main app)
   - Termux:API (helper app)
2. Both must be from F-Droid
3. Grant necessary permissions to Termux:API

### macOS: "Application can't be opened"

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /Applications/Perplexity\ to\ Notion.app
```

---

## 🔄 Updating

### Desktop

```bash
cd ~/Perplexity-to-Notion  # or your install directory
git pull
pip3 install -r requirements.txt --upgrade
```

### Android

```bash
cd ~/Perplexity-to-Notion
git pull
pip install -r requirements.txt --upgrade
```

Or re-run installer:
```bash
bash android_installer.sh
```

---

## 🗑️ Uninstallation

### macOS

```bash
# Remove application
rm -rf ~/Applications/Perplexity\ to\ Notion.app

# Remove files
rm -rf ~/Perplexity-to-Notion
rm -rf ~/.perplexity-notion

# Remove aliases
# Edit ~/.zshrc or ~/.bashrc and remove Perplexity to Notion section
```

### Android

```bash
# Remove files
rm -rf ~/Perplexity-to-Notion
rm -rf ~/.perplexity-notion

# Remove shortcuts
rm -rf ~/.shortcuts/export-to-notion
rm -rf ~/.shortcuts/start-webhook

# Remove aliases
# Edit ~/.bashrc and remove Perplexity to Notion section
```

### Revoke Notion Access

1. Go to https://www.notion.so/my-integrations
2. Find your integration
3. Click settings → "Remove integration"

---

## 📞 Getting Help

### Check Documentation

- README.md - Overview and features
- SECURITY_HARDENING.md - Security setup
- ANDROID_GUIDE.md - Detailed Android instructions
- This file - Installation help

### Common Issues

See [Troubleshooting](#troubleshooting) section above.

### Report Issues

GitHub Issues: https://github.com/shutterbuuuug/Perplexity-to-Notion/issues

### Community

- Discussions: Check GitHub Discussions
- Documentation: Review all .md files in repository

---

## ✨ Next Steps

After installation:

1. **Read the README** - Understand features and usage
2. **Review Security Guide** - Implement recommended security measures
3. **Try Mobile Setup** - Set up Android if you have a device
4. **Create First Export** - Test with a Perplexity search
5. **Customize** - Adjust settings to your needs

---

**Congratulations! You're ready to automate your research workflow! 🎉**
