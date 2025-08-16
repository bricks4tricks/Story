"""
Test authentication utilities for LogicAndStories tests.
Provides mock authentication for testing admin endpoints.
"""

from unittest.mock import patch
from datetime import datetime, timezone, timedelta


class MockSessionManager:
    """Mock session manager for testing."""
    
    @staticmethod
    def create_mock_admin_session():
        """Create a mock admin session for testing."""
        return {
            'user_id': 1,
            'user_type': 'admin',
            'username': 'test_admin'
        }
    
    @staticmethod
    def create_mock_student_session():
        """Create a mock student session for testing."""
        return {
            'user_id': 0,  # Use user_id 0 to match test data
            'user_type': 'student',
            'username': 'test_student'
        }


def get_admin_headers():
    """Get headers with admin authentication token."""
    return {
        'Authorization': 'Bearer mock_admin_token',
        'Content-Type': 'application/json'
    }


def get_student_headers():
    """Get headers with student authentication token."""
    return {
        'Authorization': 'Bearer mock_student_token',
        'Content-Type': 'application/json'
    }


def mock_admin_auth():
    """Context manager to mock admin authentication."""
    def mock_validate_session(token):
        if token == 'mock_admin_token':
            return MockSessionManager.create_mock_admin_session()
        elif token == 'mock_student_token':
            return MockSessionManager.create_mock_student_session()
        return None
    
    return patch('auth_utils.SessionManager.validate_session', side_effect=mock_validate_session)


def mock_student_auth():
    """Context manager to mock student authentication."""
    def mock_validate_session(token):
        if token == 'mock_student_token':
            return MockSessionManager.create_mock_student_session()
        return None
    
    return patch('auth_utils.SessionManager.validate_session', side_effect=mock_validate_session)