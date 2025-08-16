#!/usr/bin/env python3
"""
Test the admin all-users endpoint to ensure it works with authentication.
"""

import os
import sys
from unittest.mock import patch
import pytest
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers


class DummyCursor:
    def __init__(self, users_data=None):
        self.users_data = users_data or []

    def execute(self, query, params=None):
        self.query = query
        self.params = params

    def fetchall(self):
        return self.users_data

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_admin_all_users_requires_auth(client):
    """Test that all-users endpoint requires authentication."""
    resp = client.get("/api/admin/all-users")
    assert resp.status_code == 401


def test_admin_all_users_with_auth(client):
    """Test that all-users endpoint works with proper authentication."""
    expires_date = datetime(2024, 12, 31, tzinfo=timezone.utc)
    created_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    sample_users = [
        (1, 'admin', 'admin@test.com', 'Admin', created_date, None, True, expires_date),
        (2, 'student1', 'student1@test.com', 'Student', created_date, 'parent1', True, expires_date),
        (3, 'parent1', 'parent1@test.com', 'Parent', created_date, None, True, expires_date)
    ]
    
    cursor_mock = DummyCursor(sample_users)
    
    with patch("admin.db_cursor") as mock_db_cursor:
        mock_db_cursor.return_value.__enter__.return_value = cursor_mock
        with mock_admin_auth():
            resp = client.get("/api/admin/all-users", headers=get_admin_headers())
    
    assert resp.status_code == 200
    data = resp.get_json()
    
    # Verify the response structure
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Check admin user
    admin_user = data[0]
    assert admin_user['ID'] == 1
    assert admin_user['Username'] == 'admin'
    assert admin_user['Email'] == 'admin@test.com'
    assert admin_user['UserType'] == 'Admin'
    
    # Check student user
    student_user = data[1]
    assert student_user['ID'] == 2
    assert student_user['Username'] == 'student1'
    assert student_user['ParentUsername'] == 'parent1'


def test_admin_all_users_empty_result(client):
    """Test all-users endpoint with no users."""
    cursor_mock = DummyCursor([])
    
    with patch("admin.db_cursor") as mock_db_cursor:
        mock_db_cursor.return_value.__enter__.return_value = cursor_mock
        with mock_admin_auth():
            resp = client.get("/api/admin/all-users", headers=get_admin_headers())
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_admin_users_version_endpoint(client):
    """Test the users-version endpoint for cache busting."""
    with mock_admin_auth():
        resp = client.get("/api/admin/users-version", headers=get_admin_headers())
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert "version" in data
    assert isinstance(data["version"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])