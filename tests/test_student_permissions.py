import os
import sys
from unittest.mock import patch
import pytest

# Ensure the app can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyCursor:
    def __init__(self, usertype='Student'):
        self.usertype = usertype
        self.calls = 0
        self.rowcount = 1

    def execute(self, query, params=None):
        self.last_query = query

    def fetchone(self):
        if 'passwordhash' in getattr(self, 'last_query', ''):
            # For change-password route
            return (b'hash', self.usertype)
        # For update-profile route
        if self.calls == 0:
            self.calls += 1
            return (self.usertype,)
        return None

    def close(self):
        pass


class DummyConnection:
    def __init__(self, usertype='Student'):
        self.cursor_obj = DummyCursor(usertype)

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


def test_student_cannot_update_profile(client):
    conn = DummyConnection('Student')
    with patch('auth.get_db_connection', return_value=conn), \
         patch('auth.update_users_version'):
        resp = client.post('/api/update-profile', json={
            'userId': 1,
            'username': 'new',
            'email': 'new@example.com'
        })
    assert resp.status_code == 403


def test_student_cannot_change_password(client):
    conn = DummyConnection('Student')
    with patch('auth.get_db_connection', return_value=conn), \
         patch('auth.update_users_version'), \
         patch('extensions.bcrypt.check_password_hash', return_value=True), \
         patch('extensions.bcrypt.generate_password_hash', return_value=b'hash'):
        resp = client.post('/api/change-password', json={
            'userId': 1,
            'currentPassword': 'Oldpass1!',
            'newPassword': 'Newpass2@'
        })
    assert resp.status_code == 403
