import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers

class DummyCursor:
    def __init__(self, rowcount=1):
        self.rowcount = rowcount
    def execute(self, query, params=None):
        pass
    def fetchall(self):
        return []
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

def test_update_curriculum_success(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.put('/api/admin/update-curriculum/1', json={'name': 'Math'}, headers=get_admin_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'

def test_update_curriculum_not_found(client):
    conn = DummyConnection(rowcount=0)
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.put('/api/admin/update-curriculum/99', json={'name': 'Math'}, headers=get_admin_headers())
    assert resp.status_code == 404
    data = resp.get_json()
    assert data['status'] == 'error'

def test_update_curriculum_missing_name(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.put('/api/admin/update-curriculum/1', json={}, headers=get_admin_headers())
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['status'] == 'error'
