import sys
import os
import sys
import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyCursor:
    def __init__(self, url=None):
        self.url = url

    def execute(self, query, params=None):
        pass

    def fetchone(self):
        if self.url is None:
            return None
        return (self.url,)

    def close(self):
        pass


class DummyConnection:
    def __init__(self, url=None):
        self.cursor_obj = DummyCursor(url)

    def cursor(self, cursor_factory=None):
        return self.cursor_obj

    def close(self):
        pass


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

def test_get_video_success(client):
    conn = DummyConnection("https://youtu.be/test")
    with patch("app.get_db_connection", return_value=conn):
        resp = client.get("/api/video/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["videoUrl"] == "https://youtu.be/test"


def test_get_video_not_found(client):
    conn = DummyConnection(None)
    with patch("app.get_db_connection", return_value=conn):
        resp = client.get("/api/video/1")
    assert resp.status_code == 404
