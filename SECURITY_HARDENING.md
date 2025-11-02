# Security Hardening Guide

**Comprehensive guide to securing your Perplexity to Notion deployment**

⚠️ **CRITICAL**: Do NOT use this system in production without implementing the security measures outlined in this guide.

---

## Table of Contents

1. [Pre-Deployment Security Checklist](#pre-deployment-security-checklist)
2. [Desktop Security Hardening](#desktop-security-hardening)
3. [Mobile Security Hardening](#mobile-security-hardening)
4. [Webhook Server Security](#webhook-server-security)
5. [Credential Management](#credential-management)
6. [Network Security](#network-security)
7. [Monitoring & Incident Response](#monitoring--incident-response)
8. [Security Maintenance](#security-maintenance)

---

## Pre-Deployment Security Checklist

### Critical (P0) - Must Complete Before Any Use

- [ ] **HTTPS Enforcement**
  ```bash
  # Generate self-signed certificate for dev
  cd security
  python generate_https_cert.py

  # Or use Let's Encrypt for production
  sudo certbot certonly --standalone -d your-domain.com
  ```

- [ ] **Enable Authentication**
  ```python
  # In your .env file
  WEBHOOK_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
  ```

- [ ] **Rate Limiting**
  ```python
  # Already implemented in auth_manager.py
  # Ensure it's enabled in webhook_server.py
  ```

- [ ] **Secure Credential Storage** (Mobile)
  ```bash
  # Migrate from plaintext .env
  python security/secure_storage_android.py migrate .env
  ```

### High Priority (P1) - Complete Within 1 Week

- [ ] **Input Validation**
  - Enable URL validation
  - Enable content sanitization
  - Test with malicious inputs

- [ ] **Device Registration**
  - Generate device certificates
  - Test device revocation
  - Document device management process

- [ ] **Audit Logging**
  - Enable comprehensive logging
  - Set up log rotation
  - Configure log monitoring

### Medium Priority (P2) - Complete Within 1 Month

- [ ] **OAuth Implementation**
  - Set up Notion OAuth app
  - Implement authorization flow
  - Test token refresh

- [ ] **Biometric Authentication** (Mobile)
  - Install Termux:API
  - Test fingerprint auth
  - Document setup for users

- [ ] **Security Monitoring**
  - Set up alerting
  - Configure dashboards
  - Test incident response

---

## Desktop Security Hardening

### 1. Secure Credential Storage

**Problem**: `.env` file in plaintext

**Solution**:

```bash
# Set proper file permissions
chmod 600 .env

# Better: Use system keyring
pip install keyring
python -c "import keyring; keyring.set_password('perplexity-notion', 'NOTION_TOKEN', 'your-token')"
```

**In your code**:
```python
import keyring

# Instead of os.getenv
notion_token = keyring.get_password('perplexity-notion', 'NOTION_TOKEN')
```

### 2. HTTPS for Webhook Server

**Generate Self-Signed Certificate** (Development):

```bash
# Run the provided script
python security/generate_https_cert.py --output-dir ./certs

# Or manually with OpenSSL
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

**Update webhook server**:
```python
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')

httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
```

**Production with Let's Encrypt**:

```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d api.yourdomain.com

# Certificates will be in /etc/letsencrypt/live/api.yourdomain.com/
```

### 3. Firewall Configuration

**Linux (ufw)**:
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTPS webhook only
sudo ufw allow 8443/tcp

# Enable firewall
sudo ufw enable
```

**macOS**:
```bash
# Enable firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on

# Add application
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
```

### 4. Process Isolation

**Run as non-root user**:
```bash
# Create dedicated user
sudo useradd -r -s /bin/false perplexity-notion

# Set file ownership
sudo chown -R perplexity-notion:perplexity-notion /opt/perplexity-notion

# Run as that user
sudo -u perplexity-notion python perplexity_to_notion.py --webhook
```

**Use systemd hardening** (see `examples/systemd_service.txt`):
```ini
[Service]
# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/perplexity-notion
```

---

## Mobile Security Hardening

### 1. Secure Credential Storage

**Install Required Tools**:
```bash
# Termux
pkg install termux-api python cryptography

# Install our secure storage module
pip install cryptography
```

**Migrate from Plaintext .env**:
```bash
# Run migration script
python security/secure_storage_android.py migrate ~/.perplexity-notion/.env

# This will:
# 1. Encrypt credentials with device-bound key
# 2. Enable biometric authentication
# 3. Backup and remove plaintext .env
```

**Usage in Scripts**:
```python
from security.secure_storage_android import SecureCredentialManager

# Initialize (will prompt for biometric)
manager = SecureCredentialManager(use_biometric=True)

# Get credentials
notion_token = manager.get('NOTION_TOKEN')
```

### 2. Enable Biometric Authentication

**Setup**:
```bash
# Install Termux:API from F-Droid
# https://f-droid.org/packages/com.termux.api/

# Test fingerprint sensor
termux-fingerprint

# Expected output: {"auth_result": "AUTH_RESULT_SUCCESS"}
```

**In your scripts**:
```python
# Biometric is automatically required when using SecureCredentialManager
manager = SecureCredentialManager(use_biometric=True)
credentials = manager.load()  # Prompts for fingerprint
```

### 3. Samsung Knox Integration (One UI 7+)

**Check Knox Availability**:
```bash
# Check if Knox is available
getprop ro.config.knox

# Should output: v30 or similar if Knox is present
```

**Enable Knox Features**:
```python
from security.secure_storage_android import KnoxSecureStorage

knox = KnoxSecureStorage()

if knox.knox_available:
    print("✓ Knox available")
    # Use Knox Vault for credential storage
    knox.store_in_knox_vault('NOTION_TOKEN', token)
else:
    print("ℹ Using Android Keystore fallback")
```

### 4. Network Security on Mobile

**Bind to Localhost Only**:
```bash
# In termux_shortcut.sh
python perplexity_to_notion.py --webhook --bind 127.0.0.1 --port 8080
```

**Use VPN for Remote Access**:
```bash
# Install WireGuard
pkg install wireguard-tools

# Configure VPN tunnel
# Then access webhook via VPN only
```

**Certificate Pinning** (for production):
```python
import ssl
import hashlib

def pin_certificate(cert_file):
    with open(cert_file, 'rb') as f:
        cert_data = f.read()

    pin = hashlib.sha256(cert_data).hexdigest()
    return pin

# Validate server certificate matches pin
```

### 5. Clipboard Security

**Validate Clipboard Content**:
```bash
# In termux_shortcut.sh
CLIPBOARD=$(termux-clipboard-get 2>/dev/null)

# Validate before use
if [[ $CLIPBOARD =~ ^https://www\.perplexity\.ai/search/[a-zA-Z0-9-]+$ ]]; then
    echo "✓ Valid Perplexity URL"
    python perplexity_to_notion.py --source "$CLIPBOARD"
else
    echo "✗ Invalid URL in clipboard"
    exit 1
fi
```

**Clear Sensitive Data from Clipboard**:
```bash
# After processing
termux-clipboard-set ""
```

### 6. App-to-App Authentication (Android)

**Using Android Account Manager**:

```python
# Note: Requires Android app development
# This is a reference for future native Android app

from android.accounts import AccountManager

# Add account
account_manager = AccountManager.get(context)
account = Account("user@example.com", "com.perplexity.notion")
account_manager.addAccountExplicitly(account, password, bundle)

# Get auth token
token = account_manager.blockingGetAuthToken(account, "notion_api", True)
```

---

## Webhook Server Security

### 1. HTTPS Configuration

**Self-Signed Certificate** (Development):
```bash
cd security
python generate_https_cert.py --domain localhost --output-dir ../certs
```

**Update webhook server**:
```python
# In webhook_server.py
import ssl

def run_webhook_server(app, port, logger, use_https=True):
    if use_https:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('certs/cert.pem', 'certs/key.pem')

        # Require TLS 1.2+
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
```

### 2. Rate Limiting

**Enable in webhook server**:
```python
from security.auth_manager import RateLimiter

# Initialize rate limiter
rate_limiter = RateLimiter(rate=10, per=60, burst=15)

# In request handler
def do_POST(self):
    client_id = self.client_address[0]  # IP address

    if not rate_limiter.is_allowed(client_id):
        retry_after = rate_limiter.get_retry_after(client_id)
        self.send_response(429)  # Too Many Requests
        self.send_header('Retry-After', str(int(retry_after)))
        self.end_headers()
        return

    # Process request...
```

### 3. JWT Authentication

**Generate Tokens**:
```python
from security.auth_manager import JWTAuthManager

auth = JWTAuthManager()

# Generate access token (1 hour)
access_token = auth.generate_token(
    user_id='mobile_device_1',
    expires_in=3600,
    scopes=['export:create']
)

# Generate refresh token (30 days)
refresh_token = auth.generate_refresh_token(
    user_id='mobile_device_1',
    expires_in=2592000
)

print(f"Access Token: {access_token}")
print(f"Refresh Token: {refresh_token}")
```

**Validate in Webhook**:
```python
def _authenticate(self) -> bool:
    auth_header = self.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return False

    token = auth_header[7:]

    try:
        payload = self.auth_manager.validate_token(
            token,
            required_scopes=['export:create']
        )

        # Store user info for logging
        self.user_id = payload['sub']
        self.device_id = payload['device_id']

        return True

    except jwt.InvalidTokenError as e:
        self.logger.warning(f"Auth failed: {e}")
        return False
```

### 4. Input Validation

**Enable for All Inputs**:
```python
from security.input_validator import InputValidator

validator = InputValidator()

def do_POST(self):
    # ... parse request ...

    # Validate URL
    if 'source' in payload:
        is_valid, error = validator.validate_perplexity_url(payload['source'])
        if not is_valid:
            self.send_error(400, f"Invalid URL: {error}")
            return

    # Sanitize content
    if 'content' in payload:
        is_valid, error, sanitized = validator.sanitize_notion_content(payload['content'])
        payload['content'] = sanitized
```

### 5. CORS Configuration

**Restrict Origins**:
```python
# Instead of: Access-Control-Allow-Origin: *
ALLOWED_ORIGINS = [
    'https://app.perplexity.ai',
    'https://www.notion.so'
]

def _set_headers(self):
    origin = self.headers.get('Origin', '')

    if origin in ALLOWED_ORIGINS:
        self.send_header('Access-Control-Allow-Origin', origin)

    # No wildcard!
```

### 6. Request Logging

**Comprehensive Audit Trail**:
```python
import json
from datetime import datetime

def log_request(self, status, error=None):
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'ip': self.client_address[0],
        'user_id': getattr(self, 'user_id', 'anonymous'),
        'device_id': getattr(self, 'device_id', 'unknown'),
        'method': self.command,
        'path': self.path,
        'status': status,
        'error': error,
        'user_agent': self.headers.get('User-Agent', '')
    }

    # Write to audit log
    with open('logs/audit.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

---

## Credential Management

### 1. Rotation Policy

**Notion Integration Token**:
```bash
# Rotate every 90 days
# 1. Create new integration in Notion
# 2. Update .env or secure storage
# 3. Test with new token
# 4. Revoke old token in Notion
```

**Webhook API Key**:
```bash
# Rotate every 30 days
python -c "import secrets; print(secrets.token_urlsafe(32))" > new_key.txt

# Update .env
# Distribute to authorized devices
# Delete old key after grace period
```

### 2. Token Revocation

**Revoke JWT Token**:
```python
from security.auth_manager import JWTAuthManager

auth = JWTAuthManager()

# Revoke specific token
auth.revoke_token(compromised_token)

# Revoke device
device_id = "compromised_device"
auth.device_identity.revoke_device()
```

**Revoke Notion Access**:
```
1. Go to https://www.notion.so/my-integrations
2. Find your integration
3. Click "Revoke access" or delete integration
4. Create new integration
5. Re-share databases with new integration
```

### 3. Least Privilege

**Separate Integrations per Database**:
```bash
# Instead of one integration with access to everything:
# - Create "Research Database" integration → only shared with research DB
# - Create "Notes Database" integration → only shared with notes DB
# - Use appropriate integration for each export
```

**Notion API Scopes** (when using OAuth):
```python
# Request minimal scopes
scopes = [
    'notion:databases:read',
    'notion:pages:create',
    # Don't request 'notion:pages:update' unless needed
]
```

---

## Network Security

### 1. Firewall Rules

**iptables** (Linux):
```bash
# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTPS webhook from specific IPs only
iptables -A INPUT -p tcp --dport 8443 -s 192.168.1.0/24 -j ACCEPT

# Drop all other incoming
iptables -A INPUT -j DROP
```

**nftables** (Modern Linux):
```bash
# Create table
nft add table inet filter

# Allow established connections
nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'
nft add rule inet filter input ct state established,related accept

# Allow webhook from local network only
nft add rule inet filter input ip saddr 192.168.1.0/24 tcp dport 8443 accept
```

### 2. Reverse Proxy (Nginx)

**Production Configuration**:
```nginx
# See examples/nginx.conf for full config

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;
    limit_req zone=api_limit burst=5 nodelay;

    # Proxy to webhook server
    location / {
        proxy_pass http://localhost:8080;

        # Security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
    }
}
```

### 3. VPN Access

**WireGuard Setup** (for remote mobile access):
```bash
# Server setup
apt install wireguard

# Generate keys
wg genkey | tee privatekey | wg pubkey > publickey

# Configure /etc/wireguard/wg0.conf
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = <server-private-key>

[Peer]
PublicKey = <client-public-key>
AllowedIPs = 10.0.0.2/32

# Start VPN
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
```

**Client (Mobile)**:
```bash
# Install WireGuard app from Play Store
# Import configuration:
[Interface]
PrivateKey = <client-private-key>
Address = 10.0.0.2/24

[Peer]
PublicKey = <server-public-key>
Endpoint = your-server.com:51820
AllowedIPs = 10.0.0.1/32

# Now webhook is accessible via VPN: https://10.0.0.1:8443
```

---

## Monitoring & Incident Response

### 1. Security Monitoring

**Log Analysis**:
```bash
# Monitor failed authentication attempts
grep "Auth failed" logs/audit.jsonl | jq -r '.ip' | sort | uniq -c | sort -rn

# Monitor for suspicious patterns
grep "rate limit" logs/webhook.log

# Monitor for malicious URLs
grep "Invalid URL" logs/audit.jsonl
```

**Automated Alerts**:
```bash
# Create alert script
#!/bin/bash
# check_security.sh

FAILED_AUTH=$(grep "Auth failed" /var/log/perplexity-notion/audit.jsonl | tail -100 | wc -l)

if [ $FAILED_AUTH -gt 10 ]; then
    echo "⚠️ High number of failed auth attempts: $FAILED_AUTH"
    # Send notification
    curl -X POST https://ntfy.sh/your-topic \
         -H "Title: Security Alert" \
         -d "Failed auth attempts: $FAILED_AUTH"
fi
```

**Set up cron job**:
```bash
# Run every 5 minutes
*/5 * * * * /opt/perplexity-notion/check_security.sh
```

### 2. Incident Response Plan

**If Credentials Compromised**:

1. **Immediate**:
   ```bash
   # Revoke all tokens
   python security/revoke_all_tokens.py

   # Stop webhook server
   systemctl stop perplexity-notion

   # Change all credentials
   ```

2. **Investigation**:
   ```bash
   # Review audit logs
   cat logs/audit.jsonl | jq 'select(.timestamp > "2025-11-01T00:00:00")'

   # Identify compromised exports
   # Review Notion pages created during incident window
   ```

3. **Recovery**:
   - Generate new Notion integration
   - Create new webhook API keys
   - Re-share databases with new integration
   - Update all authorized devices
   - Resume service

**If Device Lost/Stolen**:

1. **Revoke device immediately**:
   ```python
   from security.auth_manager import JWTAuthManager

   auth = JWTAuthManager()
   # Revoke all tokens for device
   auth.device_identity.revoke_device()
   ```

2. **Change credentials on remaining devices**

3. **Review exports from compromised device**

### 3. Regular Security Audits

**Weekly**:
- [ ] Review failed authentication attempts
- [ ] Check for unusual export patterns
- [ ] Verify rate limiting is working
- [ ] Review system logs for errors

**Monthly**:
- [ ] Rotate webhook API keys
- [ ] Review and update firewall rules
- [ ] Update dependencies (`pip list --outdated`)
- [ ] Test backup restoration

**Quarterly**:
- [ ] Rotate Notion integration tokens
- [ ] Penetration testing
- [ ] Security awareness training
- [ ] Review and update this document

---

## Security Maintenance

### 1. Dependency Updates

**Check for vulnerabilities**:
```bash
# Install safety
pip install safety

# Check for known vulnerabilities
safety check

# Update dependencies
pip install -r requirements.txt --upgrade
```

**Monitor security advisories**:
- GitHub Security Advisories
- Notion API changelog
- Python security announcements

### 2. Backup Strategy

**What to Backup**:
- [ ] Encrypted credentials
- [ ] Device certificates
- [ ] Audit logs
- [ ] Configuration files

**Backup Script**:
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/secure/backups/perplexity-notion"
DATE=$(date +%Y%m%d)

# Create encrypted backup
tar czf - ~/.perplexity-notion | \
    gpg --encrypt --recipient your@email.com > \
    "$BACKUP_DIR/backup-$DATE.tar.gz.gpg"

# Keep only last 30 days
find "$BACKUP_DIR" -mtime +30 -delete
```

### 3. Security Checklist (Monthly)

- [ ] All dependencies up to date
- [ ] No known vulnerabilities (`safety check`)
- [ ] SSL certificates valid and not expiring soon
- [ ] Audit logs reviewed
- [ ] Backups tested and verified
- [ ] Firewall rules reviewed
- [ ] Access list reviewed (remove inactive devices)
- [ ] Incident response plan tested

---

## Quick Reference

### Emergency Commands

**Stop webhook server**:
```bash
# Systemd
sudo systemctl stop perplexity-notion

# Manual
pkill -f "perplexity_to_notion.py --webhook"
```

**Revoke all access**:
```bash
# Delete Notion integration at:
# https://www.notion.so/my-integrations

# Revoke all JWT tokens
python -c "from security.auth_manager import JWTAuthManager; JWTAuthManager().revoked_tokens.clear()"
```

**Check for compromise**:
```bash
# Review recent exports
grep "Export" logs/audit.jsonl | tail -50

# Check for suspicious IPs
grep "POST /export" logs/audit.jsonl | jq -r '.ip' | sort | uniq -c | sort -rn
```

### Security Contacts

- **Notion Security**: security@makenotion.com
- **Report Vulnerabilities**: Create issue at GitHub (if self-hosted)

---

## Conclusion

Security is an ongoing process, not a one-time setup. Regularly review and update your security measures as threats evolve and new vulnerabilities are discovered.

**Remember**:
- ✅ Defense in depth: Multiple layers of security
- ✅ Least privilege: Minimal permissions required
- ✅ Monitoring: Know when something goes wrong
- ✅ Regular updates: Keep software patched
- ✅ Incident response: Be prepared

For questions or to report security issues, see [SECURITY.md](SECURITY.md).

---

**Last Updated**: 2025-11-01
**Next Review**: 2025-12-01
