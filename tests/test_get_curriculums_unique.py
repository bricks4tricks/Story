import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self):
        self.subjects = ["Math", "Math", "Science"]
    def execute(self, query, params=None):
        self.query = query

    def fetchall(self):
        unique = sorted({name.strip() for name in self.subjects})
        return [(name,) for name in unique]
    def close(self):
        pass

class DummyConnection:
    def __init__(self):
        self.cursor_obj = DummyCursor()
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

def test_get_curriculums_returns_unique(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.get('/get_curriculums')
    assert resp.status_code == 200
    assert resp.get_json() == ["Math", "Science"]
