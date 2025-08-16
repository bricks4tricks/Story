import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers


class DummyCursor:
    def execute(self, query, params=None):
        pass

    def close(self):
        pass


class DummyConnection:
    def __init__(self):
        self.cursor_obj = DummyCursor()

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
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_add_video_success(client):
    conn = DummyConnection()
    with patch("app.get_db_connection", return_value=conn), mock_admin_auth():
        resp = client.post(
            "/api/admin/add-video",
            json={"topicId": 1, "youtubeUrl": "https://youtu.be/test"},
            headers=get_admin_headers()
        )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "success"


def test_add_video_missing_fields(client):
    conn = DummyConnection()
    with patch("app.get_db_connection", return_value=conn), mock_admin_auth():
        resp = client.post("/api/admin/add-video", json={}, headers=get_admin_headers())
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["status"] == "error"
