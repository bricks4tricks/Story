import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers

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


def test_curriculum_hierarchy(client):
    rows = [
        {'curriculum': 'Math', 'unitname': 'Algebra', 'topicname': 'Addition', 'topicid': 1},
        {'curriculum': 'Math', 'unitname': 'Algebra', 'topicname': 'Subtraction', 'topicid': 2},
        {'curriculum': 'Science', 'unitname': 'Biology', 'topicname': 'Cells', 'topicid': 3},
    ]
    conn = DummyConnection(rows)
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.get('/api/admin/curriculum-hierarchy', headers=get_admin_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'Math' in data
    assert 'Algebra' in data['Math']
    assert {'id': 1, 'name': 'Addition'} in data['Math']['Algebra']
