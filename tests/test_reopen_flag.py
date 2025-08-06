import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self):
        self.executed = []
        self.rowcount = 1
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

def test_reopen_flag(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.put('/api/admin/update-flag-status/1', json={'status': 'Pending', 'adminId': 2})
    assert resp.status_code == 200
    query, params = conn.cursor_obj.executed[0]
    assert 'ResolvedOn = NULL' in query
    assert params == ('Pending', 1)


def test_update_flag_status_admin_id_zero(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.put('/api/admin/update-flag-status/1', json={'status': 'Reviewed', 'adminId': 0})
    assert resp.status_code == 200
    query, params = conn.cursor_obj.executed[0]
    assert 'ResolvedOn = NOW()' in query
    assert params == ('Reviewed', 0, 1)

