import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self, rowcount=1):
        self.rowcount = rowcount
    def execute(self, query, params=None):
        pass
    def close(self):
        pass

class DummyConnection:
    def __init__(self, rowcount=1):
        self.cursor_obj = DummyCursor(rowcount)
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

def test_delete_curriculum_success(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.delete('/api/admin/delete-curriculum/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'

def test_delete_curriculum_not_found(client):
    conn = DummyConnection(rowcount=0)
    with patch('app.get_db_connection', return_value=conn):
        resp = client.delete('/api/admin/delete-curriculum/99')
    assert resp.status_code == 404
    data = resp.get_json()
    assert data['status'] == 'error'
