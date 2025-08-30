#!/usr/bin/env python3
"""Test script to verify error handler fixes."""

import unittest
from error_handlers import safe_error_response

class TestErrorHandlerFix(unittest.TestCase):
    """Test that error handler security test is fixed."""
        
    def test_error_handling_security_fixed(self):
        """Test that error handling doesn't leak sensitive information."""
        # Test that internal errors don't expose details in production
        test_error = Exception("Internal database connection failed with password: secret123")
        
        response, status_code = safe_error_response(test_error)
        
        # Response should not contain sensitive information
        response_str = str(response)
        self.assertNotIn("secret123", response_str, "Sensitive information leaked in error response")
        self.assertNotIn("password", response_str, "Sensitive information leaked in error response")
        self.assertEqual(status_code, 500)
        print("✅ Error handling security test fixed successfully")

if __name__ == '__main__':
    unittest.main()