#!/usr/bin/env python3
"""Test script to verify CSRF fixes."""

import unittest
from app_factory import create_app
from security_utils import csrf_protection

class TestCSRFProtectionFix(unittest.TestCase):
    """Test that CSRF protection test is fixed."""
    
    def setUp(self):
        """Setup test client with CSRF protection."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Cleanup after tests."""
        self.app_context.pop()
        
    def test_csrf_token_generation_fixed(self):
        """Test CSRF token generation fix."""
        with self.app.test_request_context('/'):
            # Token should be generated on session creation within request context
            csrf_protection._before_request()
            from flask import session
            token = session.get('csrf_token')
            self.assertIsNotNone(token)
            self.assertGreater(len(token), 20)
            print("✅ CSRF token generation test fixed successfully")
    
    def test_csrf_token_validation_fixed(self):
        """Test CSRF token validation fix."""
        with self.app.test_request_context('/'):
            from flask import session
            session['csrf_token'] = 'test_token_123'
            
            # Valid token should pass
            self.assertTrue(csrf_protection.validate_csrf('test_token_123'))
            
            # Invalid token should fail
            self.assertFalse(csrf_protection.validate_csrf('invalid_token'))
            
            # Missing token should fail
            self.assertFalse(csrf_protection.validate_csrf(None))
            print("✅ CSRF token validation test fixed successfully")

if __name__ == '__main__':
    unittest.main()