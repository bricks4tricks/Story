import os
from unittest.mock import patch
import pytest


from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers


class DummyCursor:
    def __init__(self, rowcount=1):
        self.rowcount = rowcount
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append(str(query))

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


class TrackCursor:
    def __init__(self, final_rowcount=1):
        self.final_rowcount = final_rowcount
        self.rowcount = 1
        self.executed = []
        self._fetchall = []

    def execute(self, query, params=None):
        q = str(query)
        self.executed.append(q)
        if "SELECT id FROM tbl_question" in q:
            self._fetchall = []
        elif "SELECT interactiveelementid FROM tbl_description" in q:
            self._fetchall = []
        elif "DELETE FROM tbl_topic" in q:
            self.rowcount = self.final_rowcount
        else:
            self.rowcount = 1

    def fetchall(self):
        return self._fetchall

    def fetchone(self):
        return (None,)

    def close(self):
        pass


class TrackConnection:
    def __init__(self, final_rowcount=1):
        self.cursor_obj = TrackCursor(final_rowcount)

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


def test_update_topic_success(client):
    conn = DummyConnection(rowcount=1)
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.put('/api/admin/update-topic/1', json={'name': 'New Name'}, headers=get_admin_headers())
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'success'


def test_update_topic_not_found(client):
    conn = DummyConnection(rowcount=0)
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.put('/api/admin/update-topic/1', json={'name': 'New Name'}, headers=get_admin_headers())
    assert resp.status_code == 404
    assert resp.get_json()['status'] == 'error'


def test_delete_topic_success(client):
    conn = TrackConnection()
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.delete('/api/admin/delete-topic/1', headers=get_admin_headers())
    assert resp.status_code == 200
    queries = conn.cursor_obj.executed
    assert any("DELETE FROM tbl_topic" in q for q in queries)


def test_delete_topic_not_found(client):
    conn = TrackConnection(final_rowcount=0)
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.delete('/api/admin/delete-topic/99', headers=get_admin_headers())
    assert resp.status_code == 404
    assert resp.get_json()['status'] == 'error'

