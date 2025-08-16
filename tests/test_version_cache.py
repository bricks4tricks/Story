import datetime
import sys
import os
import time
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import version_cache
from app import app as flask_app
from test_auth_utils import mock_admin_auth, get_admin_headers


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_users_version_timezone():
    assert version_cache.users_version.tzinfo is datetime.timezone.utc
    version_cache.update_users_version()
    assert version_cache.users_version.tzinfo is datetime.timezone.utc


def test_admin_users_version_endpoint_updates(client):
    with mock_admin_auth():
        response1 = client.get("/api/admin/users-version", headers=get_admin_headers())
        assert response1.status_code == 200
        version1 = response1.get_json()["version"]

        time.sleep(0.01)
        version_cache.update_users_version()

        response2 = client.get("/api/admin/users-version", headers=get_admin_headers())
        assert response2.status_code == 200
        version2 = response2.get_json()["version"]

    assert version2 != version1
    dt1 = datetime.datetime.fromisoformat(version1)
    dt2 = datetime.datetime.fromisoformat(version2)
    assert dt2 >= dt1
