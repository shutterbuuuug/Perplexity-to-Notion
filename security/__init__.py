"""
Security Module for Perplexity to Notion
=========================================

Comprehensive security components for protecting the automation system.

Components:
- auth_manager: JWT authentication, OAuth, device registration, rate limiting
- secure_storage_android: Encrypted credential storage for mobile devices
- input_validator: Input validation and sanitization
- generate_https_cert: SSL certificate generation utility

Usage:
    from security.auth_manager import JWTAuthManager, RateLimiter
    from security.secure_storage_android import SecureCredentialManager
    from security.input_validator import InputValidator

Author: Claude Code - Security Enhancement
License: MIT
"""

__version__ = '1.0.0'
__all__ = [
    'JWTAuthManager',
    'NotionOAuthManager',
    'RateLimiter',
    'DeviceIdentity',
    'SecureCredentialManager',
    'AndroidSecureStorage',
    'KnoxSecureStorage',
    'InputValidator',
    'URLValidator',
    'ContentSanitizer',
    'CommandValidator',
]
