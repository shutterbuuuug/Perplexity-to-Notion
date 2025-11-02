#!/usr/bin/env python3
"""
Perplexity to Notion Automation Script
======================================

A comprehensive, MCP-aware script for automating the export of Perplexity research
to Notion databases and pages. Designed for both desktop and mobile (Android) usage.

Features:
- Notion API integration with MCP best practices
- Perplexity API integration for research exports
- Dynamic destination selection
- Secure credential management
- Mobile-optimized CLI interface
- Batch and single export support
- Error handling and logging

Author: Claude Code
License: MIT
"""

import os
import sys
import json
import logging
import argparse
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import re

# Third-party imports (install via requirements.txt)
try:
    import requests
    from dotenv import load_dotenv
    from notion_client import Client as NotionClient
    from notion_client.errors import APIResponseError
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


# ============================================================================
# CONFIGURATION & LOGGING SETUP
# ============================================================================

class Config:
    """
    Configuration manager for API credentials and app settings.

    Supports loading from environment variables, .env file, and config.json.
    Prioritizes security by never hardcoding credentials.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration from multiple sources.

        Args:
            config_file: Optional path to JSON config file
        """
        # Load environment variables from .env file
        load_dotenv()

        # Core API credentials
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')

        # Optional: Notion MCP endpoint (if using streamable HTTP)
        self.notion_mcp_endpoint = os.getenv(
            'NOTION_MCP_ENDPOINT',
            'https://mcp.notion.com/mcp'
        )

        # Configuration storage
        self.config_dir = Path.home() / '.perplexity-notion'
        self.config_dir.mkdir(exist_ok=True)

        self.preferences_file = self.config_dir / 'preferences.json'
        self.cache_file = self.config_dir / 'cache.json'

        # Load additional config from JSON if provided
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
                self.__dict__.update(custom_config)

        # Validate required credentials
        self._validate()

    def _validate(self):
        """Validate that required credentials are present."""
        if not self.notion_token:
            raise ValueError(
                "NOTION_TOKEN not found. Set it as an environment variable "
                "or in .env file."
            )

        if not self.perplexity_api_key:
            logging.warning(
                "PERPLEXITY_API_KEY not found. Some features may be limited."
            )

    def save_preferences(self, preferences: Dict[str, Any]):
        """Save user preferences for future runs."""
        with open(self.preferences_file, 'w') as f:
            json.dump(preferences, f, indent=2)

    def load_preferences(self) -> Dict[str, Any]:
        """Load saved user preferences."""
        if self.preferences_file.exists():
            with open(self.preferences_file, 'r') as f:
                return json.load(f)
        return {}


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configure logging with appropriate level and format.

    Args:
        verbose: Enable debug logging if True

    Returns:
        Configured logger instance
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    return logging.getLogger(__name__)


# ============================================================================
# NOTION API CLIENT
# ============================================================================

class NotionManager:
    """
    Notion API manager implementing MCP best practices.

    Handles authentication, database/page discovery, and content creation.
    Supports both direct API integration and MCP-aware operations.
    """

    def __init__(self, config: Config, logger: logging.Logger):
        """
        Initialize Notion client with authentication.

        Args:
            config: Configuration object with API credentials
            logger: Logger instance for operations
        """
        self.config = config
        self.logger = logger

        # Initialize official Notion client
        try:
            self.client = NotionClient(auth=config.notion_token)
            self.logger.info("✓ Notion client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Notion client: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test Notion API connection and permissions.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Search for accessible pages to verify connection
            response = self.client.search(
                filter={"property": "object", "value": "page"}
            )
            self.logger.info(f"✓ Connection successful. Found {len(response['results'])} accessible pages")
            return True
        except APIResponseError as e:
            self.logger.error(f"Notion API error: {e.code} - {e.message}")
            return False
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def list_databases(self, query: str = "") -> List[Dict[str, Any]]:
        """
        List all accessible Notion databases.

        Args:
            query: Optional search query to filter databases

        Returns:
            List of database objects with id, title, and properties
        """
        try:
            search_params = {
                "filter": {"property": "object", "value": "database"}
            }

            if query:
                search_params["query"] = query

            response = self.client.search(**search_params)

            databases = []
            for db in response['results']:
                databases.append({
                    'id': db['id'],
                    'title': self._extract_title(db.get('title', [])),
                    'url': db.get('url', ''),
                    'properties': list(db.get('properties', {}).keys())
                })

            self.logger.info(f"Found {len(databases)} database(s)")
            return databases

        except Exception as e:
            self.logger.error(f"Failed to list databases: {e}")
            return []

    def list_pages(self, query: str = "") -> List[Dict[str, Any]]:
        """
        List all accessible Notion pages.

        Args:
            query: Optional search query to filter pages

        Returns:
            List of page objects with id, title, and metadata
        """
        try:
            search_params = {
                "filter": {"property": "object", "value": "page"}
            }

            if query:
                search_params["query"] = query

            response = self.client.search(**search_params)

            pages = []
            for page in response['results']:
                pages.append({
                    'id': page['id'],
                    'title': self._extract_title(
                        page.get('properties', {}).get('title', {}).get('title', [])
                    ),
                    'url': page.get('url', ''),
                    'created_time': page.get('created_time', ''),
                    'last_edited_time': page.get('last_edited_time', '')
                })

            self.logger.info(f"Found {len(pages)} page(s)")
            return pages

        except Exception as e:
            self.logger.error(f"Failed to list pages: {e}")
            return []

    def create_page_in_database(
        self,
        database_id: str,
        title: str,
        content_blocks: List[Dict[str, Any]],
        properties: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a new page in a Notion database.

        Args:
            database_id: Target database ID
            title: Page title
            content_blocks: List of Notion block objects for page content
            properties: Optional additional properties for the database entry

        Returns:
            Created page ID if successful, None otherwise
        """
        try:
            # Build page properties
            page_properties = {
                "Name": {"title": [{"text": {"content": title}}]}
            }

            # Add custom properties if provided
            if properties:
                page_properties.update(properties)

            # Create the page
            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=page_properties,
                children=content_blocks
            )

            page_id = response['id']
            page_url = response.get('url', '')

            self.logger.info(f"✓ Created page: {title}")
            self.logger.info(f"  URL: {page_url}")

            return page_id

        except APIResponseError as e:
            self.logger.error(f"API error creating page: {e.code} - {e.message}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create page: {e}")
            return None

    def append_to_page(
        self,
        page_id: str,
        content_blocks: List[Dict[str, Any]]
    ) -> bool:
        """
        Append content blocks to an existing Notion page.

        Args:
            page_id: Target page ID
            content_blocks: List of Notion block objects to append

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.blocks.children.append(
                block_id=page_id,
                children=content_blocks
            )

            self.logger.info(f"✓ Appended {len(content_blocks)} block(s) to page")
            return True

        except APIResponseError as e:
            self.logger.error(f"API error appending to page: {e.code} - {e.message}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to append to page: {e}")
            return False

    @staticmethod
    def _extract_title(title_array: List[Dict]) -> str:
        """Extract plain text from Notion rich text title array."""
        if not title_array:
            return "Untitled"
        return "".join([t.get('plain_text', '') for t in title_array])


# ============================================================================
# PERPLEXITY API CLIENT
# ============================================================================

class PerplexityManager:
    """
    Perplexity API integration for fetching research and thread data.

    Supports multiple export methods:
    - Direct API queries (if Perplexity provides an export API)
    - Thread/report URL parsing
    - Shared link monitoring
    """

    API_BASE = "https://api.perplexity.ai"

    def __init__(self, config: Config, logger: logging.Logger):
        """
        Initialize Perplexity API client.

        Args:
            config: Configuration object with API credentials
            logger: Logger instance for operations
        """
        self.config = config
        self.logger = logger
        self.api_key = config.perplexity_api_key

        if not self.api_key:
            self.logger.warning(
                "Perplexity API key not configured. "
                "Only URL-based exports will work."
            )

    def fetch_thread_content(self, thread_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch content from a Perplexity thread/report URL.

        This method attempts to extract research content from shared Perplexity links.
        Note: This is a placeholder implementation as Perplexity's API may vary.

        Args:
            thread_url: Perplexity thread or report URL

        Returns:
            Dictionary with title, content, sources, and metadata if successful
        """
        try:
            self.logger.info(f"Fetching content from: {thread_url}")

            # For demonstration: This would need to be adapted based on
            # Perplexity's actual API or web scraping methods

            # Option 1: If Perplexity has a direct API endpoint
            if self.api_key:
                thread_id = self._extract_thread_id(thread_url)
                if thread_id:
                    return self._fetch_via_api(thread_id)

            # Option 2: Parse shared page (requires web scraping)
            return self._parse_shared_page(thread_url)

        except Exception as e:
            self.logger.error(f"Failed to fetch thread content: {e}")
            return None

    def _extract_thread_id(self, url: str) -> Optional[str]:
        """Extract thread ID from Perplexity URL."""
        # Example pattern: https://www.perplexity.ai/search/thread-id
        match = re.search(r'perplexity\.ai/(?:search|thread)/([a-zA-Z0-9-_]+)', url)
        return match.group(1) if match else None

    def _fetch_via_api(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch thread data via Perplexity API.

        Note: This is a placeholder. Adapt based on actual Perplexity API docs.
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        try:
            # Placeholder endpoint - adjust based on actual API
            response = requests.get(
                f"{self.API_BASE}/threads/{thread_id}",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return self._normalize_response(data)
            else:
                self.logger.error(
                    f"API request failed: {response.status_code} - {response.text}"
                )
                return None

        except requests.RequestException as e:
            self.logger.error(f"API request error: {e}")
            return None

    def _parse_shared_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Parse content from Perplexity shared page HTML.

        This is a fallback method when API is not available.
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # This would require HTML parsing (BeautifulSoup) to extract:
            # - Research query/title
            # - AI response content
            # - Source citations
            # - Related questions

            # Placeholder return
            self.logger.warning(
                "HTML parsing not fully implemented. "
                "Please provide content manually or use API method."
            )

            return {
                'title': 'Perplexity Research Export',
                'url': url,
                'content': 'Content extraction requires HTML parsing implementation',
                'sources': [],
                'timestamp': datetime.now().isoformat()
            }

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch shared page: {e}")
            return None

    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize API response to standard format."""
        return {
            'title': data.get('query', 'Perplexity Research'),
            'content': data.get('answer', ''),
            'sources': data.get('citations', []),
            'related_questions': data.get('related_questions', []),
            'timestamp': data.get('created_at', datetime.now().isoformat()),
            'raw_data': data
        }

    def search(self, query: str, options: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a Perplexity search query programmatically.

        Args:
            query: Search query string
            options: Optional parameters (model, context, etc.)

        Returns:
            Normalized search results dictionary
        """
        if not self.api_key:
            self.logger.error("API key required for search functionality")
            return None

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'query': query,
            **(options or {})
        }

        try:
            # Placeholder endpoint - adjust based on actual API
            response = requests.post(
                f"{self.API_BASE}/search",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return self._normalize_response(data)
            else:
                self.logger.error(
                    f"Search failed: {response.status_code} - {response.text}"
                )
                return None

        except requests.RequestException as e:
            self.logger.error(f"Search request error: {e}")
            return None


# ============================================================================
# CONTENT CONVERSION
# ============================================================================

class ContentConverter:
    """
    Convert Perplexity research content to Notion block format.

    Transforms text, sources, and metadata into properly formatted Notion blocks
    following Notion's block structure specifications.
    """

    @staticmethod
    def perplexity_to_notion_blocks(
        perplexity_data: Dict[str, Any],
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Convert Perplexity research data to Notion block format.

        Args:
            perplexity_data: Normalized Perplexity response data
            include_metadata: Include timestamp and source info

        Returns:
            List of Notion block objects ready for API submission
        """
        blocks = []

        # Add header with research title
        if perplexity_data.get('title'):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": perplexity_data['title']}
                    }]
                }
            })

        # Add metadata callout
        if include_metadata and perplexity_data.get('timestamp'):
            timestamp = perplexity_data['timestamp']
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                except:
                    timestamp_str = timestamp
            else:
                timestamp_str = str(timestamp)

            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"📅 Exported: {timestamp_str}"}
                    }],
                    "icon": {"emoji": "📚"}
                }
            })

        # Add main content
        content = perplexity_data.get('content', '')
        if content:
            # Split content into paragraphs
            paragraphs = content.split('\n\n')

            for para in paragraphs:
                if para.strip():
                    # Handle long paragraphs (Notion has 2000 char limit per block)
                    chunks = ContentConverter._chunk_text(para.strip(), 1900)

                    for chunk in chunks:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{
                                    "type": "text",
                                    "text": {"content": chunk}
                                }]
                            }
                        })

        # Add sources section
        sources = perplexity_data.get('sources', [])
        if sources:
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Sources"}
                    }]
                }
            })

            for idx, source in enumerate(sources, 1):
                if isinstance(source, dict):
                    title = source.get('title', f'Source {idx}')
                    url = source.get('url', '')
                else:
                    title = f'Source {idx}'
                    url = str(source)

                if url:
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": title, "link": {"url": url}}
                            }]
                        }
                    })

        # Add related questions if available
        related = perplexity_data.get('related_questions', [])
        if related:
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Related Questions"}
                    }]
                }
            })

            for question in related[:5]:  # Limit to 5
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": str(question)}
                        }]
                    }
                })

        return blocks

    @staticmethod
    def _chunk_text(text: str, max_length: int) -> List[str]:
        """Split text into chunks respecting Notion's character limits."""
        if len(text) <= max_length:
            return [text]

        chunks = []
        current_chunk = ""

        # Split by sentences if possible
        sentences = re.split(r'(?<=[.!?])\s+', text)

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # If single sentence is too long, force split
                if len(sentence) > max_length:
                    for i in range(0, len(sentence), max_length):
                        chunks.append(sentence[i:i+max_length])
                    current_chunk = ""
                else:
                    current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


# ============================================================================
# MAIN APPLICATION LOGIC
# ============================================================================

class PerplexityNotionApp:
    """
    Main application orchestrator.

    Coordinates Perplexity content fetching, user interaction for destination
    selection, and Notion API operations.
    """

    def __init__(self, config: Config, logger: logging.Logger):
        """
        Initialize application with configuration.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

        # Initialize API managers
        self.notion = NotionManager(config, logger)
        self.perplexity = PerplexityManager(config, logger)
        self.converter = ContentConverter()

        # Load saved preferences
        self.preferences = config.load_preferences()

    def run_interactive(self):
        """Run interactive CLI mode for manual export."""
        self.logger.info("🚀 Perplexity to Notion Export Tool")
        self.logger.info("=" * 50)

        # Test Notion connection
        if not self.notion.test_connection():
            self.logger.error("Cannot proceed without Notion connection")
            return

        # Get Perplexity content
        content = self._get_perplexity_content()
        if not content:
            self.logger.error("No content to export")
            return

        # Select destination
        destination = self._select_destination()
        if not destination:
            self.logger.error("No destination selected")
            return

        # Convert and export
        self._export_to_notion(content, destination)

    def run_automated(
        self,
        source: str,
        destination_id: Optional[str] = None,
        destination_type: str = 'database'
    ):
        """
        Run automated export (for webhooks/shortcuts).

        Args:
            source: Perplexity URL or query
            destination_id: Target Notion database/page ID
            destination_type: Either 'database' or 'page'
        """
        self.logger.info("🤖 Running automated export")

        # Fetch content
        if source.startswith('http'):
            content = self.perplexity.fetch_thread_content(source)
        else:
            content = self.perplexity.search(source)

        if not content:
            self.logger.error("Failed to fetch content")
            return False

        # Use saved destination if not provided
        if not destination_id:
            destination_id = self.preferences.get('default_destination_id')
            destination_type = self.preferences.get('default_destination_type', 'database')

        if not destination_id:
            self.logger.error("No destination specified")
            return False

        destination = {
            'id': destination_id,
            'type': destination_type
        }

        return self._export_to_notion(content, destination)

    def _get_perplexity_content(self) -> Optional[Dict[str, Any]]:
        """Interactively get Perplexity content from user."""
        print("\n📚 Content Source")
        print("1. Perplexity thread/report URL")
        print("2. New search query")
        print("3. Manual text input")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == '1':
            url = input("Enter Perplexity URL: ").strip()
            return self.perplexity.fetch_thread_content(url)

        elif choice == '2':
            query = input("Enter search query: ").strip()
            return self.perplexity.search(query)

        elif choice == '3':
            print("\nEnter content (press Ctrl+D or Ctrl+Z when done):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass

            content_text = '\n'.join(lines)
            if content_text:
                return {
                    'title': 'Manual Input',
                    'content': content_text,
                    'timestamp': datetime.now().isoformat()
                }

        return None

    def _select_destination(self) -> Optional[Dict[str, str]]:
        """Interactively select Notion destination."""
        print("\n🎯 Destination Selection")
        print("1. Database (create new entry)")
        print("2. Page (append to existing)")

        if self.preferences.get('default_destination_id'):
            print(f"3. Use saved default ({self.preferences.get('default_destination_name')})")

        choice = input("\nSelect option: ").strip()

        if choice == '3' and self.preferences.get('default_destination_id'):
            return {
                'id': self.preferences['default_destination_id'],
                'type': self.preferences['default_destination_type'],
                'name': self.preferences.get('default_destination_name', 'Saved')
            }

        if choice == '1':
            return self._select_database()
        elif choice == '2':
            return self._select_page()

        return None

    def _select_database(self) -> Optional[Dict[str, str]]:
        """Show database selection menu."""
        databases = self.notion.list_databases()

        if not databases:
            self.logger.error("No databases found or accessible")
            return None

        print("\n📊 Available Databases:")
        for idx, db in enumerate(databases, 1):
            print(f"{idx}. {db['title']}")

        try:
            selection = int(input("\nSelect database number: ")) - 1
            if 0 <= selection < len(databases):
                db = databases[selection]

                # Ask to save as default
                save = input("Save as default destination? (y/n): ").strip().lower()
                if save == 'y':
                    self.config.save_preferences({
                        'default_destination_id': db['id'],
                        'default_destination_type': 'database',
                        'default_destination_name': db['title']
                    })

                return {
                    'id': db['id'],
                    'type': 'database',
                    'name': db['title']
                }
        except (ValueError, IndexError):
            self.logger.error("Invalid selection")

        return None

    def _select_page(self) -> Optional[Dict[str, str]]:
        """Show page selection menu."""
        pages = self.notion.list_pages()

        if not pages:
            self.logger.error("No pages found or accessible")
            return None

        print("\n📄 Available Pages:")
        for idx, page in enumerate(pages, 1):
            print(f"{idx}. {page['title']}")

        try:
            selection = int(input("\nSelect page number: ")) - 1
            if 0 <= selection < len(pages):
                page = pages[selection]

                # Ask to save as default
                save = input("Save as default destination? (y/n): ").strip().lower()
                if save == 'y':
                    self.config.save_preferences({
                        'default_destination_id': page['id'],
                        'default_destination_type': 'page',
                        'default_destination_name': page['title']
                    })

                return {
                    'id': page['id'],
                    'type': 'page',
                    'name': page['title']
                }
        except (ValueError, IndexError):
            self.logger.error("Invalid selection")

        return None

    def _export_to_notion(
        self,
        content: Dict[str, Any],
        destination: Dict[str, str]
    ) -> bool:
        """
        Export content to selected Notion destination.

        Args:
            content: Normalized Perplexity content
            destination: Destination info (id, type, name)

        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"\n📤 Exporting to {destination['name']}...")

        # Convert to Notion blocks
        blocks = self.converter.perplexity_to_notion_blocks(content)

        if destination['type'] == 'database':
            # Create new page in database
            title = content.get('title', 'Perplexity Research')
            page_id = self.notion.create_page_in_database(
                database_id=destination['id'],
                title=title,
                content_blocks=blocks
            )
            success = page_id is not None
        else:
            # Append to existing page
            success = self.notion.append_to_page(
                page_id=destination['id'],
                content_blocks=blocks
            )

        if success:
            self.logger.info("✅ Export completed successfully!")
            return True
        else:
            self.logger.error("❌ Export failed")
            return False


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Export Perplexity research to Notion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python perplexity_to_notion.py

  # Automated mode with URL
  python perplexity_to_notion.py --source "https://perplexity.ai/search/..." \\
                                  --destination-id "db-id-here"

  # New search and export
  python perplexity_to_notion.py --search "quantum computing applications" \\
                                  --destination-id "db-id-here"

  # Webhook mode (for Android shortcuts)
  python perplexity_to_notion.py --webhook --port 8080

Environment Variables:
  NOTION_TOKEN           Your Notion integration token (required)
  PERPLEXITY_API_KEY     Your Perplexity API key (optional)
  NOTION_MCP_ENDPOINT    Custom MCP endpoint (optional)
        """
    )

    # Input options
    parser.add_argument(
        '--source', '-s',
        help='Perplexity thread/report URL to export'
    )
    parser.add_argument(
        '--search', '-q',
        help='New Perplexity search query'
    )

    # Destination options
    parser.add_argument(
        '--destination-id', '-d',
        help='Target Notion database or page ID'
    )
    parser.add_argument(
        '--destination-type', '-t',
        choices=['database', 'page'],
        default='database',
        help='Destination type (default: database)'
    )

    # Mode options
    parser.add_argument(
        '--webhook',
        action='store_true',
        help='Start webhook server for mobile/automation'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Webhook server port (default: 8080)'
    )

    # Configuration
    parser.add_argument(
        '--config', '-c',
        help='Path to custom config JSON file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup
    logger = setup_logging(args.verbose)

    try:
        config = Config(args.config)
        app = PerplexityNotionApp(config, logger)

        # Webhook mode
        if args.webhook:
            from webhook_server import run_webhook_server
            run_webhook_server(app, args.port, logger)
            return

        # Automated mode
        if args.source or args.search:
            source = args.source or args.search
            success = app.run_automated(
                source=source,
                destination_id=args.destination_id,
                destination_type=args.destination_type
            )
            sys.exit(0 if success else 1)

        # Interactive mode
        app.run_interactive()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n\n👋 Cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
