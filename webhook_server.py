#!/usr/bin/env python3
"""
Webhook Server for Perplexity to Notion Automation
==================================================

A lightweight webhook server for receiving Perplexity exports from
mobile devices, automation tools, and third-party integrations.

Designed for Android shortcuts (Tasker, Automate, HTTP Shortcuts)
and desktop automation workflows.

Features:
- Simple HTTP POST endpoint for content submission
- Authentication via API key
- Push notification support
- Request logging and monitoring
- Mobile-optimized responses

Author: Claude Code
License: MIT
"""

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from typing import Any, Dict, Optional
import traceback


class WebhookHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for webhook endpoints.

    Accepts POST requests with Perplexity content and processes
    them through the main application.
    """

    # Set by run_webhook_server()
    app = None
    api_key = None
    logger = None

    def _set_headers(self, status_code: int = 200, content_type: str = 'application/json'):
        """Set HTTP response headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def _authenticate(self) -> bool:
        """Verify API key authentication."""
        if not self.api_key:
            return True  # No auth required if not configured

        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            return token == self.api_key

        return False

    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response."""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self._set_headers(204)

    def do_GET(self):
        """
        Handle GET requests.

        Provides API status and basic documentation.
        """
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/':
            # Status endpoint
            response = {
                'status': 'online',
                'service': 'Perplexity to Notion Webhook',
                'endpoints': {
                    '/export': 'POST - Export content to Notion',
                    '/health': 'GET - Health check',
                    '/': 'GET - This information'
                }
            }
            self._send_json_response(response)

        elif parsed_path.path == '/health':
            # Health check
            self._send_json_response({'status': 'healthy', 'ready': True})

        else:
            self._send_json_response(
                {'error': 'Not found', 'path': self.path},
                404
            )

    def do_POST(self):
        """
        Handle POST requests for content export.

        Expected JSON payload:
        {
            "source": "perplexity-url-or-query",
            "destination_id": "optional-notion-id",
            "destination_type": "database|page",
            "content": {
                "title": "optional-title",
                "content": "optional-manual-content",
                "sources": []
            }
        }
        """
        try:
            # Authentication
            if not self._authenticate():
                self._send_json_response(
                    {'error': 'Unauthorized', 'message': 'Invalid API key'},
                    401
                )
                return

            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')

            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                self._send_json_response(
                    {'error': 'Invalid JSON', 'message': 'Request body must be valid JSON'},
                    400
                )
                return

            # Validate required fields
            if 'source' not in payload and 'content' not in payload:
                self._send_json_response(
                    {
                        'error': 'Missing required field',
                        'message': 'Either "source" or "content" must be provided'
                    },
                    400
                )
                return

            # Process export
            self.logger.info(f"📥 Webhook request received from {self.client_address[0]}")

            if payload.get('content'):
                # Manual content provided
                perplexity_content = payload['content']
            else:
                # Fetch from source
                source = payload['source']
                if source.startswith('http'):
                    perplexity_content = self.app.perplexity.fetch_thread_content(source)
                else:
                    perplexity_content = self.app.perplexity.search(source)

            if not perplexity_content:
                self._send_json_response(
                    {'error': 'Content fetch failed', 'message': 'Could not retrieve content'},
                    500
                )
                return

            # Determine destination
            destination_id = payload.get('destination_id')
            destination_type = payload.get('destination_type', 'database')

            if not destination_id:
                # Use saved default
                destination_id = self.app.preferences.get('default_destination_id')
                destination_type = self.app.preferences.get('default_destination_type', 'database')

            if not destination_id:
                self._send_json_response(
                    {
                        'error': 'No destination',
                        'message': 'No destination specified and no default saved'
                    },
                    400
                )
                return

            destination = {
                'id': destination_id,
                'type': destination_type,
                'name': 'Webhook Destination'
            }

            # Export to Notion
            success = self.app._export_to_notion(perplexity_content, destination)

            if success:
                self._send_json_response({
                    'status': 'success',
                    'message': 'Content exported to Notion successfully',
                    'title': perplexity_content.get('title', 'Untitled')
                })
            else:
                self._send_json_response(
                    {
                        'error': 'Export failed',
                        'message': 'Failed to export content to Notion'
                    },
                    500
                )

        except Exception as e:
            self.logger.error(f"Webhook error: {e}")
            self.logger.debug(traceback.format_exc())

            self._send_json_response(
                {
                    'error': 'Internal server error',
                    'message': str(e)
                },
                500
            )

    def log_message(self, format, *args):
        """Override to use custom logger."""
        if self.logger:
            self.logger.info(f"{self.client_address[0]} - {format % args}")


def run_webhook_server(app, port: int, logger: logging.Logger, api_key: Optional[str] = None):
    """
    Start the webhook server.

    Args:
        app: PerplexityNotionApp instance
        port: Port to listen on
        logger: Logger instance
        api_key: Optional API key for authentication
    """
    # Configure handler with app instance
    WebhookHandler.app = app
    WebhookHandler.logger = logger
    WebhookHandler.api_key = api_key or app.config.config_dir / 'webhook_key.txt'

    # Create server
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)

    logger.info("=" * 60)
    logger.info("🌐 Webhook Server Started")
    logger.info("=" * 60)
    logger.info(f"Listening on: http://0.0.0.0:{port}")
    logger.info(f"Local access: http://localhost:{port}")
    logger.info("\nEndpoints:")
    logger.info(f"  POST http://localhost:{port}/export  - Export content")
    logger.info(f"  GET  http://localhost:{port}/health  - Health check")
    logger.info(f"  GET  http://localhost:{port}/        - API info")
    logger.info("\nPress Ctrl+C to stop")
    logger.info("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n\n👋 Shutting down webhook server...")
        httpd.shutdown()


def send_push_notification(title: str, message: str, service: str = 'ntfy'):
    """
    Send push notification to mobile device.

    Supports multiple notification services:
    - ntfy.sh (open source, no account required)
    - Pushover
    - Telegram
    - Custom webhook

    Args:
        title: Notification title
        message: Notification message
        service: Notification service to use
    """
    # This is a placeholder for push notification integration
    # Implement based on your preferred service

    if service == 'ntfy':
        # Example: ntfy.sh integration
        # Replace 'your-topic' with your configured topic
        try:
            import requests
            requests.post(
                'https://ntfy.sh/your-topic',
                data=message.encode('utf-8'),
                headers={'Title': title}
            )
        except:
            pass

    # Add other notification services as needed


if __name__ == '__main__':
    # Standalone webhook server mode
    print("Use: python perplexity_to_notion.py --webhook")
