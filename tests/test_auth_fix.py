#!/usr/bin/env python3
"""Test to verify authentication fixes with proper pytest structure."""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def auth_test_env():
    """Set up and clean up test environment variables."""
    original_testing = os.environ.get('TESTING')
    original_mock_auth = os.environ.get('MOCK_AUTH')
    
    # Set test environment
    os.environ['TESTING'] = 'True'
    os.environ['MOCK_AUTH'] = 'true'
    
    yield
    
    # Clean up environment variables
    if original_testing is not None:
        os.environ['TESTING'] = original_testing
    else:
        os.environ.pop('TESTING', None)
    
    if original_mock_auth is not None:
        os.environ['MOCK_AUTH'] = original_mock_auth
    else:
        os.environ.pop('MOCK_AUTH', None)


def test_auth_utils_import_works(auth_test_env):
    """Test that auth_utils can be imported successfully."""
    from auth_utils import require_auth
    assert require_auth is not None


def test_auth_decorator_creation(auth_test_env):
    """Test that auth decorator can be created for admin endpoints."""
    from auth_utils import require_auth
    from app import app
    
    @require_auth(['admin'])
    def admin_endpoint():
        return "User: test-admin"
    
    # Test the decorated function within app context
    with app.app_context():
        with app.test_request_context():
            result = admin_endpoint()
            assert result == "User: test-admin"


def test_mock_auth_environment_variable(auth_test_env):
    """Test that MOCK_AUTH environment variable is set correctly."""
    assert os.environ.get('MOCK_AUTH') == 'true'
    assert os.environ.get('TESTING') == 'True'
