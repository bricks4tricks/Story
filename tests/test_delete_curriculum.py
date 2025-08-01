import os
import sys
from unittest.mock import patch
import pytest
import psycopg2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self, rowcount=1):
        self.rowcount = rowcount
        self._fetchall = []
    def execute(self, query, params=None):
        self._fetchall = []
    def fetchall(self):
        return self._fetchall
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


def test_delete_curriculum_cascades_topics(client):
    class TrackCursor:
        def __init__(self):
            self.rowcount = 1
            self.executed = []
            self._fetchall = []

        def execute(self, query, params=None):
            q_str = str(query)
            self.executed.append(q_str)
            if "SELECT id FROM tbl_topic" in q_str:
                self._fetchall = [(1,), (2,)]
            elif "SELECT interactiveelementid FROM tbl_description" in q_str:
                self._fetchall = []
            else:
                self._fetchall = []

        def fetchall(self):
            return self._fetchall

        def close(self):
            pass

    class TrackConnection:
        def __init__(self):
            self.cursor_obj = TrackCursor()
            self.autocommit = True

        def cursor(self, cursor_factory=None):
            return self.cursor_obj

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    conn = TrackConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.delete('/api/admin/delete-curriculum/1')

    assert resp.status_code == 200
    queries = conn.cursor_obj.executed
    subject_index = next(i for i, q in enumerate(queries) if "DELETE FROM tbl_subject" in q)
    topic_index = next(i for i, q in enumerate(queries) if "DELETE FROM tbl_topic" in q)
    assert topic_index < subject_index


def test_delete_curriculum_removes_steps_before_questions(client):
    class TrackCursor:
        def __init__(self):
            self.rowcount = 1
            self.executed = []
            self._fetchall = []

        def execute(self, query, params=None):
            q_str = str(query)
            self.executed.append(q_str)
            if "SELECT id FROM tbl_topic" in q_str:
                self._fetchall = [(1,)]
            elif "SELECT interactiveelementid FROM tbl_description" in q_str:
                self._fetchall = []
            elif "SELECT id FROM tbl_question" in q_str:
                self._fetchall = [(10,), (11,)]
            else:
                self._fetchall = []

        def fetchall(self):
            return self._fetchall

        def close(self):
            pass

    class TrackConnection:
        def __init__(self):
            self.cursor_obj = TrackCursor()
            self.autocommit = True

        def cursor(self, cursor_factory=None):
            return self.cursor_obj

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    conn = TrackConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.delete('/api/admin/delete-curriculum/1')

    assert resp.status_code == 200
    queries = conn.cursor_obj.executed
    step_index = next(i for i, q in enumerate(queries) if "DELETE FROM tbl_step" in q)
    question_index = next(i for i, q in enumerate(queries) if "DELETE FROM tbl_question" in q)
    assert step_index < question_index


def test_delete_curriculum_missing_quizscore_table(client):
    class ErrorCursor(DummyCursor):
        def execute(self, query, params=None):
            if "tbl_quizscore" in str(query):
                raise psycopg2.errors.UndefinedTable
            super().execute(query, params)

    class ErrorConnection(DummyConnection):
        def __init__(self):
            self.cursor_obj = ErrorCursor()
            self.autocommit = True

    conn = ErrorConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.delete('/api/admin/delete-curriculum/1')

    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
