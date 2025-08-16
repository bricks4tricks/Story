import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app
from test_auth_utils import mock_student_auth, get_student_headers


class DummyCursor:
    def __init__(self):
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def close(self):
        pass


class DummyConnection:
    def __init__(self):
        self.cursor_obj = DummyCursor()

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


def test_record_question_attempt_accepts_zero_ids(client):
    conn = DummyConnection()
    payload = {
        'userId': 0,
        'questionId': 0,
        'userAnswer': '42',
        'isCorrect': True,
        'difficultyAtAttempt': 1
    }
    with patch('app.get_db_connection', return_value=conn), mock_student_auth():
        resp = client.post('/api/record-question-attempt', json=payload, headers=get_student_headers())
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['status'] == 'success'
    query, params = conn.cursor_obj.executed[0]
    assert 'INSERT INTO tbl_questionattempt' in query
    assert params == (0, 0, '42', True, 1)


def test_record_question_attempt_rejects_none(client):
    conn = DummyConnection()
    payload = {
        'userId': None,
        'questionId': 1,
        'userAnswer': 'answer',
        'isCorrect': False,
        'difficultyAtAttempt': 2
    }
    with patch('app.get_db_connection', return_value=conn), mock_student_auth():
        resp = client.post('/api/record-question-attempt', json=payload, headers=get_student_headers())
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['status'] == 'error'
    assert conn.cursor_obj.executed == []

