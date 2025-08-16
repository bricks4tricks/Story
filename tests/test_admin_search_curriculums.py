import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers

class DummyCursor:
    def __init__(self):
        self.query = None
        self.params = None
    def execute(self, query, params=None):
        self.query = query
        self.params = params
    def fetchall(self):
        # Return filtered result assuming search for 'math'
        if self.params:
            return [{'id': 1, 'subjectname': 'Math'}]
        return [
            {'id': 1, 'subjectname': 'Math'},
            {'id': 2, 'subjectname': 'Science'}
        ]
    def close(self):
        pass

class DummyConnection:
    def __init__(self):
        self.cursor_obj = DummyCursor()
    def cursor(self, cursor_factory=None):
        return self.cursor_obj
    def close(self):
        pass

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_admin_curriculums_search(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.get('/api/admin/curriculums?search=math', headers=get_admin_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == [{'id': 1, 'subjectname': 'Math'}]
    cursor = conn.cursor_obj
    assert 'ILIKE' in cursor.query
    assert cursor.params == ('%math%',)
