import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyStoryCursor:
    def __init__(self):
        self.last_query = None
    def execute(self, query, params=None):
        self.last_query = query
    def fetchone(self):
        # No default theme or count
        return None
    def fetchall(self):
        # No available themes and no sections
        return []
    def close(self):
        pass


class DummyStoryConnection:
    def cursor(self, cursor_factory=None):
        return DummyStoryCursor()
    def close(self):
        pass


class DummyExistsCursor:
    def execute(self, query, params=None):
        pass
    def fetchone(self):
        # Pretend no sections exist for this topic
        return (0,)
    def close(self):
        pass


class DummyExistsConnection:
    def cursor(self):
        return DummyExistsCursor()
    def close(self):
        pass


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


def test_get_story_returns_placeholder(client):
    conn = DummyStoryConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.get('/api/story/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['sections'][0]['content'] == 'Story coming soon.'


def test_story_exists_reports_placeholder(client):
    conn = DummyExistsConnection()
    with patch('app.get_db_connection', return_value=conn):
        resp = client.get('/api/story_exists/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['storyExists'] is False
    assert data['isPlaceholder'] is True
