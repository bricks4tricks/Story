import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_edit_user_invalid_json_returns_error(client):
    with mock_admin_auth():
        response = client.put(
            "/api/admin/edit-user/1", data="invalid", content_type="application/json", headers=get_admin_headers()
        )
    assert response.status_code == 400
    assert response.mimetype == "application/json"
    data = response.get_json()
    assert data["status"] == "error"
    assert data["message"] == "Invalid JSON"
