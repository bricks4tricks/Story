import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self, rows):
        self.executed = []
        self.rows = rows
    def execute(self, query, params=None):
        self.executed.append((query, params))
    def fetchall(self):
        return self.rows
    def close(self):
        pass

class DummyConnection:
    def __init__(self, rows):
        self.cursor_obj = DummyCursor(rows)
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


def test_get_open_flags(client):
    rows = [{"FlagID": 1, "ItemType": "Question", "ItemName": "Sample"}]
    with patch('app.get_db_connection', return_value=DummyConnection(rows)):
        resp = client.get('/api/open-flags')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data[0]['FlagID'] == 1
