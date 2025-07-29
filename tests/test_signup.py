import os
import sys
import pytest
from unittest.mock import patch

# Ensure the app module can be imported when tests are run from the tests
# directory by adding the project root to the Python path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self):
        self.executed = []
    def execute(self, query, params=None):
        self.executed.append((query, params))
    def fetchone(self):
        # Simulate no existing user for SELECT queries
        return None
    def close(self):
        pass

class DummyConnection:
    def __init__(self):
        self.cursor_obj = DummyCursor()
        self.closed = 0
        self.autocommit = False
    def cursor(self, dictionary=False, cursor_factory=None):
        return self.cursor_obj
    def commit(self):
        pass
    def rollback(self):
        pass
    def close(self):
        self.closed = 1

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_signup_success(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "ValidPass123!"
    }
    with patch('app.psycopg2.connect', return_value=DummyConnection()):
        response = client.post('/api/signup', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert "Parent account created" in data["message"]
