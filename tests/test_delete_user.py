import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers

class DummyCursor:
    def __init__(self, user_exists=True, user_type='Student', has_children=False, delete_rowcount=1):
        self.user_exists = user_exists
        self.user_type = user_type
        self.has_children = has_children
        self.delete_rowcount = delete_rowcount
        self.queries = []
        self.last_query = ""
        self.rowcount = delete_rowcount
    def execute(self, query, params=None):
        self.last_query = query
        self.queries.append(query)
    def fetchone(self):
        if "SELECT usertype" in self.last_query:
            return (self.user_type,) if self.user_exists else None
        if "SELECT id FROM tbl_user WHERE parentuserid" in self.last_query:
            return (1,) if self.has_children else None
        return None
    def close(self):
        pass

class DummyConnection:
    def __init__(self, **cursor_kwargs):
        self.cursor_obj = DummyCursor(**cursor_kwargs)
        self.commit_called = False
        self.rollback_called = False
    def cursor(self, dictionary=False, cursor_factory=None):
        return self.cursor_obj
    def commit(self):
        self.commit_called = True
    def rollback(self):
        self.rollback_called = True
    def close(self):
        pass

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


def test_delete_user_success_removes_subscription(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.delete('/api/admin/delete-user/1', headers=get_admin_headers())
    assert resp.status_code == 200
    q = " ".join(conn.cursor_obj.queries)
    assert "DELETE FROM tbl_subscription" in q
    assert "DELETE FROM tbl_user" in q


def test_delete_user_not_found(client):
    conn = DummyConnection(user_exists=True, delete_rowcount=0)
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        with patch('app.update_users_version') as mock_update:
            resp = client.delete('/api/admin/delete-user/99', headers=get_admin_headers())
    assert resp.status_code == 404
    assert conn.rollback_called is True
    assert conn.commit_called is False
    mock_update.assert_not_called()
