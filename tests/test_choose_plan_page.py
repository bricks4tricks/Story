import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_choose_plan_page_loads(client):
    response = client.get('/choose-plan.html')
    assert response.status_code == 200
    assert b'Choose Your Plan' in response.data
