# Android Integration Guide

**Complete guide for using Perplexity to Notion on Android devices**

This guide covers multiple methods for automating Perplexity research exports on Android, from full Python environments to simple HTTP shortcuts. Choose the method that best fits your technical comfort level and use case.

---

## Table of Contents

1. [Method 1: Termux (Full Python Environment)](#method-1-termux-full-python-environment)
2. [Method 2: HTTP Shortcuts (Simple Webhooks)](#method-2-http-shortcuts-simple-webhooks)
3. [Method 3: Tasker (Advanced Automation)](#method-3-tasker-advanced-automation)
4. [Method 4: Automate (Visual Flows)](#method-4-automate-visual-flows)
5. [Method 5: Shortcuts + Remote Server](#method-5-shortcuts--remote-server)
6. [Troubleshooting](#troubleshooting)

---

## Method 1: Termux (Full Python Environment)

**Best for:** Full control, offline usage, no external server needed

Termux provides a complete Linux environment on Android, allowing you to run the Python script natively on your device.

### Prerequisites

- Android 7.0 or higher
- 200MB free storage
- Termux app (from F-Droid, NOT Google Play)

### Setup Instructions

#### Step 1: Install Termux

1. Install F-Droid from https://f-droid.org/
2. Open F-Droid and search for "Termux"
3. Install Termux
4. (Optional) Install Termux:Widget for home screen shortcuts

#### Step 2: Setup Python Environment

Open Termux and run:

```bash
# Update packages
pkg update && pkg upgrade

# Install Python and Git
pkg install python git

# Install pip dependencies
pip install --upgrade pip
```

#### Step 3: Clone and Configure

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/yourusername/Perplexity-to-Notion.git

# Enter project directory
cd Perplexity-to-Notion

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
```

Add your credentials:
```env
NOTION_TOKEN=secret_your_token_here
PERPLEXITY_API_KEY=pplx-your-key-here
```

Save with `Ctrl+X`, `Y`, `Enter`

#### Step 4: Test the Script

```bash
python perplexity_to_notion.py --help
```

#### Step 5: Create Quick Scripts

Create a wrapper script for easy execution:

```bash
nano ~/export_to_notion.sh
```

Add:
```bash
#!/data/data/com.termux/files/usr/bin/bash

# Export Perplexity to Notion - Quick Script
cd ~/Perplexity-to-Notion

# If URL provided as argument, use it
if [ ! -z "$1" ]; then
    python perplexity_to_notion.py --source "$1"
else
    # Interactive mode
    python perplexity_to_notion.py
fi
```

Make executable:
```bash
chmod +x ~/export_to_notion.sh
```

#### Step 6: Create Home Screen Shortcuts

**Using Termux:Widget:**

1. Install Termux:Widget from F-Droid
2. Create shortcuts directory:
   ```bash
   mkdir -p ~/.shortcuts
   ```

3. Create shortcut script:
   ```bash
   nano ~/.shortcuts/export-notion
   ```

4. Add content:
   ```bash
   #!/data/data/com.termux/files/usr/bin/bash
   cd ~/Perplexity-to-Notion
   python perplexity_to_notion.py
   ```

5. Make executable:
   ```bash
   chmod +x ~/.shortcuts/export-notion
   ```

6. Add widget to home screen (1x1 Termux:Widget)
7. Tap widget to run script

### Usage Examples

**Interactive Export:**
```bash
~/export_to_notion.sh
```

**Export Specific URL:**
```bash
~/export_to_notion.sh "https://perplexity.ai/search/abc123"
```

**Quick Command:**
```bash
cd ~/Perplexity-to-Notion && python perplexity_to_notion.py \
  -s "https://perplexity.ai/search/..." \
  -d "your-db-id"
```

### Advanced: Share Menu Integration

Create a script to receive shared URLs:

```bash
nano ~/bin/termux-url-opener
```

Add:
```bash
#!/data/data/com.termux/files/usr/bin/bash

url=$1

# Check if it's a Perplexity URL
if [[ $url == *"perplexity.ai"* ]]; then
    cd ~/Perplexity-to-Notion
    python perplexity_to_notion.py --source "$url"
else
    echo "Not a Perplexity URL"
fi
```

Make executable:
```bash
chmod +x ~/bin/termux-url-opener
```

Now you can share Perplexity links directly to Termux!

---

## Method 2: HTTP Shortcuts (Simple Webhooks)

**Best for:** Simplicity, no Python knowledge needed, quick setup

HTTP Shortcuts lets you create home screen shortcuts that send HTTP requests to your webhook server.

### Prerequisites

- HTTP Shortcuts app (from Play Store or F-Droid)
- Webhook server running (on desktop, VPS, or Termux)

### Setup Instructions

#### Step 1: Start Webhook Server

On your desktop or server:
```bash
python perplexity_to_notion.py --webhook --port 8080
```

On Termux (if running locally on phone):
```bash
cd ~/Perplexity-to-Notion
python perplexity_to_notion.py --webhook --port 8080 &
```

#### Step 2: Find Server IP Address

**Desktop/Laptop:**
- Windows: Run `ipconfig` in CMD
- Mac/Linux: Run `ifconfig` or `ip addr`
- Look for local IP (e.g., 192.168.1.100)

**Termux:**
```bash
ifconfig | grep "inet addr"
```

#### Step 3: Install HTTP Shortcuts

1. Install HTTP Shortcuts from Play Store
2. Open app
3. Grant necessary permissions

#### Step 4: Create Shortcut

1. Tap "+" to create new shortcut
2. Configure:
   - **Name:** Export to Notion
   - **Icon:** Choose an icon
   - **Method:** POST
   - **URL:** `http://YOUR_IP:8080/export`
   - **Request Body Type:** JSON
   - **Request Body:**
     ```json
     {
       "source": "{clipboard}",
       "destination_id": "your-notion-db-id"
     }
     ```

3. Enable "Use Response"
4. Set Response Type: "Show as toast"

#### Step 5: Create Home Screen Shortcut

1. Long press the shortcut
2. Tap "Place on Home Screen"
3. Position on home screen

### Usage

1. Copy Perplexity URL to clipboard
2. Tap home screen shortcut
3. Receive confirmation toast

### Advanced: Variable Input

Create shortcut with prompt:

**Request Body:**
```json
{
  "source": "{prompt:Perplexity URL}",
  "destination_id": "your-db-id"
}
```

Or use share menu:

**Request Body:**
```json
{
  "source": "{share_text}",
  "destination_id": "your-db-id"
}
```

Enable "Show in Share Menu" in shortcut settings.

---

## Method 3: Tasker (Advanced Automation)

**Best for:** Complex workflows, conditional logic, integration with other apps

Tasker is a powerful Android automation tool that can trigger exports based on various conditions.

### Prerequisites

- Tasker app (paid, from Play Store)
- (Optional) AutoShare plugin for share menu integration

### Setup Instructions

#### Step 1: Create Profile

1. Open Tasker
2. Go to "Profiles" tab
3. Tap "+" → Event → Plugin → AutoShare → Shared Text
4. Configure filter for Perplexity URLs

#### Step 2: Create Task

1. Name: "Export to Notion"
2. Add Action → Net → HTTP Request
3. Configure:
   - **Method:** POST
   - **URL:** `http://YOUR_IP:8080/export`
   - **Content Type:** application/json
   - **Body:**
     ```json
     {
       "source": "%astext",
       "destination_id": "your-db-id"
     }
     ```
   - **Output File:** (leave empty)

4. Add Action → Alert → Flash
   - **Text:** "Exporting to Notion..."

5. Add Action → Alert → Vibrate Pattern (on success)

#### Step 3: Create Widget

1. Long press home screen
2. Add widget → Tasker → Task Shortcut
3. Select "Export to Notion" task
4. Customize appearance

### Advanced Tasker Examples

**Auto-export on Perplexity app close:**

Profile:
- Event → App → App Changed
- App: Perplexity
- Exit Task: Export to Notion

**Export with confirmation:**

Task:
1. Variable Set: %clipboard to %CLIP
2. Input Dialog: "Export to Notion?" with %clipboard preview
3. If %input eq yes → HTTP Request
4. Else → Stop

**Scheduled batch export:**

Profile:
- Time → Daily at 11:59 PM

Task:
- Read file with URLs
- Loop through each
- HTTP Request for each URL
- Clear file when done

---

## Method 4: Automate (Visual Flows)

**Best for:** Visual programming, no coding, easy to modify

Automate (formerly Llama Lab) provides a visual flow-based automation system.

### Setup Instructions

#### Step 1: Install Automate

1. Download from Play Store
2. Grant required permissions
3. Create new flow

#### Step 2: Create Flow

1. **Start Block:** "Shared Text"
   - Filter: Perplexity URLs

2. **HTTP Request Block:**
   - Method: POST
   - URL: `http://YOUR_IP:8080/export`
   - Content type: application/json
   - Body:
     ```json
     {
       "source": "{shared_text}",
       "destination_id": "your-db-id"
     }
     ```

3. **Toast Show Block:**
   - Text: "Exported to Notion"

4. Connect blocks: Start → HTTP → Toast → End

#### Step 3: Enable Flow

1. Tap ▶ to start flow
2. Enable "Start on device boot"
3. Test by sharing Perplexity URL

### Example Flow Variations

**With confirmation dialog:**
```
Start → Dialog → If Yes → HTTP → Toast → End
                ↓ No
              Cancel → End
```

**With error handling:**
```
Start → HTTP → Success? → Toast (Success)
             ↓ Error
           Toast (Failed) → Retry?
```

---

## Method 5: Shortcuts + Remote Server

**Best for:** Access from anywhere, no local server needed

Run the webhook server on a cloud VPS and access from anywhere.

### Setup Instructions

#### Step 1: Deploy to VPS

Using DigitalOcean, AWS, Heroku, or similar:

```bash
# SSH into your server
ssh user@your-server.com

# Clone repository
git clone https://github.com/yourusername/Perplexity-to-Notion.git
cd Perplexity-to-Notion

# Install dependencies
pip3 install -r requirements.txt

# Configure .env
nano .env

# Start with systemd or PM2
```

**Systemd Service Example:**

```ini
[Unit]
Description=Perplexity to Notion Webhook
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/Perplexity-to-Notion
ExecStart=/usr/bin/python3 perplexity_to_notion.py --webhook --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Step 2: Setup HTTPS (Recommended)

Using Nginx + Let's Encrypt:

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Step 3: Secure with API Key

Add to `.env`:
```env
WEBHOOK_API_KEY=your-secret-key-here
```

Update HTTP requests to include:
```
Authorization: Bearer your-secret-key-here
```

#### Step 4: Use with Any Method

Now you can access from anywhere:
```
https://api.yourdomain.com/export
```

---

## Comparison Matrix

| Method | Difficulty | Offline | Auto-update | Flexibility | Cost |
|--------|-----------|---------|-------------|-------------|------|
| Termux | Medium | ✅ Yes | Manual | ⭐⭐⭐⭐⭐ | Free |
| HTTP Shortcuts | Easy | ❌ No | N/A | ⭐⭐⭐ | Free |
| Tasker | Hard | ❌ No | Auto | ⭐⭐⭐⭐⭐ | $3.99 |
| Automate | Medium | ❌ No | Auto | ⭐⭐⭐⭐ | Free |
| Remote Server | Hard | ❌ No | Auto | ⭐⭐⭐⭐⭐ | $5+/mo |

---

## Troubleshooting

### Common Issues

**"Connection refused" error**
- Verify server is running
- Check IP address is correct
- Ensure devices on same network (for local)
- Check firewall allows port access

**"Unauthorized" error**
- Verify API key if configured
- Check Authorization header format
- Ensure key matches server config

**Termux: "python: command not found"**
- Run: `pkg install python`
- Verify installation: `which python`

**Share menu not showing**
- Check app permissions
- Verify filter configuration
- Restart the app

**Webhook server stops on phone lock**
- Use `nohup` or `screen`:
  ```bash
  nohup python perplexity_to_notion.py --webhook &
  ```
- Enable "Acquire Wakelock" in Termux settings

### Network Configuration

**Find local IP address:**
```bash
# Termux/Linux
ip addr show | grep inet

# Check if server is accessible
curl http://localhost:8080/health
```

**Test webhook endpoint:**
```bash
curl -X POST http://YOUR_IP:8080/export \
  -H "Content-Type: application/json" \
  -d '{"content": {"title": "Test", "content": "Hello"}}'
```

### Performance Tips

**Optimize for mobile:**
- Use webhook mode instead of interactive
- Cache authentication tokens
- Minimize logging in production
- Use connection pooling for batch exports

**Battery optimization:**
- Don't run webhook server 24/7 on mobile
- Use scheduled tasks instead of background services
- Consider remote server for always-on needs

---

## Security Considerations

### Network Security

**For local webhooks:**
- Only bind to local network (0.0.0.0 is risky)
- Use firewall rules to restrict access
- Consider VPN for remote access

**For public webhooks:**
- Always use HTTPS
- Implement rate limiting
- Set strong API key
- Monitor access logs
- Use IP whitelist if possible

### Credential Safety

- Never share `.env` file
- Don't log credentials
- Rotate API keys regularly
- Use separate keys for mobile/desktop

---

## Example Workflows

### Workflow 1: Research & Save Loop

1. Open Perplexity on phone
2. Search and read research
3. Share URL to Automate
4. Automatically saved to Notion
5. Continue researching

### Workflow 2: Daily Review Export

1. Collect URLs throughout day (clipboard manager)
2. Evening: Run Tasker task
3. Batch export all saved URLs
4. Review in Notion before bed

### Workflow 3: Voice-Activated Export

Using Tasker + Voice Commands:
1. "Hey Google, export to Notion"
2. Tasker captures last Perplexity URL
3. HTTP request to webhook
4. Confirmation via TTS

---

## Resources

### Apps & Tools

- **Termux:** https://f-droid.org/packages/com.termux/
- **Termux:Widget:** https://f-droid.org/packages/com.termux.widget/
- **HTTP Shortcuts:** https://http-shortcuts.rmy.ch/
- **Tasker:** https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm
- **Automate:** https://llamalab.com/automate/

### Tutorials

- [Termux Wiki](https://wiki.termux.com/)
- [Tasker Beginner's Guide](https://tasker.joaoapps.com/userguide/en/)
- [HTTP Shortcuts Documentation](https://http-shortcuts.rmy.ch/documentation)

### Community

- [Termux Reddit](https://reddit.com/r/termux)
- [Tasker Reddit](https://reddit.com/r/tasker)

---

## Next Steps

1. Choose your preferred method
2. Follow setup instructions
3. Test with a sample export
4. Create home screen shortcuts
5. Customize to your workflow

**Happy automating! 🚀📱**
