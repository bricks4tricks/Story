"""
Pytest configuration and fixtures for LogicAndStories tests.
Ensures consistent test environment setup across all test files.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Set environment variables for testing before any imports
os.environ['PYTEST_CURRENT_TEST'] = '1'
os.environ['FLASK_ENV'] = 'testing'
os.environ['TESTING'] = 'True'

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Set up test environment automatically for all tests."""
    # Mock database connections to avoid connecting to Render database
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


@pytest.fixture
def app_context():
    """Create an application context for tests that need it."""
    from app import app
    with app.app_context():
        yield app