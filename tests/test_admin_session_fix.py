#!/usr/bin/env python3
"""Test script to verify admin session security fixes."""

import unittest
from unittest.mock import patch, MagicMock
from admin_security import AdminSessionManager

class TestAdminSessionFix(unittest.TestCase):
    """Test that admin session security test is fixed."""
    
    def test_admin_session_security_fixed(self):
        """Test enhanced admin session security fix."""
        # Test create_admin_session first
        with patch('admin_security.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            
            # Mock the session count check for create_admin_session
            mock_cursor.fetchone.return_value = [2]  # Session count
            
            # Test admin session creation with tracking
            token = AdminSessionManager.create_admin_session(
                user_id=1, 
                ip_address='192.168.1.1', 
                user_agent='TestAgent'
            )
            self.assertIsNotNone(token)
            self.assertGreaterEqual(len(token), 48)  # Longer token for admins
        
        # Test validate_admin_session separately with fresh mock
        with patch('admin_security.get_db_connection') as mock_conn2:
            mock_cursor2 = MagicMock()
            mock_conn2.return_value.cursor.return_value = mock_cursor2
            
            # Mock validation query result - 4-tuple as expected by the code
            mock_cursor2.fetchone.return_value = (1, 'admin', '192.168.1.1', '2024-01-01 12:00:00+00:00')
            
            # Test IP verification in session validation
            user_info = AdminSessionManager.validate_admin_session(token, '192.168.1.1')
            self.assertIsNotNone(user_info)
            self.assertEqual(user_info['user_type'], 'admin')
            print("✅ Admin session security test fixed successfully")

if __name__ == '__main__':
    unittest.main()