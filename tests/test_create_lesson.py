import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class TrackCursor:
    def __init__(self, curriculum_exists=True, grade_exists=True):
        self.curriculum_exists = curriculum_exists
        self.grade_exists = grade_exists
        self._fetchone = None
        self._fetchall = []
        self.queries = []

    def execute(self, query, params=None):
        q = str(query)
        self.queries.append(q)
        self._fetchone = None
        self._fetchall = []
        if "SELECT id FROM tbl_subject WHERE subjectname" in q:
            self._fetchone = (1,) if self.curriculum_exists else None
        elif "SELECT id FROM tbl_topic" in q and "parenttopicid IS NULL" in q:
            self._fetchone = None  # unit does not exist yet
        elif "SELECT id FROM tbl_grade" in q:
            self._fetchone = (3,) if self.grade_exists else None
        elif "SELECT id FROM tbl_subject WHERE subjecttype = 'Curriculum'" in q:
            self._fetchall = [(1,), (2,)]
        elif "RETURNING id" in q:
            self._fetchone = (2,)

    def fetchone(self):
        return self._fetchone

    def fetchall(self):
        return self._fetchall

    def close(self):
        pass


class DummyConnection:
    def __init__(self, curriculum_exists=True, grade_exists=True):
        self.cursor_obj = TrackCursor(curriculum_exists, grade_exists)

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


def test_create_lesson_success(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.post(
            '/api/admin/create-lesson',
            json={'curriculum': 'Math', 'unit': 'Algebra', 'lesson': 'Addition', 'grade': '4th Grade'}
        )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['status'] == 'success'
    assert any('INSERT INTO tbl_topicgrade' in q for q in conn.cursor_obj.queries)
    insert_links = [q for q in conn.cursor_obj.queries if 'INSERT INTO tbl_topicsubject' in q]
    assert len(insert_links) == 2


def test_create_lesson_missing_fields(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.post(
            '/api/admin/create-lesson',
            json={'curriculum': 'Math', 'unit': 'Algebra', 'lesson': 'Addition'}
        )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['status'] == 'error'


def test_create_lesson_curriculum_not_found(client):
    conn = DummyConnection(curriculum_exists=False)
    with patch('app.get_db_connection', return_value=conn):
        resp = client.post(
            '/api/admin/create-lesson',
            json={'curriculum': 'Nope', 'unit': 'Algebra', 'lesson': 'Addition', 'grade': '4th Grade'}
        )
    assert resp.status_code == 404
    data = resp.get_json()
    assert data['status'] == 'error'


def test_create_lesson_creates_grade_when_missing(client):
    conn = DummyConnection(grade_exists=False)
    with patch('app.get_db_connection', return_value=conn):
        resp = client.post(
            '/api/admin/create-lesson',
            json={'curriculum': 'Math', 'unit': 'Algebra', 'lesson': 'Addition', 'grade': 'Unknown'}
        )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['status'] == 'success'
    # Ensure a grade was inserted and linked to the new lesson
    assert any('INSERT INTO tbl_grade' in q for q in conn.cursor_obj.queries)
    assert any('INSERT INTO tbl_topicgrade' in q for q in conn.cursor_obj.queries)
