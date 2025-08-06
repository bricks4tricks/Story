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
        self.returning_id = 1
    def execute(self, query, params=None):
        self.executed.append((query, params))
    def fetchone(self):
        # Return an id when INSERT ... RETURNING is executed
        if 'RETURNING id' in self.executed[-1][0]:
            return (self.returning_id,)
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
    with patch('auth.get_db_connection', return_value=DummyConnection()):
        response = client.post('/api/signup', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert "Parent account created" in data["message"]
    assert data["userId"] == 1


def test_signup_invalid_email(client):
    payload = {
        "username": "bademailuser",
        "email": "invalidemail@domain",
        "password": "ValidPass123!"
    }
    with patch('auth.get_db_connection', return_value=DummyConnection()):
        response = client.post('/api/signup', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "Invalid email address" in data["message"]


def test_signup_defaults_plan_to_monthly(client):
    payload = {
        "username": "planuser",
        "email": "planuser@example.com",
        "password": "ValidPass123!",
    }
    conn = DummyConnection()
    with patch('auth.get_db_connection', return_value=conn):
        response = client.post('/api/signup', json=payload)
    assert response.status_code == 201
    insert_query = conn.cursor_obj.executed[-1]
    assert 'INSERT INTO tbl_user' in insert_query[0]
    assert insert_query[1][-1] == 'Monthly'
