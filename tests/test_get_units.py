import os
import sys
from unittest.mock import patch
from flask import jsonify
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_get_units_invalid_curriculum(client):
    def dummy_curriculums():
        return jsonify(["Math", "Science"])

    with patch('app.get_curriculums', side_effect=dummy_curriculums), \
         patch('app.get_db_connection', side_effect=AssertionError("db should not be used")):
        resp = client.get('/get_units/History')

    assert resp.status_code == 400
    data = resp.get_json()
    assert data["status"] == "error"
    assert "Invalid curriculum" in data["message"]
