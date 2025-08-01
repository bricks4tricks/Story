import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyCursor:
    """A minimal cursor used to simulate database interactions."""

    def __init__(self, user_exists: bool = True):
        self.user_exists = user_exists
        # ``rowcount`` is used by the route to determine if a user was updated.
        self.rowcount = 1 if user_exists else 0

    def execute(self, query, params=None):
        pass

    def fetchone(self):
        return None

    def close(self):
        pass


class DummyConnection:
    def __init__(self, user_exists: bool = True):
        self.cursor_obj = DummyCursor(user_exists)

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


@pytest.mark.parametrize('plan', ['Monthly', 'Annual', 'Family'])
def test_select_plan_success(client, plan):
    """Selecting any valid plan should return success."""
    with patch('app.get_db_connection', return_value=DummyConnection()):
        resp = client.post('/api/select-plan', json={'userId': 1, 'plan': plan})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    assert data['message'] == 'Plan updated'


def test_select_plan_user_not_found(client):
    """If the user row is missing the API should respond with 404."""
    with patch('app.get_db_connection', return_value=DummyConnection(user_exists=False)):
        resp = client.post('/api/select-plan', json={'userId': 99, 'plan': 'Monthly'})
    assert resp.status_code == 404
    data = resp.get_json()
    assert data['status'] == 'error'


def test_select_plan_missing_user_id(client):
    """Requests without a userId should return a 400 error."""
    resp = client.post('/api/select-plan', json={'plan': 'Monthly'})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['status'] == 'error'


def test_select_plan_invalid_plan(client):
    """Invalid plan values should be rejected."""
    resp = client.post('/api/select-plan', json={'userId': 1, 'plan': 'Weekly'})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['status'] == 'error'
