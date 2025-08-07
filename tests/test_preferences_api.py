import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyCursor:
    def __init__(self):
        self.queries = []

    def execute(self, query, params=None):
        self.queries.append(query)

    def fetchone(self):
        return None

    def close(self):
        pass


class DummyConnection:
    def __init__(self):
        self.cursor_obj = DummyCursor()

    def cursor(self, *args, **kwargs):
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


def test_preferences_saved_to_db(client):
    conn = DummyConnection()
    with patch('auth.get_db_connection', return_value=conn), \
         patch('auth.ensure_user_preferences_table') as ensure_table:
        resp = client.post('/api/preferences', json={'userId': 1, 'darkMode': True, 'fontSize': 'large'})
    assert resp.status_code == 200
    assert any('INSERT INTO tbl_userpreferences' in q for q in conn.cursor_obj.queries)
    ensure_table.assert_called_once()
