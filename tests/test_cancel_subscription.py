import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self, user_exists=True):
        self.user_exists = user_exists
        self.last_query = ""
        self.rowcount = 1
    def execute(self, query, params=None):
        self.last_query = query
        if "SELECT id FROM tbl_user" in query:
            pass
        elif query.strip().upper().startswith("UPDATE") and not self.user_exists:
            self.rowcount = 0
    def fetchone(self):
        if "SELECT id FROM tbl_user" in self.last_query:
            return (1,) if self.user_exists else None
        return None
    def close(self):
        pass

class DummyConnection:
    def __init__(self, user_exists=True):
        self.cursor_obj = DummyCursor(user_exists)
    def cursor(self, cursor_factory=None):
        return self.cursor_obj
    def commit(self):
        pass
    def rollback(self):
        pass
    def close(self):
        pass

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_cancel_subscription_success(client):
    with patch('app.get_db_connection', return_value=DummyConnection()):
        resp = client.post('/api/cancel-subscription/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'

def test_cancel_subscription_user_not_found(client):
    with patch('app.get_db_connection', return_value=DummyConnection(user_exists=False)):
        resp = client.post('/api/cancel-subscription/99')
    assert resp.status_code == 404
    data = resp.get_json()
    assert data['status'] == 'error'
