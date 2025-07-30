import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self):
        self.executed = []
    def execute(self, query, params=None):
        self.executed.append((query, params))
    def close(self):
        pass

class DummyConnection:
    def __init__(self):
        self.cursor_obj = DummyCursor()
        self.closed = 0
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

def test_flag_page_error(client):
    payload = {
        "userId": 1,
        "pagePath": "/index.html",
        "description": "typo"
    }
    with patch('app.get_db_connection', return_value=DummyConnection()):
        response = client.post('/api/flag-page-error', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert "Error reported" in data["message"]
