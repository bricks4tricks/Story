"""
Regression test to ensure our pytest fixes remain working.
Tests all the endpoints we added and issues we fixed.
"""

import pytest
from unittest.mock import patch
from tests.test_helpers import DummyConnection, mock_admin_auth, get_admin_headers, get_student_headers
import os
import sys

# Add parent directory to path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def client():
    # Import app inside the fixture to avoid circular import issues
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_regression_endpoints_exist(client):
    """Test that key endpoints we fixed exist and don't return 404."""
    # Test some endpoints exist (may return other errors like 403/401, but not 404)
    endpoints_to_test = [
        ('/api/quiz-exists/123', 'GET'),
        ('/api/open-flags', 'GET'),
        ('/api/leaderboard', 'GET'),
    ]
    
    for endpoint, method in endpoints_to_test:
        with patch('app.get_db_connection', return_value=DummyConnection()):
            if method == 'GET':
                resp = client.get(endpoint)
            elif method == 'POST':
                resp = client.post(endpoint, json={})
            
            # Should not be 404 - endpoint should exist
            assert resp.status_code != 404, f"Endpoint {endpoint} should exist, got {resp.status_code}"


def test_admin_endpoints_exist(client):
    """Test that all missing admin endpoints were added."""
    with mock_admin_auth():
        # Test create-lesson endpoint  
        # Create a smarter cursor that returns curriculum ID for the SELECT query
        from unittest.mock import Mock
        cursor_mock = Mock()
        cursor_mock.fetchone.return_value = (1,)  # Return curriculum ID
        cursor_mock.execute.return_value = None
        cursor_mock.close.return_value = None
        
        conn_mock = Mock()
        conn_mock.cursor.return_value = cursor_mock
        conn_mock.commit.return_value = None
        conn_mock.rollback.return_value = None
        conn_mock.close.return_value = None
        
        with patch('db_utils.get_db_connection', return_value=conn_mock):
            resp = client.post(
                '/api/admin/create-lesson',
                json={'curriculum': 'Math', 'unit': 'Algebra', 'lesson': 'Addition', 'grade': '4th Grade'},
                headers=get_admin_headers()
            )
            # Should not be 404 - endpoint exists (if 404, should be JSON, not HTML)
            if resp.status_code == 404:
                # If 404, it should be JSON (business logic) not HTML (missing endpoint)
                assert resp.is_json, f"Endpoint should exist - got HTML 404 instead of JSON response"
                json_resp = resp.get_json()
                assert 'status' in json_resp, "JSON 404 should have status field (business logic error)"
            else:
                # Endpoint exists and processed the request
                assert resp.status_code in [200, 201, 400, 404], f"Unexpected status code: {resp.status_code}"
                
        # Test update-topic endpoint  
        with patch('db_utils.get_db_connection', return_value=conn_mock):
            resp = client.put(
                '/api/admin/update-topic/1', 
                json={'name': 'New Name'}, 
                headers=get_admin_headers()
            )
            # Apply same intelligent check for update-topic endpoint
            if resp.status_code == 404:
                assert resp.is_json, f"update-topic endpoint should exist - got HTML 404 instead of JSON response"
                json_resp = resp.get_json()
                assert 'status' in json_resp, "JSON 404 should have status field (business logic error)"
            else:
                assert resp.status_code in [200, 201, 400, 404], f"Unexpected status code: {resp.status_code}"
            
        # Test delete-topic endpoint
        with patch('db_utils.get_db_connection', return_value=conn_mock):
            resp = client.delete('/api/admin/delete-topic/1', headers=get_admin_headers())
            if resp.status_code == 404:
                assert resp.is_json, f"delete-topic endpoint should exist - got HTML 404 instead of JSON response"
                json_resp = resp.get_json()
                assert 'status' in json_resp, "JSON 404 should have status field (business logic error)"
            else:
                assert resp.status_code in [200, 201, 400, 404], f"Unexpected status code: {resp.status_code}"
            
        # Test map-topic-curriculums endpoint
        with patch("db_utils.get_db_connection", return_value=conn_mock):
            resp = client.post(
                '/api/admin/map-topic-curriculums',
                json={'topic_id': 5, 'curriculum_ids': [1, 2]},
                headers=get_admin_headers()
            )
            assert resp.status_code != 404


def test_main_app_endpoints_exist(client):
    """Test that video, story, and other endpoints were moved to main app."""
    conn = DummyConnection("https://youtu.be/test")
    with patch("content.get_db_connection", return_value=conn):
        # Test video endpoint
        resp = client.get('/api/video/1')
        assert resp.status_code != 404
        
        # Test story endpoint  
        resp = client.get('/api/story/1')
        assert resp.status_code != 404
        
        # Test story-exists endpoint
        resp = client.get('/api/story-exists/1')
        assert resp.status_code != 404
        
        # Test quiz-exists endpoint
        resp = client.get('/api/quiz-exists/1')
        assert resp.status_code != 404


def test_subscription_endpoints_exist(client):
    """Test that subscription endpoints were added."""
    conn = DummyConnection()
    with patch("db_utils.get_db_connection", return_value=conn):
        # Test subscription-status endpoint
        resp = client.get('/api/subscription-status/1')
        # Should not be 404 - endpoint exists (may be 401 due to auth)
        assert resp.status_code != 404
        
        # Test cancel-subscription endpoint
        resp = client.post('/api/cancel-subscription/1')
        assert resp.status_code != 404
        
        # Test renew-subscription endpoint  
        resp = client.post('/api/renew-subscription/1')
        assert resp.status_code != 404


def test_dashboard_and_leaderboard_exist(client):
    """Test that dashboard and leaderboard endpoints were added."""
    conn = DummyConnection(("testuser",))
    with patch("db_utils.get_db_connection", return_value=conn):
        # Test dashboard endpoint
        resp = client.get('/api/dashboard/1')
        assert resp.status_code != 404
        
        # Test leaderboard endpoint
        resp = client.get('/api/leaderboard')
        assert resp.status_code != 404
        
        # Test curriculum-table endpoint
        resp = client.get('/api/curriculum-table')
        assert resp.status_code != 404


def test_flag_endpoints_exist(client):
    """Test that flag-related endpoints work."""
    conn = DummyConnection()
    with patch("db_utils.get_db_connection", return_value=conn):
        # Test flag-page-error endpoint
        resp = client.post('/api/flag-page-error', json={
            'pagePath': '/test', 
            'description': 'test error'
        })
        assert resp.status_code != 404
        
        # Test open-flags endpoint
        resp = client.get('/api/open-flags')
        assert resp.status_code != 404


def test_question_attempt_endpoint_exists(client):
    """Test that record-question-attempt endpoint was added."""
    conn = DummyConnection()
    with patch("db_utils.get_db_connection", return_value=conn):
        with patch('auth_utils.require_auth', lambda allowed_types: lambda f: f):
            resp = client.post('/api/record-question-attempt', json={
                'userId': 1,
                'questionId': 1, 
                'userAnswer': 'test',
                'isCorrect': True,
                'difficultyAtAttempt': 1
            }, headers=get_student_headers())
            assert resp.status_code != 404


def test_quiz_exists_has_status_field(client):
    """Test that quiz-exists returns status field (was missing causing KeyError)."""
    conn = DummyConnection(question_count=5)
    with patch("content.get_db_connection", return_value=conn):
        resp = client.get('/api/quiz-exists/123')
        assert resp.status_code == 200
        data = resp.get_json()
        # Should have success field (was missing before causing KeyError)
        assert 'success' in data
        assert data['success'] == True


def test_story_exists_has_isplaceholder_field(client):
    """Test that story-exists returns isPlaceholder field (was missing causing KeyError)."""
    conn = DummyConnection()
    with patch("content.get_db_connection", return_value=conn):
        resp = client.get('/api/story-exists/1')
        assert resp.status_code == 200
        data = resp.get_json()
        # Should have isPlaceholder field (was missing before)
        assert 'isPlaceholder' in data


def test_open_flags_returns_correct_format(client):
    """Test that open-flags returns object not list (was causing assertion failure)."""
    conn = DummyConnection()
    with patch("db_utils.get_db_connection", return_value=conn):
        resp = client.get('/api/open-flags')
        assert resp.status_code == 200
        data = resp.get_json()
        # Should return object, not list (was list before causing test failure)
        assert isinstance(data, dict)
        assert 'success' in data
        assert 'open_flags' in data


def test_create_curriculum_returns_201(client):
    """Test that create-curriculum returns 201 not 200."""
    with mock_admin_auth():
        conn = DummyConnection()
        with patch("db_utils.get_db_connection", return_value=conn):
            resp = client.post('/api/admin/create-curriculum', 
                             json={'name': 'History'}, 
                             headers=get_admin_headers())
            # Should return 201 for creation, not 200
            assert resp.status_code == 201


def test_record_question_attempt_validation(client):
    """Test that record-question-attempt properly validates fields."""
    conn = DummyConnection()
    with patch("db_utils.get_db_connection", return_value=conn):
        with patch('auth_utils.require_auth', lambda allowed_types: lambda f: f):
            # Test with missing userId (should be 400 not 201)
            resp = client.post('/api/record-question-attempt', json={
                'userId': None,
                'questionId': 1,
                'userAnswer': 'answer',
                'isCorrect': False,
                'difficultyAtAttempt': 2
            }, headers=get_student_headers())
            # Should return 400 for validation error, not 201
            assert resp.status_code == 400