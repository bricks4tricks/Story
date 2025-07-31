import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self):
        self.call = 0
        self.results = [
            [{'topic_id': 1, 'topicname': 'Topic 1'}],
            [{'topic_id': 1, 'topicname': 'Topic 1', 'score': 80, 'takenon': '2024-01-01'}],
            [{'id': 2, 'title': 'Homework', 'due_date': '2024-12-31'}],
        ]
    def execute(self, query, params=None):
        pass
    def fetchall(self):
        res = self.results[self.call]
        self.call += 1
        return res
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

def test_get_dashboard(client):
    with patch('app.get_db_connection', return_value=DummyConnection()):
        resp = client.get('/api/dashboard/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'completedModules' in data
    assert 'quizScores' in data
    assert 'upcomingAssignments' in data
