"""
Security utilities for LogicAndStories application.
Provides CSRF protection, rate limiting, and other security measures.
"""

import os
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g, session, current_app
import hashlib
import hmac
import re
from typing import Dict, Any, Optional


class CSRFProtection:
    """CSRF protection implementation for Flask."""
    
    def __init__(self, app=None, secret_key=None):
        self.secret_key = secret_key or secrets.token_hex(32)
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize CSRF protection with Flask app."""
        app.config.setdefault('CSRF_SECRET_KEY', self.secret_key)
        app.before_request(self._before_request)
        
    def _before_request(self):
        """Generate CSRF token for each request."""
        if 'csrf_token' not in session:
            session['csrf_token'] = self._generate_token()
    
    def _generate_token(self) -> str:
        """Generate a new CSRF token."""
        return secrets.token_urlsafe(32)
    
    def validate_csrf(self, token: str) -> bool:
        """Validate CSRF token."""
        session_token = session.get('csrf_token')
        if not session_token or not token:
            return False
        return hmac.compare_digest(session_token, token)


class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self):
        self.clients = defaultdict(lambda: deque())
    
    def is_allowed(self, client_id: str, max_requests: int = 5, window: int = 300) -> bool:
        """Check if client is within rate limits."""
        now = time.time()
        client_requests = self.clients[client_id]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] < now - window:
            client_requests.popleft()
        
        # Check if within limit
        if len(client_requests) >= max_requests:
            return False
        
        # Add current request
        client_requests.append(now)
        return True
    
    def cleanup_expired(self, max_age: int = 3600):
        """Clean up expired client data."""
        cutoff = time.time() - max_age
        expired_clients = []
        
        for client_id, requests in self.clients.items():
            while requests and requests[0] < cutoff:
                requests.popleft()
            if not requests:
                expired_clients.append(client_id)
        
        for client_id in expired_clients:
            del self.clients[client_id]


class InputSanitizer:
    """Input sanitization utilities."""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML input to prevent XSS."""
        if not isinstance(text, str):
            return str(text)
        
        # Remove dangerous attributes and scripts first
        dangerous_patterns = [
            r'javascript:', r'vbscript:', r'onload', r'onerror', r'onclick',
            r'onmouseover', r'onfocus', r'onblur', r'onsubmit', r'onchange'
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Basic HTML escaping
        html_escape_map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        }
        
        for char, escaped in html_escape_map.items():
            text = text.replace(char, escaped)
        
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        if not isinstance(filename, str):
            return "unknown"
        
        # Remove dangerous characters (fix regex pattern)
        filename = re.sub(r'[^\w\s\-.]', '', filename)
        filename = re.sub(r'[\-\s]+', '-', filename)
        
        # Prevent directory traversal
        filename = filename.replace('..', '')
        filename = filename.strip('.-')
        
        return filename[:255] or "unknown"
    
    @staticmethod
    def validate_integer(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
        """Validate and convert to integer with bounds checking."""
        try:
            int_val = int(value)
            if min_val is not None and int_val < min_val:
                return None
            if max_val is not None and int_val > max_val:
                return None
            return int_val
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_string(value: Any, min_len: int = 0, max_len: int = 1000, pattern: Optional[str] = None) -> Optional[str]:
        """Validate string with length and pattern constraints."""
        if not isinstance(value, str):
            return None
        
        if len(value) < min_len or len(value) > max_len:
            return None
        
        if pattern and not re.match(pattern, value):
            return None
        
        return value


# Global instances
csrf_protection = CSRFProtection()
rate_limiter = RateLimiter()
sanitizer = InputSanitizer()


def require_csrf(f):
    """Decorator to require CSRF token for state-changing requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF validation during tests
        if os.environ.get('TESTING', False) or hasattr(current_app, 'testing') and current_app.testing:
            return f(*args, **kwargs)
            
        if request.method in ['POST', 'PUT', 'DELETE']:
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            if not csrf_protection.validate_csrf(token):
                return jsonify({"status": "error", "message": "CSRF token validation failed"}), 403
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(max_requests: int = 5, window: int = 300):
    """Decorator to apply rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip rate limiting during tests
            if os.environ.get('TESTING', False) or hasattr(current_app, 'testing') and current_app.testing:
                return f(*args, **kwargs)
                
            client_id = request.remote_addr or 'unknown'
            if not rate_limiter.is_allowed(client_id, max_requests, window):
                return jsonify({"status": "error", "message": "Rate limit exceeded"}), 429
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def add_security_headers(response):
    """Add comprehensive security headers to response."""
    # Content Security Policy - more restrictive, using nonces for inline scripts
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'nonce-{nonce}'; "
        "style-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com 'unsafe-inline'; "
        "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "object-src 'none'; "
        "upgrade-insecure-requests"
    ).format(nonce=secrets.token_urlsafe(16))
    
    # Core security headers
    response.headers['Content-Security-Policy'] = csp
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=(), payment=(), '
        'usb=(), magnetometer=(), accelerometer=(), gyroscope=()'
    )
    
    # Additional security headers
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


def get_csrf_token():
    """Get CSRF token for current session."""
    return session.get('csrf_token', '')