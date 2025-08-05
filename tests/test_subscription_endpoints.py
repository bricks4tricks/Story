import os
import sys
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyDB:
    def __init__(self, user_exists=True, subscription=None):
        self.user_exists = user_exists
        self.subscription = subscription  # dict or None


class DummyCursor:
    def __init__(self, db):
        self.db = db
        self.last_query = ""
        self.rowcount = 0

    def execute(self, query, params=None):
        self.last_query = query
        if "UPDATE tbl_subscription SET active = FALSE" in query:
            if self.db.subscription and self.db.subscription.get("active"):
                self.db.subscription["active"] = False
                self.rowcount = 1
            else:
                self.rowcount = 0
        else:
            self.rowcount = 0

    def fetchone(self):
        if "SELECT id FROM tbl_user" in self.last_query:
            return (1,) if self.db.user_exists else None
        if "SELECT active, expires_on FROM tbl_subscription" in self.last_query:
            sub = self.db.subscription
            if sub:
                return (sub.get("active"), sub.get("expires_on"))
            return None
        if "SELECT active FROM tbl_subscription" in self.last_query:
            sub = self.db.subscription
            if sub:
                return (sub.get("active"),)
            return None
        return None

    def close(self):
        pass


class DummyConnection:
    def __init__(self, db):
        self.db = db

    def cursor(self, cursor_factory=None):
        return DummyCursor(self.db)

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


def test_subscription_status_inactive(client):
    db = DummyDB(subscription=None)
    with patch("app.get_db_connection", return_value=DummyConnection(db)):
        resp = client.get("/api/subscription-status/1")
    assert resp.status_code == 200
    assert resp.get_json() == {"active": False}


def test_subscription_status_active_naive(client):
    sub = {"active": True, "expires_on": datetime.utcnow() + timedelta(days=5)}
    db = DummyDB(subscription=sub)
    with patch("app.get_db_connection", return_value=DummyConnection(db)):
        resp = client.get("/api/subscription-status/1")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["active"] is True
    assert "expires_on" in data


def test_subscription_status_active_timezone_aware(client):
    sub = {
        "active": True,
        "expires_on": datetime.now(timezone.utc) + timedelta(days=5),
    }
    db = DummyDB(subscription=sub)
    with patch("app.get_db_connection", return_value=DummyConnection(db)):
        resp = client.get("/api/subscription-status/1")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["active"] is True
    assert "expires_on" in data


def test_cancel_subscription_no_active(client):
    db = DummyDB(subscription=None)
    with patch("app.get_db_connection", return_value=DummyConnection(db)):
        resp = client.post("/api/cancel-subscription/1")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["status"] == "error"


def test_cancel_subscription_success_marks_inactive(client):
    sub = {"active": True, "expires_on": datetime.utcnow() + timedelta(days=5)}
    db = DummyDB(subscription=sub)
    with patch("app.get_db_connection", return_value=DummyConnection(db)):
        resp = client.post("/api/cancel-subscription/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        resp2 = client.get("/api/subscription-status/1")
    assert resp2.get_json()["active"] is False

