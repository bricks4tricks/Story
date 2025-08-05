import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

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

def test_record_quiz_result_valid(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.post('/api/quiz/result', json={'userId': 1, 'topicId': 2, 'score': 85})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['status'] == 'success'
    query, params = conn.cursor_obj.executed[0]
    assert 'INSERT INTO tbl_quizscore' in query
    assert params == (1, 2, 85)

def test_record_quiz_result_invalid_score(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.post('/api/quiz/result', json={'userId': 1, 'topicId': 2, 'score': 150})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['status'] == 'error'
    assert 'integer between 0 and 100' in data['message']



def test_record_quiz_result_invalid_type(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.post('/api/quiz/result', json={'userId': 1, 'topicId': 2, 'score': 'bad'})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['status'] == 'error'
    assert 'integer between 0 and 100' in data['message']


def test_record_quiz_result_missing_user_id(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.post('/api/quiz/result', json={'topicId': 2, 'score': 85})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Missing required fields.'
    assert conn.cursor_obj.executed == []

