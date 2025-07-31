import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self, rowcount=1):
        self.executed = []
        self.rowcount = rowcount
    def execute(self, query, params=None):
        self.executed.append((query, params))
    def close(self):
        pass

class DummyConnection:
    def __init__(self, rowcount=1):
        self.cursor_obj = DummyCursor(rowcount)
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


def test_delete_flag_success(client):
    with patch('app.get_db_connection', return_value=DummyConnection()):
        resp = client.delete('/api/admin/delete-flag/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'


def test_delete_flag_not_found(client):
    with patch('app.get_db_connection', return_value=DummyConnection(rowcount=0)):
        resp = client.delete('/api/admin/delete-flag/99')
    assert resp.status_code == 404
    data = resp.get_json()
    assert data['status'] == 'error'
