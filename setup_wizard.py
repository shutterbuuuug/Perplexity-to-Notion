#!/usr/bin/env python3
"""
Perplexity to Notion - Interactive Setup Wizard
================================================

A beautiful, guided installation wizard that walks you through the entire
setup process step-by-step, like a website registration flow.

Features:
- Interactive terminal UI with progress tracking
- Guided API key setup with instructions
- Automatic dependency installation
- Security configuration
- Desktop shortcut creation
- Test suite to verify everything works

Compatible with: macOS (M1/Intel), Linux, Windows

Usage:
    python3 setup_wizard.py                 # Run full setup
    python3 setup_wizard.py --skip-checks   # Skip internet connection check

Author: Claude Code
License: MIT
"""

import os
import sys
import subprocess
import json
import secrets
import platform
import shutil
import argparse
from pathlib import Path
from typing import Optional, Dict, Tuple

# Check for required modules
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Installing required UI library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.table import Table
    from rich import box


console = Console()


class SetupWizard:
    """Interactive setup wizard for Perplexity to Notion."""

    def __init__(self, skip_checks=False):
        """Initialize the setup wizard.

        Args:
            skip_checks: If True, skip internet connection check
        """
        self.console = Console()
        self.project_dir = Path(__file__).parent.absolute()
        self.config = {}
        self.current_step = 0
        self.total_steps = 8
        self.skip_checks = skip_checks

        # Detect platform
        self.platform = platform.system()
        self.is_macos = self.platform == "Darwin"
        self.is_linux = self.platform == "Linux"
        self.is_windows = self.platform == "Windows"
        self.is_m1 = platform.machine() == "arm64" and self.is_macos

    def show_welcome(self):
        """Display welcome screen."""
        self.console.clear()

        welcome_text = """
# 🎉 Welcome to Perplexity to Notion Setup

This wizard will guide you through the setup process step-by-step.

## What we'll do together:

1. ✅ Check system requirements
2. 📦 Install dependencies
3. 🔑 Configure API credentials
4. 🔒 Set up security
5. 🧪 Test the connection
6. 🚀 Create shortcuts
7. 📱 Mobile setup (optional)
8. ✨ Final verification

**Estimated time:** 10-15 minutes

Press Enter to begin the setup...
        """

        panel = Panel(
            Markdown(welcome_text),
            title="[bold cyan]Perplexity to Notion Setup Wizard[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        )

        self.console.print(panel)
        input()

    def show_progress(self):
        """Show current progress."""
        progress_bar = f"Step {self.current_step}/{self.total_steps}"
        percentage = int((self.current_step / self.total_steps) * 100)

        bar_length = 30
        filled = int(bar_length * self.current_step / self.total_steps)
        bar = "█" * filled + "░" * (bar_length - filled)

        self.console.print(f"\n[cyan]{progress_bar}[/cyan] [{percentage}%] {bar}\n")

    def step_system_check(self):
        """Step 1: Check system requirements."""
        self.current_step = 1
        self.console.clear()
        self.show_progress()

        self.console.print(Panel(
            "[bold]Step 1: System Requirements Check[/bold]\n\n"
            "Checking your system...",
            border_style="green"
        ))

        checks = []

        # Check Python version
        py_version = sys.version_info
        if py_version >= (3, 8):
            checks.append(("✅", f"Python {py_version.major}.{py_version.minor}.{py_version.micro}"))
        else:
            checks.append(("❌", f"Python {py_version.major}.{py_version.minor} (3.8+ required)"))

        # Check platform
        platform_name = platform.system()
        if self.is_m1:
            platform_name += " (Apple Silicon M1)"
        checks.append(("✅", f"Platform: {platform_name}"))

        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"],
                         capture_output=True, check=True)
            checks.append(("✅", "pip is installed"))
        except:
            checks.append(("❌", "pip not found"))

        # Check git
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            checks.append(("✅", "git is installed"))
        except:
            checks.append(("⚠️", "git not found (optional)"))

        # Check internet connection
        if not self.skip_checks:
            try:
                import urllib.request
                urllib.request.urlopen('https://www.google.com', timeout=3)
                checks.append(("✅", "Internet connection"))
            except:
                checks.append(("⚠️", "Internet connection check failed (skippable)"))
        else:
            checks.append(("⏭️", "Internet connection check (skipped)"))

        # Display results
        table = Table(show_header=False, box=box.SIMPLE)
        for status, check in checks:
            table.add_row(status, check)

        self.console.print("\n")
        self.console.print(table)

        # Only fail on critical errors (not warnings)
        critical_failures = [check for check in checks if check[0] == "❌"]
        if critical_failures:
            self.console.print("\n[red]⚠️  Some requirements are not met. Please fix them and try again.[/red]")
            sys.exit(1)

        # Show warning if there are any warnings
        if any(check[0] == "⚠️" for check in checks):
            self.console.print("\n[yellow]⚠️  Some checks failed but setup can continue.[/yellow]")
            if not self.skip_checks:
                self.console.print("[dim]Tip: Use --skip-checks to skip internet connection check[/dim]")

        self.console.print("\n[green]✅ All system checks passed![/green]")
        input("\nPress Enter to continue...")

    def step_install_dependencies(self):
        """Step 2: Install Python dependencies."""
        self.current_step = 2
        self.console.clear()
        self.show_progress()

        self.console.print(Panel(
            "[bold]Step 2: Installing Dependencies[/bold]\n\n"
            "Installing required Python packages...",
            border_style="green"
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Installing packages...", total=None)

            try:
                # Install from requirements.txt
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                progress.update(task, description="✅ All packages installed")
            except subprocess.CalledProcessError as e:
                progress.update(task, description="❌ Installation failed")
                self.console.print(f"\n[red]Error installing dependencies: {e}[/red]")
                sys.exit(1)

        self.console.print("\n[green]✅ Dependencies installed successfully![/green]")
        input("\nPress Enter to continue...")

    def step_notion_setup(self) -> str:
        """Step 3: Set up Notion integration."""
        self.current_step = 3
        self.console.clear()
        self.show_progress()

        guide = """
[bold]Step 3: Notion Integration Setup[/bold]

To export to Notion, you need an Integration Token.

[cyan]📝 Follow these steps:[/cyan]

1. Open your browser and go to: [link]https://www.notion.so/my-integrations[/link]
2. Click [bold]"+ New integration"[/bold]
3. Give it a name (e.g., "Perplexity Exporter")
4. Select your workspace
5. Click [bold]"Submit"[/bold]
6. Copy the [bold]"Internal Integration Token"[/bold] (starts with "secret_")
7. **Important:** Share your target database/page with this integration:
   - Open the database/page in Notion
   - Click "Share" in the top right
   - Invite your integration

[yellow]⚠️  Keep this token secret! It grants access to your Notion workspace.[/yellow]
        """

        self.console.print(Panel(Markdown(guide), border_style="green"))

        # Offer to open browser
        if Confirm.ask("\n🌐 Open Notion integrations page in browser?", default=True):
            url = "https://www.notion.so/my-integrations"
            if self.is_macos:
                subprocess.run(["open", url])
            elif self.is_linux:
                subprocess.run(["xdg-open", url])
            elif self.is_windows:
                subprocess.run(["start", url], shell=True)

        # Get token from user
        self.console.print("\n")
        while True:
            token = Prompt.ask(
                "📋 Paste your Notion Integration Token",
                password=True
            )

            if token.startswith("secret_") and len(token) > 40:
                self.config['NOTION_TOKEN'] = token
                self.console.print("[green]✅ Token saved![/green]")
                break
            else:
                self.console.print("[red]❌ Invalid token format. It should start with 'secret_'[/red]")

        input("\nPress Enter to continue...")
        return token

    def step_perplexity_setup(self):
        """Step 4: Set up Perplexity API (optional)."""
        self.current_step = 4
        self.console.clear()
        self.show_progress()

        guide = """
[bold]Step 4: Perplexity API Setup (Optional)[/bold]

The Perplexity API key enables programmatic searches.

[cyan]📝 To get your API key:[/cyan]

1. Go to: [link]https://www.perplexity.ai/settings/api[/link]
2. Generate a new API key
3. Copy the key (starts with "pplx-")

[dim]If you don't have an API key, you can still use URL-based exports.[/dim]
        """

        self.console.print(Panel(Markdown(guide), border_style="green"))

        if Confirm.ask("\n❓ Do you have a Perplexity API key?", default=False):
            # Open browser
            if Confirm.ask("🌐 Open Perplexity API settings?", default=True):
                url = "https://www.perplexity.ai/settings/api"
                if self.is_macos:
                    subprocess.run(["open", url])
                elif self.is_linux:
                    subprocess.run(["xdg-open", url])
                elif self.is_windows:
                    subprocess.run(["start", url], shell=True)

            self.console.print("\n")
            api_key = Prompt.ask(
                "📋 Paste your Perplexity API key",
                password=True,
                default=""
            )

            if api_key:
                self.config['PERPLEXITY_API_KEY'] = api_key
                self.console.print("[green]✅ API key saved![/green]")
        else:
            self.console.print("\n[dim]Skipping Perplexity API setup. You can add it later in .env[/dim]")

        input("\nPress Enter to continue...")

    def step_security_setup(self):
        """Step 5: Configure security settings."""
        self.current_step = 5
        self.console.clear()
        self.show_progress()

        self.console.print(Panel(
            "[bold]Step 5: Security Configuration[/bold]\n\n"
            "Setting up secure credentials...",
            border_style="green"
        ))

        # Generate webhook API key
        webhook_key = secrets.token_urlsafe(32)
        self.config['WEBHOOK_API_KEY'] = webhook_key

        # Security options
        self.console.print("\n[cyan]Security Options:[/cyan]\n")

        use_https = Confirm.ask("🔒 Generate HTTPS certificate for webhook?", default=True)

        if use_https:
            self.console.print("\n[dim]Generating self-signed certificate...[/dim]")
            try:
                subprocess.run(
                    [sys.executable, "security/generate_https_cert.py",
                     "--domain", "localhost", "--output-dir", "certs"],
                    check=True,
                    capture_output=True
                )
                self.console.print("[green]✅ HTTPS certificate generated![/green]")
                self.config['USE_HTTPS'] = 'true'
            except subprocess.CalledProcessError:
                self.console.print("[yellow]⚠️  Certificate generation failed. You can do this later.[/yellow]")
                self.config['USE_HTTPS'] = 'false'

        # Set webhook port
        port = Prompt.ask("\n🔌 Webhook server port", default="8080")
        self.config['WEBHOOK_PORT'] = port

        self.console.print("\n[green]✅ Security configured![/green]")
        input("\nPress Enter to continue...")

    def step_save_config(self):
        """Step 6: Save configuration."""
        self.current_step = 6
        self.console.clear()
        self.show_progress()

        self.console.print(Panel(
            "[bold]Step 6: Saving Configuration[/bold]\n\n"
            "Creating configuration files...",
            border_style="green"
        ))

        # Create .env file
        env_content = f"""# Perplexity to Notion Configuration
# Generated by setup wizard on {platform.node()}

# Notion Integration Token (Required)
NOTION_TOKEN={self.config.get('NOTION_TOKEN', '')}

# Perplexity API Key (Optional)
PERPLEXITY_API_KEY={self.config.get('PERPLEXITY_API_KEY', '')}

# Webhook Security
WEBHOOK_API_KEY={self.config.get('WEBHOOK_API_KEY', '')}
WEBHOOK_PORT={self.config.get('WEBHOOK_PORT', '8080')}
USE_HTTPS={self.config.get('USE_HTTPS', 'false')}

# Notion MCP Endpoint (Default)
NOTION_MCP_ENDPOINT=https://mcp.notion.com/mcp
"""

        env_file = self.project_dir / '.env'
        env_file.write_text(env_content)
        env_file.chmod(0o600)  # Secure permissions

        self.console.print("✅ Created .env file with secure permissions")

        # Create a setup info file
        setup_info = {
            'setup_date': str(Path.cwd()),
            'platform': self.platform,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
            'webhook_port': self.config.get('WEBHOOK_PORT'),
            'https_enabled': self.config.get('USE_HTTPS') == 'true',
            'has_perplexity_key': bool(self.config.get('PERPLEXITY_API_KEY'))
        }

        setup_file = self.project_dir / '.perplexity-notion' / 'setup_info.json'
        setup_file.parent.mkdir(exist_ok=True)
        setup_file.write_text(json.dumps(setup_info, indent=2))

        self.console.print("✅ Created setup information file")
        self.console.print("\n[green]✅ Configuration saved successfully![/green]")
        input("\nPress Enter to continue...")

    def step_test_connection(self):
        """Step 7: Test Notion connection."""
        self.current_step = 7
        self.console.clear()
        self.show_progress()

        self.console.print(Panel(
            "[bold]Step 7: Testing Connection[/bold]\n\n"
            "Verifying your Notion integration...",
            border_style="green"
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Testing Notion connection...", total=None)

            try:
                # Import and test
                from notion_client import Client

                notion = Client(auth=self.config['NOTION_TOKEN'])
                response = notion.search(filter={"property": "object", "value": "page"})

                count = len(response.get('results', []))

                progress.update(task, description=f"✅ Connected! Found {count} accessible pages")

                self.console.print(f"\n[green]✅ Connection successful![/green]")
                self.console.print(f"[dim]Found {count} pages you can access[/dim]")

                if count == 0:
                    self.console.print("\n[yellow]⚠️  No pages found. Make sure to share your databases with the integration![/yellow]")

            except Exception as e:
                progress.update(task, description="❌ Connection failed")
                self.console.print(f"\n[red]❌ Connection failed: {e}[/red]")
                self.console.print("\n[yellow]Please check your token and try again.[/yellow]")

        input("\nPress Enter to continue...")

    def step_create_shortcuts(self):
        """Step 8: Create desktop shortcuts."""
        self.current_step = 8
        self.console.clear()
        self.show_progress()

        self.console.print(Panel(
            "[bold]Step 8: Creating Shortcuts[/bold]\n\n"
            "Setting up easy access...",
            border_style="green"
        ))

        shortcuts_created = []

        if self.is_macos:
            # Create macOS app
            if Confirm.ask("\n🍎 Create macOS Application?", default=True):
                self.create_macos_app()
                shortcuts_created.append("macOS Application in Applications folder")

        elif self.is_linux:
            # Create Linux desktop entry
            if Confirm.ask("\n🐧 Create desktop launcher?", default=True):
                self.create_linux_desktop_entry()
                shortcuts_created.append("Desktop launcher")

        elif self.is_windows:
            # Create Windows shortcut
            if Confirm.ask("\n🪟 Create desktop shortcut?", default=True):
                self.create_windows_shortcut()
                shortcuts_created.append("Desktop shortcut")

        # Create terminal aliases
        if Confirm.ask("\n💻 Add terminal aliases?", default=True):
            self.create_terminal_aliases()
            shortcuts_created.append("Terminal aliases (ptn, ptn-webhook)")

        if shortcuts_created:
            self.console.print("\n[green]✅ Shortcuts created:[/green]")
            for shortcut in shortcuts_created:
                self.console.print(f"  • {shortcut}")

        input("\nPress Enter to continue...")

    def create_macos_app(self):
        """Create a macOS .app bundle."""
        app_name = "Perplexity to Notion"
        app_path = Path.home() / "Applications" / f"{app_name}.app"

        # Create app bundle structure
        contents = app_path / "Contents"
        macos = contents / "MacOS"
        resources = contents / "Resources"

        macos.mkdir(parents=True, exist_ok=True)
        resources.mkdir(parents=True, exist_ok=True)

        # Create Info.plist
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.perplexity.notion</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
</dict>
</plist>"""

        (contents / "Info.plist").write_text(plist)

        # Create launcher script
        launcher = f"""#!/bin/bash
cd "{self.project_dir}"
{sys.executable} perplexity_to_notion.py "$@"
"""

        launcher_path = macos / "launcher"
        launcher_path.write_text(launcher)
        launcher_path.chmod(0o755)

        self.console.print(f"[green]✅ Created macOS app: {app_path}[/green]")

    def create_linux_desktop_entry(self):
        """Create Linux .desktop file."""
        desktop_entry = f"""[Desktop Entry]
Name=Perplexity to Notion
Comment=Export Perplexity research to Notion
Exec={sys.executable} {self.project_dir}/perplexity_to_notion.py
Terminal=true
Type=Application
Categories=Utility;Network;
"""

        desktop_file = Path.home() / ".local" / "share" / "applications" / "perplexity-notion.desktop"
        desktop_file.parent.mkdir(parents=True, exist_ok=True)
        desktop_file.write_text(desktop_entry)
        desktop_file.chmod(0o755)

        self.console.print(f"[green]✅ Created desktop entry[/green]")

    def create_windows_shortcut(self):
        """Create Windows shortcut."""
        # Note: This requires pywin32, so we'll create a batch file instead
        batch_file = Path.home() / "Desktop" / "Perplexity to Notion.bat"
        batch_content = f"""@echo off
cd /d "{self.project_dir}"
"{sys.executable}" perplexity_to_notion.py %*
pause
"""
        batch_file.write_text(batch_content)
        self.console.print(f"[green]✅ Created desktop shortcut[/green]")

    def create_terminal_aliases(self):
        """Create terminal aliases for easy access."""
        aliases = f"""
# Perplexity to Notion Aliases
alias ptn='cd {self.project_dir} && {sys.executable} perplexity_to_notion.py'
alias ptn-webhook='cd {self.project_dir} && {sys.executable} perplexity_to_notion.py --webhook --port {self.config.get("WEBHOOK_PORT", "8080")}'
"""

        # Determine shell config file
        shell = os.environ.get('SHELL', '')
        if 'zsh' in shell:
            rc_file = Path.home() / '.zshrc'
        elif 'bash' in shell:
            rc_file = Path.home() / '.bashrc'
        else:
            rc_file = Path.home() / '.profile'

        # Append aliases if not already present
        if rc_file.exists():
            content = rc_file.read_text()
            if 'Perplexity to Notion Aliases' not in content:
                with open(rc_file, 'a') as f:
                    f.write(aliases)
                self.console.print(f"[green]✅ Added aliases to {rc_file.name}[/green]")
                self.console.print("[dim]Run 'source ~/{rc_file.name}' or restart terminal[/dim]")

    def show_completion(self):
        """Show setup completion summary."""
        self.console.clear()

        summary = f"""
# 🎉 Setup Complete!

Your Perplexity to Notion automation is ready to use!

## 📋 What was configured:

✅ Python dependencies installed
✅ Notion integration connected
{"✅ Perplexity API configured" if self.config.get('PERPLEXITY_API_KEY') else "⚠️  Perplexity API not configured (optional)"}
✅ Security settings applied
✅ Configuration saved to .env
{"✅ HTTPS certificate generated" if self.config.get('USE_HTTPS') == 'true' else ""}
✅ Desktop shortcuts created

## 🚀 How to use:

### Interactive Mode
```bash
python3 perplexity_to_notion.py
```

### Export URL
```bash
python3 perplexity_to_notion.py --source "https://perplexity.ai/search/..."
```

### Start Webhook Server
```bash
python3 perplexity_to_notion.py --webhook --port {self.config.get('WEBHOOK_PORT', '8080')}
```

### Using Terminal Aliases (after restart)
```bash
ptn              # Interactive mode
ptn-webhook      # Start webhook server
```

## 📱 Mobile Setup (Android)

To set up on your Android device, run:
```bash
python3 android_installer.sh
```

This will guide you through the Termux setup process.

## 📚 Documentation

- 📖 README: {self.project_dir}/README.md
- 🔒 Security Guide: {self.project_dir}/SECURITY_HARDENING.md
- 📱 Android Guide: {self.project_dir}/ANDROID_GUIDE.md

## ⚠️  Important Security Notes

- Your credentials are stored in: {self.project_dir}/.env
- Keep this file secure (already set to 600 permissions)
- Never commit .env to version control
- Review SECURITY_HARDENING.md before production use

## 🆘 Need Help?

- Check the README for detailed usage instructions
- Review the troubleshooting section
- Open an issue on GitHub

---

**Enjoy seamless research exports! 🚀**
        """

        self.console.print(Panel(Markdown(summary), title="[bold green]Setup Complete[/bold green]", border_style="green"))

        # Offer to test now
        if Confirm.ask("\n\n🧪 Would you like to test the system now?", default=True):
            self.console.print("\n[cyan]Launching interactive mode...[/cyan]\n")
            subprocess.run([sys.executable, "perplexity_to_notion.py"])

        self.console.print("\n[bold green]Thank you for using Perplexity to Notion! 🎉[/bold green]\n")

    def run(self):
        """Run the complete setup wizard."""
        try:
            self.show_welcome()
            self.step_system_check()
            self.step_install_dependencies()
            self.step_notion_setup()
            self.step_perplexity_setup()
            self.step_security_setup()
            self.step_save_config()
            self.step_test_connection()
            self.step_create_shortcuts()
            self.show_completion()
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]Setup cancelled by user.[/yellow]")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"\n\n[red]Setup failed: {e}[/red]")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Perplexity to Notion - Interactive Setup Wizard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 setup_wizard.py                    # Run full setup with all checks
  python3 setup_wizard.py --skip-checks      # Skip internet connection check

For more information, see the README.md file.
        """
    )
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip internet connection check (useful if already connected but check fails)'
    )

    args = parser.parse_args()

    wizard = SetupWizard(skip_checks=args.skip_checks)
    wizard.run()


if __name__ == '__main__':
    main()
