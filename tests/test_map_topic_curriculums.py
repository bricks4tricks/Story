import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers


class TrackCursor:
    def __init__(self):
        self.queries = []

    def execute(self, query, params=None):
        self.queries.append(str(query))

    def close(self):
        pass

    def fetchall(self):
        return []

    def fetchone(self):
        return None


class DummyConnection:
    def __init__(self):
        self.cursor_obj = TrackCursor()

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


def test_map_topic_curriculums_inserts_links(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn), mock_admin_auth():
        resp = client.post(
            '/api/admin/map-topic-curriculums',
            json={'topic_id': 5, 'curriculum_ids': [1, 2]},
            headers=get_admin_headers()
        )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['status'] == 'success'
    insert_queries = [q for q in conn.cursor_obj.queries if 'INSERT INTO tbl_topicsubject' in q]
    assert len(insert_queries) == 2
