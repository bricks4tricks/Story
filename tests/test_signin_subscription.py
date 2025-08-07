import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(
        self,
        active=True,
        expired=False,
        has_subscription=True,
        usertype="Parent",
        parent_id=None,
    ):
        self.active = active
        self.expired = expired
        self.has_subscription = has_subscription
        self.usertype = usertype
        self.parent_id = parent_id
        self.calls = 0

    def execute(self, query, params=None):
        self.last_query = query

    def fetchone(self):
        # First call fetches user
        if self.calls == 0:
            self.calls += 1
            # id, username, hash, usertype, parent_id
            return (1, "user", b"hash", self.usertype, self.parent_id)
        # Second call fetches subscription
        elif self.calls == 1:
            self.calls += 1
            if not self.has_subscription:
                return None
            from datetime import datetime
            expires = datetime(2020, 1, 1) if self.expired else datetime(2999, 1, 1)
            return (self.active, expires)
        return None

    def close(self):
        pass


class DummyConnection:
    def __init__(
        self,
        active=True,
        expired=False,
        has_subscription=True,
        usertype="Parent",
        parent_id=None,
    ):
        self.cursor_obj = DummyCursor(
            active, expired, has_subscription, usertype, parent_id
        )
    def cursor(self, dictionary=False, cursor_factory=None):
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


def test_signin_subscription_inactive(client):
    conn = DummyConnection(active=False)
    with patch('auth.get_db_connection', return_value=conn), \
         patch('extensions.bcrypt.check_password_hash', return_value=True):
        resp = client.post('/api/signin', json={'username': 'user', 'password': 'pw'})
    assert resp.status_code == 200


def test_signin_subscription_expired(client):
    conn = DummyConnection(active=True, expired=True)
    with patch('auth.get_db_connection', return_value=conn), \
         patch('extensions.bcrypt.check_password_hash', return_value=True):
        resp = client.post('/api/signin', json={'username': 'user', 'password': 'pw'})
    assert resp.status_code == 200


def test_signin_subscription_absent_record(client):
    conn = DummyConnection(has_subscription=False)
    with patch('auth.get_db_connection', return_value=conn), \
         patch('extensions.bcrypt.check_password_hash', return_value=True):
        resp = client.post('/api/signin', json={'username': 'user', 'password': 'pw'})
    assert resp.status_code == 200


def test_student_signin_requires_active_subscription(client):
    conn = DummyConnection(active=False, usertype="Student", parent_id=2)
    with patch('auth.get_db_connection', return_value=conn), \
         patch('extensions.bcrypt.check_password_hash', return_value=True):
        resp = client.post('/api/signin', json={'username': 'user', 'password': 'pw'})
    assert resp.status_code == 403


def test_student_signin_with_active_subscription(client):
    conn = DummyConnection(usertype="Student", parent_id=2)
    with patch('auth.get_db_connection', return_value=conn), \
         patch('extensions.bcrypt.check_password_hash', return_value=True):
        resp = client.post('/api/signin', json={'username': 'user', 'password': 'pw'})
    assert resp.status_code == 200


def test_student_signin_requires_subscription_record(client):
    conn = DummyConnection(has_subscription=False, usertype="Student", parent_id=2)
    with patch('auth.get_db_connection', return_value=conn), \
         patch('extensions.bcrypt.check_password_hash', return_value=True):
        resp = client.post('/api/signin', json={'username': 'user', 'password': 'pw'})
    assert resp.status_code == 403


def test_signin_missing_json_body(client):
    resp = client.post('/api/signin')
    assert resp.status_code == 400
