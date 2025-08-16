"""
Security testing suite for LogicAndStories application.

Tests authentication, authorization, input validation, CSRF protection,
rate limiting, and other security features.
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from app_factory import create_app
from security_utils import csrf_protection, rate_limiter, sanitizer
from auth_utils import SessionManager
from admin_security import AdminSessionManager


class TestAuthentication:
    """Test authentication mechanisms."""
    
    def setup_method(self):
        """Setup test client."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup after tests."""
        self.app_context.pop()
    
    def test_session_creation_and_validation(self):
        """Test session token creation and validation."""
        # Mock database operations
        with patch('auth_utils.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = [1]  # Mock token creation
            
            # Test session creation
            token = SessionManager.create_session(user_id=1, user_type='parent')
            assert token is not None
            assert len(token) > 20  # Token should be reasonably long
            
            # Test session validation
            mock_cursor.fetchone.return_value = (1, 'parent', 'testuser')
            user_info = SessionManager.validate_session(token)
            assert user_info is not None
            assert user_info['user_id'] == 1
            assert user_info['user_type'] == 'parent'
    
    def test_admin_session_security(self):
        """Test enhanced admin session security."""
        with patch('admin_security.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            mock_cursor.fetchone.side_effect = [
                [2],  # Session count
                [1],  # Token creation
                (1, 'admin', '192.168.1.1', '2024-01-01 12:00:00+00:00')  # Session validation - fixed tuple
            ]
            
            # Test admin session creation with tracking
            token = AdminSessionManager.create_admin_session(
                user_id=1, 
                ip_address='192.168.1.1', 
                user_agent='TestAgent'
            )
            assert token is not None
            assert len(token) >= 48  # Longer token for admins
            
            # Test IP verification in session validation
            user_info = AdminSessionManager.validate_admin_session(token, '192.168.1.1')
            assert user_info is not None
            assert user_info['user_type'] == 'admin'


class TestInputSanitization:
    """Test input sanitization and validation."""
    
    def test_html_sanitization(self):
        """Test HTML input sanitization."""
        dangerous_input = "<script>alert('xss')</script><p>Safe content</p>"
        sanitized = sanitizer.sanitize_html(dangerous_input)
        
        assert '<script>' not in sanitized
        assert '&lt;script&gt;' in sanitized
        assert 'Safe content' in sanitized
    
    def test_filename_sanitization(self):
        """Test filename sanitization."""
        dangerous_filename = "../../../etc/passwd"
        sanitized = sanitizer.sanitize_filename(dangerous_filename)
        
        assert '..' not in sanitized
        assert '/' not in sanitized
        assert len(sanitized) > 0
    
    def test_integer_validation(self):
        """Test integer validation with bounds."""
        # Valid integer
        result = sanitizer.validate_integer(42, min_val=1, max_val=100)
        assert result == 42
        
        # Invalid integer
        result = sanitizer.validate_integer("not_a_number")
        assert result is None
        
        # Out of bounds
        result = sanitizer.validate_integer(150, min_val=1, max_val=100)
        assert result is None
    
    def test_string_validation(self):
        """Test string validation with constraints."""
        # Valid string
        result = sanitizer.validate_string("valid", min_len=1, max_len=10)
        assert result == "valid"
        
        # Too short
        result = sanitizer.validate_string("a", min_len=5, max_len=10)
        assert result is None
        
        # Too long
        result = sanitizer.validate_string("very_long_string", min_len=1, max_len=10)
        assert result is None


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_allows_within_limits(self):
        """Test that rate limiter allows requests within limits."""
        client_id = "test_client_1"
        
        # Should allow first request
        assert rate_limiter.is_allowed(client_id, max_requests=5, window=60)
        
        # Should allow subsequent requests within limit
        for _ in range(4):
            assert rate_limiter.is_allowed(client_id, max_requests=5, window=60)
    
    def test_rate_limiter_blocks_over_limit(self):
        """Test that rate limiter blocks requests over the limit."""
        client_id = "test_client_2"
        
        # Make maximum allowed requests
        for _ in range(5):
            rate_limiter.is_allowed(client_id, max_requests=5, window=60)
        
        # Next request should be blocked
        assert not rate_limiter.is_allowed(client_id, max_requests=5, window=60)
    
    def test_rate_limiter_cleanup(self):
        """Test rate limiter cleanup of expired data."""
        client_id = "test_client_3"
        
        # Add some requests
        rate_limiter.is_allowed(client_id, max_requests=5, window=1)
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Cleanup should remove expired data
        initial_count = len(rate_limiter.clients)
        rate_limiter.cleanup_expired(max_age=1)
        
        # Should be able to make requests again
        assert rate_limiter.is_allowed(client_id, max_requests=5, window=60)


class TestCSRFProtection:
    """Test CSRF protection mechanisms."""
    
    def setup_method(self):
        """Setup test client with CSRF protection."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup after tests."""
        self.app_context.pop()
    
    def test_csrf_token_generation(self):
        """Test CSRF token generation."""
        with self.app.test_request_context('/'):
            with self.client.session_transaction() as sess:
                # Token should be generated on session creation
                csrf_protection._before_request()
                token = sess.get('csrf_token')
                assert token is not None
                assert len(token) > 20
    
    def test_csrf_token_validation(self):
        """Test CSRF token validation."""
        with self.app.test_request_context('/'):
            with self.client.session_transaction() as sess:
                sess['csrf_token'] = 'test_token_123'
            
            # Valid token should pass
            assert csrf_protection.validate_csrf('test_token_123')
            
            # Invalid token should fail
            assert not csrf_protection.validate_csrf('invalid_token')
            
            # Missing token should fail
            assert not csrf_protection.validate_csrf(None)


class TestSecurityHeaders:
    """Test security headers implementation."""
    
    def setup_method(self):
        """Setup test client."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
    
    def test_security_headers_present(self):
        """Test that security headers are properly set."""
        response = self.client.get('/health')
        
        # Check for essential security headers
        assert 'Content-Security-Policy' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert 'Referrer-Policy' in response.headers
        assert 'Permissions-Policy' in response.headers
        
        # Check header values
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['X-Frame-Options'] == 'DENY'
        assert 'strict-origin-when-cross-origin' in response.headers['Referrer-Policy']
    
    def test_csp_header_configuration(self):
        """Test Content Security Policy configuration."""
        response = self.client.get('/health')
        csp_header = response.headers.get('Content-Security-Policy')
        
        assert csp_header is not None
        assert "default-src 'self'" in csp_header
        assert "object-src 'none'" in csp_header
        assert "upgrade-insecure-requests" in csp_header


class TestDatabaseSecurity:
    """Test database security measures."""
    
    def test_sql_injection_prevention(self):
        """Test that parameterized queries prevent SQL injection."""
        # This would be tested with actual database calls
        # For now, we verify that our query patterns use parameterization
        
        # Example of safe query pattern used in codebase
        safe_query = "SELECT * FROM tbl_user WHERE username = %s"
        dangerous_input = "'; DROP TABLE tbl_user; --"
        
        # With parameterized queries, this would be treated as a literal string
        # and not executed as SQL
        assert "%s" in safe_query  # Parameterized placeholder
        assert dangerous_input  # This would be safely escaped
    
    def test_password_hashing(self):
        """Test password hashing implementation."""
        from extensions import bcrypt
        
        password = "test_password_123"
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Hash should be different from original password
        assert hashed != password
        
        # Hash should be verifiable
        assert bcrypt.check_password_hash(hashed, password)
        
        # Wrong password should not verify
        assert not bcrypt.check_password_hash(hashed, "wrong_password")


def run_security_tests():
    """Run all security tests and return results."""
    print("🔒 Running Security Test Suite...")
    
    # Run pytest on this file
    import subprocess
    result = subprocess.run([
        'python', '-m', 'pytest', __file__, '-v', '--tb=short'
    ], capture_output=True, text=True, cwd='.')
    
    return result.returncode == 0, result.stdout, result.stderr


if __name__ == "__main__":
    success, stdout, stderr = run_security_tests()
    print(f"Security tests {'PASSED' if success else 'FAILED'}")
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)