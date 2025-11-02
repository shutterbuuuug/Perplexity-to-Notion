# Perplexity to Notion Automation

**Automate exporting your Perplexity research to Notion databases and pages**

A comprehensive, MCP-aware Python script for seamlessly integrating Perplexity AI research with Notion workspaces. Designed for both desktop and mobile (Android) usage with support for interactive CLI, automated webhooks, and one-click shortcuts.

---

## ⚠️ CRITICAL SECURITY NOTICE

**🔴 This system is NOT production-ready without security hardening!**

The base implementation has **3 CRITICAL and 7 HIGH-severity security vulnerabilities** that MUST be addressed before deployment, especially for mobile usage.

**Before using this system**:

1. **Read** [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - Detailed threat analysis
2. **Implement** security enhancements from [SECURITY_HARDENING.md](SECURITY_HARDENING.md)
3. **Use** the `security/` module components:
   - JWT authentication with expiration
   - Encrypted credential storage (mobile)
   - Input validation and sanitization
   - HTTPS enforcement
   - Rate limiting

**Key Risks Without Security Module**:
- 🔴 Plaintext HTTP communication → Credentials visible on network
- 🔴 No rate limiting → DoS attacks possible
- 🔴 Weak authentication → Easy token compromise
- 🟠 Unencrypted mobile credentials → Physical device access = theft
- 🟠 No input validation → SSRF, XSS, injection attacks

**For Personal Use**: Implement P0 (Critical) and P1 (High) fixes from hardening guide
**For Production**: Complete security audit + penetration testing required

See: **[Security Checklist →](SECURITY_HARDENING.md#pre-deployment-security-checklist)**

---

## Features

✨ **Core Functionality**
- Export Perplexity threads/reports directly to Notion
- Create new pages in databases or append to existing pages
- Preserve formatting, sources, and related questions
- Dynamic destination selection with saved preferences

🔒 **Security & Best Practices**
- Follows Notion MCP security guidelines
- Secure credential management (env vars, config files)
- OAuth and Integration Token support
- No hardcoded credentials

📱 **Mobile Optimized**
- Android support via Termux, Tasker, Automate
- Webhook server for automation apps
- One-click shortcuts for instant research saves
- Push notification support

🚀 **Developer Friendly**
- Fully annotated, production-ready code
- Comprehensive error handling and logging
- Modular architecture for easy extension
- Batch and single export modes

---

## 🚀 Quick Installation

**We've created guided installation wizards that walk you through the entire setup process!**

### 🖥️ macOS (M1/Intel Mac Mini)

**One-command installation:**

```bash
curl -sSL https://raw.githubusercontent.com/shutterbuuuug/Perplexity-to-Notion/main/install_macos.sh | bash
```

Or clone and run the interactive wizard:

```bash
git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git
cd Perplexity-to-Notion
python3 setup_wizard.py
```

The wizard will:
- ✅ Check system requirements
- ✅ Install all dependencies automatically
- ✅ Guide you through API key setup with browser links
- ✅ Configure security settings
- ✅ Test your Notion connection
- ✅ Create desktop shortcuts and terminal aliases
- ✅ Verify everything works

**Time required:** ~10-15 minutes

---

### 📱 Android (via Termux)

**One-command installation:**

```bash
curl -sSL https://raw.githubusercontent.com/shutterbuuuug/Perplexity-to-Notion/main/android_installer.sh | bash
```

Or manual installation:

```bash
# 1. Install Termux from F-Droid (NOT Google Play!)
# 2. Open Termux and run:
pkg update && pkg install git
git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git
cd Perplexity-to-Notion
bash android_installer.sh
```

The Android installer will:
- ✅ Set up Python and dependencies in Termux
- ✅ Install optional Termux:API for biometric auth
- ✅ Guide you through API key setup
- ✅ Set up encrypted credential storage with fingerprint unlock
- ✅ Create home screen shortcuts (via Termux:Widget)
- ✅ Configure clipboard export functionality

**Requirements:**
- Termux from F-Droid: https://f-droid.org/packages/com.termux/
- Termux:API (optional): https://f-droid.org/packages/com.termux.api/
- Termux:Widget (optional): https://f-droid.org/packages/com.termux.widget/

**Time required:** ~15-20 minutes

---

### 🐧 Linux / 🪟 Windows

```bash
git clone https://github.com/shutterbuuuug/Perplexity-to-Notion.git
cd Perplexity-to-Notion
python3 setup_wizard.py
```

---

## 📖 Detailed Installation Guide

For step-by-step instructions, troubleshooting, and platform-specific details, see:

**[→ Complete Installation Guide](INSTALLATION.md)**

---

## Configuration

### Method 1: Environment Variables (Recommended)

Create a `.env` file in the project directory:

```env
# Required
NOTION_TOKEN=secret_your_notion_integration_token_here

# Optional
PERPLEXITY_API_KEY=pplx-your-api-key-here
```

### Method 2: JSON Config File

Create `config.json` with your settings:

```json
{
  "notion_token": "secret_your_token_here",
  "perplexity_api_key": "pplx-your-key-here",
  "preferences": {
    "default_destination_id": "your-database-id",
    "default_destination_type": "database"
  }
}
```

Run with:
```bash
python perplexity_to_notion.py --config config.json
```

---

## Usage

### Interactive Mode

Run the script without arguments for step-by-step guidance:

```bash
python perplexity_to_notion.py
```

You'll be prompted to:
1. Select content source (URL, search query, or manual input)
2. Choose destination (database or page)
3. Confirm export

### Automated Mode

Export a Perplexity thread directly:

```bash
python perplexity_to_notion.py \
  --source "https://www.perplexity.ai/search/..." \
  --destination-id "your-notion-db-id"
```

Execute a new search and export:

```bash
python perplexity_to_notion.py \
  --search "quantum computing applications" \
  --destination-id "your-notion-db-id"
```

### Webhook Mode (for Mobile & Automation)

Start a webhook server:

```bash
python perplexity_to_notion.py --webhook --port 8080
```

The server will listen for POST requests:

```bash
curl -X POST http://localhost:8080/export \
  -H "Content-Type: application/json" \
  -d '{
    "source": "https://www.perplexity.ai/search/...",
    "destination_id": "your-db-id"
  }'
```

---

## API Setup Guides

### Notion Integration Setup

1. **Create Integration**
   - Visit https://www.notion.so/my-integrations
   - Click "+ New integration"
   - Name it (e.g., "Perplexity Exporter")
   - Select your workspace
   - Click "Submit"

2. **Copy Integration Token**
   - Copy the "Internal Integration Token" (starts with `secret_`)
   - Add to `.env` file as `NOTION_TOKEN`

3. **Share Databases/Pages**
   - Open the Notion page or database you want to export to
   - Click "Share" in the top right
   - Invite your integration
   - The script can now access that resource

4. **Find Database/Page IDs**
   - Open the page in browser
   - Copy ID from URL:
     - `https://notion.so/workspace/abc123...` → `abc123...`
   - Or use the script's interactive mode to list available resources

### Perplexity API Setup (Optional)

1. **Get API Key**
   - Visit https://www.perplexity.ai/settings/api
   - Generate a new API key
   - Add to `.env` as `PERPLEXITY_API_KEY`

2. **API Features**
   - Programmatic search execution
   - Thread/report fetching (if available)
   - Enhanced content extraction

> **Note:** Perplexity API is optional. You can still export content using URLs or manual input.

---

## Command-Line Reference

```
usage: perplexity_to_notion.py [-h] [--source SOURCE] [--search QUERY]
                                [--destination-id ID] [--destination-type {database,page}]
                                [--webhook] [--port PORT] [--config CONFIG]
                                [--verbose]

Export Perplexity research to Notion

optional arguments:
  -h, --help            show this help message and exit
  --source, -s SOURCE   Perplexity thread/report URL to export
  --search, -q QUERY    New Perplexity search query
  --destination-id, -d ID
                        Target Notion database or page ID
  --destination-type, -t {database,page}
                        Destination type (default: database)
  --webhook             Start webhook server for mobile/automation
  --port PORT           Webhook server port (default: 8080)
  --config, -c CONFIG   Path to custom config JSON file
  --verbose, -v         Enable verbose logging
```

### Examples

**Export URL to specific database:**
```bash
python perplexity_to_notion.py \
  -s "https://perplexity.ai/search/abc123" \
  -d "database-id-here" \
  -t database
```

**Run new search and export:**
```bash
python perplexity_to_notion.py \
  -q "machine learning best practices 2024" \
  -d "database-id-here"
```

**Start webhook on custom port:**
```bash
python perplexity_to_notion.py --webhook --port 5000
```

**Verbose logging for debugging:**
```bash
python perplexity_to_notion.py -v -s "https://..."
```

---

## Mobile Integration (Android)

See [ANDROID_GUIDE.md](./ANDROID_GUIDE.md) for detailed setup instructions for:

- **Termux** - Full Python environment on Android
- **Tasker** - Automation tasks and shortcuts
- **HTTP Shortcuts** - Simple webhook triggers
- **Automate** - Visual flow automation

Quick Android Setup:

1. Install Termux from F-Droid
2. Setup Python environment
3. Clone and configure this repo
4. Create home screen shortcuts

Example Termux command:
```bash
python ~/Perplexity-to-Notion/perplexity_to_notion.py \
  --source "$1" --destination-id "your-db-id"
```

See the Android guide for complete instructions and shortcut examples.

---

## Architecture & Design

### Project Structure

```
Perplexity-to-Notion/
├── perplexity_to_notion.py    # Main application script
├── webhook_server.py           # Webhook server for mobile/automation
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variable template
├── config.json.example        # JSON config template
├── README.md                  # This file
├── ANDROID_GUIDE.md           # Android integration guide
└── examples/                  # Example scripts and configs
    ├── termux_shortcut.sh
    ├── tasker_profile.xml
    └── http_shortcuts.json
```

### Core Components

**Config** (`Config` class)
- Manages API credentials and settings
- Loads from env vars, .env, and JSON files
- Validates required credentials
- Saves user preferences

**NotionManager** (`NotionManager` class)
- Handles all Notion API operations
- Follows MCP best practices
- Lists databases and pages
- Creates and updates content

**PerplexityManager** (`PerplexityManager` class)
- Fetches research from Perplexity
- Supports URL parsing and API queries
- Normalizes response format

**ContentConverter** (`ContentConverter` class)
- Converts Perplexity content to Notion blocks
- Handles formatting, sources, metadata
- Respects Notion's character limits

**PerplexityNotionApp** (Main app)
- Orchestrates the workflow
- Provides interactive CLI
- Manages automated exports
- Handles destination selection

**WebhookHandler** (Webhook server)
- HTTP server for remote triggers
- Authentication support
- Mobile-optimized responses
- CORS support for web apps

### Data Flow

```
Perplexity Source
      ↓
PerplexityManager (fetch content)
      ↓
ContentConverter (format blocks)
      ↓
NotionManager (export to API)
      ↓
Notion Workspace
```

---

## Security Best Practices

### Credential Management

✅ **DO:**
- Store tokens in `.env` or secure config files
- Use environment variables in production
- Add `.env` to `.gitignore`
- Rotate API keys regularly
- Use webhook authentication in production

❌ **DON'T:**
- Hardcode credentials in scripts
- Commit `.env` files to git
- Share tokens in screenshots or logs
- Use the same key across multiple apps

### Notion Integration Permissions

Configure minimal required permissions:
- **Read**: Access to databases/pages you need
- **Insert**: Create new pages
- **Update**: Modify existing content (if needed)

### Webhook Security

When exposing webhooks:
1. Set `WEBHOOK_API_KEY` in `.env`
2. Use HTTPS in production (reverse proxy)
3. Implement rate limiting
4. Monitor access logs
5. Restrict firewall rules

---

## Troubleshooting

### Common Issues

**"NOTION_TOKEN not found"**
- Ensure `.env` file exists in project directory
- Check token format (should start with `secret_`)
- Verify file is named exactly `.env` (not `.env.txt`)

**"No databases found"**
- Share your Notion database with the integration
- Check integration permissions
- Verify token is for the correct workspace

**"Connection test failed"**
- Check internet connection
- Verify Notion token is valid
- Ensure API access isn't blocked by firewall

**"Failed to fetch thread content"**
- Verify Perplexity URL is correct
- Check if content requires authentication
- Try manual input mode instead

**Webhook not accessible on mobile**
- Ensure devices are on same network
- Use server's local IP address, not `localhost`
- Check firewall rules allow port access
- Consider using ngrok for remote access

### Enable Debug Logging

Run with verbose flag for detailed logs:
```bash
python perplexity_to_notion.py --verbose
```

### Check Dependencies

Verify all packages are installed:
```bash
pip install -r requirements.txt --upgrade
```

### Test Notion Connection

Run quick connection test:
```python
from notion_client import Client

notion = Client(auth="your-token-here")
response = notion.search()
print(f"Found {len(response['results'])} items")
```

---

## Advanced Usage

### Batch Exports

Create a batch script:

```bash
#!/bin/bash
# batch_export.sh

DEST_ID="your-database-id"

python perplexity_to_notion.py -s "url1" -d "$DEST_ID"
python perplexity_to_notion.py -s "url2" -d "$DEST_ID"
python perplexity_to_notion.py -s "url3" -d "$DEST_ID"
```

### Custom Content Processing

Extend the `ContentConverter` class:

```python
class CustomConverter(ContentConverter):
    @staticmethod
    def perplexity_to_notion_blocks(data, include_metadata=True):
        blocks = ContentConverter.perplexity_to_notion_blocks(data, include_metadata)
        # Add custom blocks
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"text": {"content": "Custom note"}}],
                "icon": {"emoji": "💡"}
            }
        })
        return blocks
```

### Integration with Other Tools

**Zapier/Make.com:**
- Trigger: Perplexity search complete
- Action: HTTP POST to webhook endpoint

**IFTTT:**
- Trigger: Note saved to app
- Action: Webhook to script

**Browser Extension:**
- Inject script to add "Export to Notion" button
- POST content to local webhook

---

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
black perplexity_to_notion.py
flake8 perplexity_to_notion.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## Roadmap

- [ ] Enhanced Perplexity API integration
- [ ] Web UI for configuration
- [ ] iOS Shortcuts support
- [ ] Chrome/Firefox extension
- [ ] Notion template customization
- [ ] Multi-workspace support
- [ ] Scheduled exports
- [ ] Email integration

---

## Resources

### Documentation

- [Notion API Reference](https://developers.notion.com/reference)
- [Notion MCP Guide](https://developers.notion.com/docs/get-started-with-mcp)
- [Perplexity API Docs](https://docs.perplexity.ai/)

### Related Projects

- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) - Official Notion Python SDK
- [Termux](https://termux.dev/) - Android terminal emulator

### Support

- [GitHub Issues](https://github.com/yourusername/Perplexity-to-Notion/issues)
- [Discussions](https://github.com/yourusername/Perplexity-to-Notion/discussions)

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Acknowledgments

- Notion team for the excellent API and MCP framework
- Perplexity AI for advancing research capabilities
- Open source community for foundational libraries

---

## Changelog

### v1.0.0 (2025-11-01)
- Initial release
- Core export functionality
- Interactive and automated modes
- Webhook server for mobile
- Android integration guide
- Comprehensive documentation

---

**Made with ❤️ by the open source community**

*Export smarter, research faster, integrate better.*
