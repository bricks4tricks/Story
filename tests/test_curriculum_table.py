import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self, rows):
        self.rows = rows
    def execute(self, query):
        pass
    def fetchall(self):
        return self.rows
    def close(self):
        pass

class DummyConnection:
    def __init__(self, rows):
        self.cursor_obj = DummyCursor(rows)
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


def test_curriculum_table(client):
    rows = [
        {"gradename": "4th Grade", "curriculumtype": "Math", "unitname": "Algebra", "topicname": "Addition"},
        {"gradename": "4th Grade", "curriculumtype": "Math", "unitname": "Algebra", "topicname": "Subtraction"}
    ]
    conn = DummyConnection(rows)
    with patch('app.get_db_connection', return_value=conn):
        resp = client.get('/api/curriculum-table')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == rows
