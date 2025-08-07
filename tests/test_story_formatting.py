import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyCursor:
    def __init__(self):
        self.last_query = None
    def execute(self, query, params=None):
        self.last_query = query
    def fetchone(self):
        if "FROM tbl_topictheme" in self.last_query and "LIMIT 1" in self.last_query:
            return None
        return None
    def fetchall(self):
        if "FROM tbl_topictheme" in self.last_query:
            return []
        elif "FROM tbl_description" in self.last_query:
            return [
                {
                    'id': 1,
                    'sectionname': 'Intro',
                    'descriptiontext': 'First line\nSecond line',
                    'interactiveelementid': None,
                    'descriptionorder': 1,
                    'contenttype': 'Paragraph',
                }
            ]
        return []
    def close(self):
        pass


class DummyConnection:
    def cursor(self, cursor_factory=None):
        return DummyCursor()
    def close(self):
        pass


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


def test_story_paragraph_newlines_replaced_with_br(client):
    conn = DummyConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.get('/api/story/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['sections'][0]['content'] == 'First line<br>Second line'
