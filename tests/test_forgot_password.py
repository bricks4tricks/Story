import os
import sys
from unittest.mock import patch

import pytest

# Ensure app module accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyCursor:
    def __init__(self, conn):
        self.conn = conn
        self.last_query = None

    def execute(self, query, params=None):
        self.last_query = query
        if "UPDATE tbl_user SET resettoken" in query:
            # Store pending token update
            self.conn.pending = (params[0], params[1])

    def fetchone(self):
        if self.last_query and "SELECT id FROM tbl_user WHERE email" in self.last_query:
            return (1,)
        return None

    def close(self):
        pass


class DummyConnection:
    def __init__(self):
        self.user = {"id": 1, "resettoken": None, "resettokenexpiry": None}
        self.pending = None
        self.rolled_back = False

    def cursor(self, dictionary=False, cursor_factory=None):
        return DummyCursor(self)

    def commit(self):
        if self.pending:
            self.user["resettoken"], self.user["resettokenexpiry"] = self.pending
            self.pending = None

    def rollback(self):
        self.pending = None
        self.rolled_back = True

    def close(self):
        pass


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_forgot_password_email_failure(client):
    dummy_conn = DummyConnection()
    with patch("app.get_db_connection", return_value=dummy_conn), \
         patch("auth.send_email", return_value=False):
        response = client.post("/api/forgot-password", json={"email": "user@example.com"})
    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"
    assert dummy_conn.rolled_back is True
    assert dummy_conn.user["resettoken"] is None


def test_forgot_password_requires_email(client):
    response = client.post("/api/forgot-password", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert data["message"] == "Email is required"


def test_forgot_password_malformed_json(client):
    response = client.post("/api/forgot-password", data="{" , content_type="application/json")
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert data["message"] == "Email is required"
