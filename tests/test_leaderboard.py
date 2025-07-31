import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed = []
    def execute(self, query, params=None):
        self.executed.append((query, params))
    def fetchall(self):
        return self.rows
    def close(self):
        pass

class DummyConnection:
    def __init__(self, rows):
        self.cursor_obj = DummyCursor(rows)
    def cursor(self, dictionary=False, cursor_factory=None):
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


def test_get_leaderboard(client):
    rows = [{"id": 1, "username": "user1", "average_score": 90.5, "attempts": 3}]
    with patch('app.get_db_connection', return_value=DummyConnection(rows)):
        resp = client.get('/api/leaderboard')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data[0]['username'] == 'user1'
