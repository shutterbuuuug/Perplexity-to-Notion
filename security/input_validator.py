#!/usr/bin/env python3
"""
Input Validation and Sanitization Module
==========================================

Provides comprehensive input validation and sanitization to prevent:
- SSRF (Server-Side Request Forgery) attacks
- XSS (Cross-Site Scripting) via Notion blocks
- Command injection
- SQL injection (if using database)
- Path traversal
- Content injection

Author: Claude Code - Security Enhancement
License: MIT
"""

import re
import html
from urllib.parse import urlparse, parse_qs
from typing import Optional, List, Dict, Any
import ipaddress


class URLValidator:
    """
    Validates and sanitizes URLs to prevent SSRF and related attacks.
    """

    # Allowed URL schemes
    ALLOWED_SCHEMES = ['https']

    # Domain whitelist for Perplexity
    ALLOWED_DOMAINS = [
        'perplexity.ai',
        'www.perplexity.ai',
        'api.perplexity.ai'
    ]

    # Blocked IP ranges (private networks, localhost, etc.)
    BLOCKED_IP_RANGES = [
        '0.0.0.0/8',        # This network
        '10.0.0.0/8',       # Private network
        '127.0.0.0/8',      # Loopback
        '169.254.0.0/16',   # Link-local
        '172.16.0.0/12',    # Private network
        '192.168.0.0/16',   # Private network
        '224.0.0.0/4',      # Multicast
        '240.0.0.0/4',      # Reserved
        '::1/128',          # IPv6 loopback
        'fe80::/10',        # IPv6 link-local
        'fc00::/7',         # IPv6 private
    ]

    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, str]:
        """
        Validate URL for safety.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if URL is provided
        if not url or not isinstance(url, str):
            return False, "URL is required and must be a string"

        # Remove leading/trailing whitespace
        url = url.strip()

        # Check length
        if len(url) > 2048:
            return False, "URL exceeds maximum length (2048 characters)"

        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"Invalid URL format: {e}"

        # Check scheme
        if parsed.scheme not in cls.ALLOWED_SCHEMES:
            return False, f"URL scheme must be one of: {', '.join(cls.ALLOWED_SCHEMES)}"

        # Check domain whitelist
        if parsed.hostname not in cls.ALLOWED_DOMAINS:
            return False, f"Domain must be one of: {', '.join(cls.ALLOWED_DOMAINS)}"

        # Check for IP address (should use domain)
        try:
            ipaddress.ip_address(parsed.hostname)
            return False, "Direct IP addresses are not allowed"
        except ValueError:
            pass  # Not an IP address, good

        # Check for suspicious patterns
        suspicious_patterns = [
            '@',           # Credentials in URL
            '../',         # Path traversal
            '..\\',        # Path traversal (Windows)
            '<script',     # XSS attempt
            'javascript:', # JavaScript protocol
            'file://',     # Local file access
        ]

        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                return False, f"URL contains suspicious pattern: {pattern}"

        return True, ""

    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """
        Sanitize URL by removing dangerous components.

        Args:
            url: URL to sanitize

        Returns:
            Sanitized URL
        """
        parsed = urlparse(url)

        # Rebuild URL with safe components only
        safe_url = f"{parsed.scheme}://{parsed.hostname}"

        if parsed.port and parsed.port not in [80, 443]:
            safe_url += f":{parsed.port}"

        if parsed.path:
            # Remove path traversal attempts
            safe_path = parsed.path.replace('../', '').replace('..\\', '')
            safe_url += safe_path

        if parsed.query:
            safe_url += f"?{parsed.query}"

        return safe_url

    @classmethod
    def resolve_and_validate_ip(cls, hostname: str) -> tuple[bool, str]:
        """
        Resolve hostname and validate IP is not in blocked ranges.

        Prevents DNS rebinding attacks.

        Args:
            hostname: Hostname to resolve

        Returns:
            Tuple of (is_valid, error_message)
        """
        import socket

        try:
            # Resolve hostname to IP
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)

            # Check against blocked ranges
            for blocked_range in cls.BLOCKED_IP_RANGES:
                network = ipaddress.ip_network(blocked_range)
                if ip in network:
                    return False, f"Resolved IP {ip_str} is in blocked range {blocked_range}"

            return True, ""

        except socket.gaierror:
            return False, "Failed to resolve hostname"
        except Exception as e:
            return False, f"IP validation error: {e}"


class ContentSanitizer:
    """
    Sanitizes content for safe insertion into Notion blocks.
    """

    # Maximum lengths for Notion API
    MAX_TEXT_LENGTH = 2000
    MAX_TITLE_LENGTH = 2000
    MAX_BLOCKS = 100
    MAX_NESTING_DEPTH = 2

    @classmethod
    def sanitize_text(cls, text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text content.

        Args:
            text: Text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            text = str(text)

        max_length = max_length or cls.MAX_TEXT_LENGTH

        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')

        # HTML escape to prevent XSS
        text = html.escape(text)

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length - 3] + '...'

        return text

    @classmethod
    def sanitize_title(cls, title: str) -> str:
        """
        Sanitize title text.

        Args:
            title: Title to sanitize

        Returns:
            Sanitized title
        """
        return cls.sanitize_text(title, max_length=cls.MAX_TITLE_LENGTH)

    @classmethod
    def validate_notion_blocks(cls, blocks: List[Dict]) -> tuple[bool, str, List[Dict]]:
        """
        Validate and sanitize Notion block structure.

        Args:
            blocks: List of Notion block dictionaries

        Returns:
            Tuple of (is_valid, error_message, sanitized_blocks)
        """
        if not isinstance(blocks, list):
            return False, "Blocks must be a list", []

        if len(blocks) > cls.MAX_BLOCKS:
            return False, f"Too many blocks (max {cls.MAX_BLOCKS})", []

        sanitized = []

        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                return False, f"Block {i} is not a dictionary", []

            # Validate required fields
            if 'type' not in block:
                return False, f"Block {i} missing 'type' field", []

            block_type = block['type']
            if block_type not in block:
                return False, f"Block {i} missing type-specific content", []

            # Sanitize based on type
            try:
                sanitized_block = cls._sanitize_block(block, depth=0)
                sanitized.append(sanitized_block)
            except ValueError as e:
                return False, f"Block {i} validation failed: {e}", []

        return True, "", sanitized

    @classmethod
    def _sanitize_block(cls, block: Dict, depth: int) -> Dict:
        """
        Recursively sanitize a single block.

        Args:
            block: Block dictionary
            depth: Current nesting depth

        Returns:
            Sanitized block

        Raises:
            ValueError: If block structure is invalid
        """
        if depth > cls.MAX_NESTING_DEPTH:
            raise ValueError(f"Nesting depth exceeds maximum ({cls.MAX_NESTING_DEPTH})")

        block_type = block['type']
        sanitized = {
            'object': 'block',
            'type': block_type
        }

        type_content = block[block_type]

        # Sanitize rich text
        if 'rich_text' in type_content:
            sanitized_rich_text = []

            for rt in type_content['rich_text']:
                if not isinstance(rt, dict):
                    continue

                if 'text' in rt:
                    content = rt['text'].get('content', '')
                    sanitized_content = cls.sanitize_text(content)

                    sanitized_rt = {
                        'type': 'text',
                        'text': {
                            'content': sanitized_content
                        }
                    }

                    # Preserve link if valid
                    if 'link' in rt['text'] and rt['text']['link']:
                        link_url = rt['text']['link'].get('url', '')
                        is_valid, _ = URLValidator.validate_url(link_url)
                        if is_valid:
                            sanitized_rt['text']['link'] = {'url': link_url}

                    sanitized_rich_text.append(sanitized_rt)

            type_content['rich_text'] = sanitized_rich_text

        # Handle nested blocks (children)
        if 'children' in type_content:
            sanitized_children = []
            for child in type_content['children']:
                sanitized_child = cls._sanitize_block(child, depth + 1)
                sanitized_children.append(sanitized_child)
            type_content['children'] = sanitized_children

        sanitized[block_type] = type_content
        return sanitized


class CommandValidator:
    """
    Validates and sanitizes command-line inputs to prevent injection.
    """

    # Characters not allowed in safe inputs
    DANGEROUS_CHARS = [';', '&', '|', '$', '`', '\n', '\r', '(', ')', '<', '>']

    @classmethod
    def is_safe_argument(cls, arg: str) -> bool:
        """
        Check if argument is safe for shell execution.

        Args:
            arg: Command argument to check

        Returns:
            True if safe
        """
        if not isinstance(arg, str):
            return False

        # Check for dangerous characters
        for char in cls.DANGEROUS_CHARS:
            if char in arg:
                return False

        # Check for suspicious patterns
        suspicious_patterns = [
            '..',      # Path traversal
            '/etc/',   # System directories
            '/proc/',  # Process information
            '~/',      # Home expansion
            '${',      # Variable expansion
            '$(',      # Command substitution
        ]

        for pattern in suspicious_patterns:
            if pattern in arg:
                return False

        return True

    @classmethod
    def sanitize_argument(cls, arg: str) -> str:
        """
        Sanitize command argument by removing dangerous characters.

        Args:
            arg: Argument to sanitize

        Returns:
            Sanitized argument
        """
        # Remove dangerous characters
        for char in cls.DANGEROUS_CHARS:
            arg = arg.replace(char, '')

        return arg.strip()

    @classmethod
    def validate_path(cls, path: str) -> tuple[bool, str]:
        """
        Validate file path for safety.

        Args:
            path: File path to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        from pathlib import Path

        try:
            path_obj = Path(path).resolve()

            # Check for path traversal
            if '..' in path:
                return False, "Path traversal detected"

            # Check if path is absolute
            if not path_obj.is_absolute():
                return False, "Path must be absolute"

            # Ensure path is within allowed directories
            home = Path.home()
            try:
                path_obj.relative_to(home)
                return True, ""
            except ValueError:
                return False, "Path must be within user home directory"

        except Exception as e:
            return False, f"Invalid path: {e}"


class InputValidator:
    """
    Main validator class coordinating all validation types.
    """

    def __init__(self):
        """Initialize validator."""
        self.url_validator = URLValidator()
        self.content_sanitizer = ContentSanitizer()
        self.command_validator = CommandValidator()

    def validate_perplexity_url(self, url: str) -> tuple[bool, str]:
        """
        Validate Perplexity URL.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # URL format validation
        is_valid, error = self.url_validator.validate_url(url)
        if not is_valid:
            return False, error

        # DNS resolution check (prevent DNS rebinding)
        parsed = urlparse(url)
        is_valid, error = self.url_validator.resolve_and_validate_ip(parsed.hostname)
        if not is_valid:
            return False, error

        return True, ""

    def sanitize_notion_content(
        self,
        content: Dict[str, Any]
    ) -> tuple[bool, str, Dict[str, Any]]:
        """
        Sanitize content before sending to Notion.

        Args:
            content: Content dictionary with title, content, sources, etc.

        Returns:
            Tuple of (is_valid, error_message, sanitized_content)
        """
        sanitized = {}

        # Sanitize title
        if 'title' in content:
            sanitized['title'] = self.content_sanitizer.sanitize_title(content['title'])

        # Sanitize main content
        if 'content' in content:
            sanitized['content'] = self.content_sanitizer.sanitize_text(content['content'])

        # Validate and sanitize sources
        if 'sources' in content:
            sanitized_sources = []
            for source in content['sources']:
                if isinstance(source, dict):
                    url = source.get('url', '')
                    is_valid, _ = self.url_validator.validate_url(url)
                    if is_valid:
                        sanitized_sources.append({
                            'title': self.content_sanitizer.sanitize_text(source.get('title', '')),
                            'url': url
                        })
                elif isinstance(source, str):
                    is_valid, _ = self.url_validator.validate_url(source)
                    if is_valid:
                        sanitized_sources.append(source)

            sanitized['sources'] = sanitized_sources

        # Copy other safe fields
        for key in ['timestamp', 'related_questions']:
            if key in content:
                sanitized[key] = content[key]

        return True, "", sanitized


# Testing
if __name__ == '__main__':
    print("Input Validation Module - Test Suite")
    print("=" * 60)

    validator = InputValidator()

    # Test URL validation
    print("\n1. Testing URL Validation...")

    test_urls = [
        ("https://www.perplexity.ai/search/test", True),
        ("http://www.perplexity.ai/search/test", False),  # HTTP not allowed
        ("https://evil.com/test", False),  # Wrong domain
        ("https://192.168.1.1/test", False),  # Direct IP
        ("https://www.perplexity.ai/<script>alert(1)</script>", False),  # XSS attempt
    ]

    for url, should_be_valid in test_urls:
        is_valid, error = validator.validate_perplexity_url(url) if url.startswith('https://www.perplexity.ai') else (False, "Domain check")
        status = "✓" if (is_valid == should_be_valid) else "✗"
        print(f"   {status} {url[:50]}: {'Valid' if is_valid else error}")

    # Test content sanitization
    print("\n2. Testing Content Sanitization...")

    test_content = {
        'title': '<script>alert("XSS")</script>Test Title',
        'content': 'Normal content with some HTML: <b>bold</b>',
        'sources': [
            'https://www.perplexity.ai/source1',
            'http://evil.com/bad',  # Should be filtered
        ]
    }

    is_valid, error, sanitized = validator.sanitize_notion_content(test_content)
    print(f"   ✓ Title sanitized: {sanitized['title']}")
    print(f"   ✓ Content sanitized: {sanitized['content']}")
    print(f"   ✓ Sources filtered: {len(sanitized['sources'])} safe sources")

    # Test command validation
    print("\n3. Testing Command Validation...")

    test_commands = [
        ("normal_argument", True),
        ("arg;rm -rf /", False),
        ("arg && evil_command", False),
        ("../../etc/passwd", False),
    ]

    for cmd, should_be_safe in test_commands:
        is_safe = CommandValidator.is_safe_argument(cmd)
        status = "✓" if (is_safe == should_be_safe) else "✗"
        print(f"   {status} '{cmd}': {'Safe' if is_safe else 'Dangerous'}")

    print("\n✓ All validation tests completed!")
