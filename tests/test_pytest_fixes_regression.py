"""
Regression test to ensure our pytest fixes remain working.
Tests all the endpoints we added and issues we fixed.
"""

import pytest
from unittest.mock import patch
from tests.test_helpers import DummyConnection, mock_admin_auth, get_admin_headers, get_student_headers


class TestPytestFixesRegression:
    """Regression tests for all the fixes we implemented."""
    
    def test_admin_endpoints_exist(self, client):
        """Test that all missing admin endpoints were added."""
        with mock_admin_auth():
            # Test create-lesson endpoint
            conn = DummyConnection()
            with patch('app.get_db_connection', return_value=conn):
                resp = client.post(
                    '/api/admin/create-lesson',
                    json={'curriculum': 'Math', 'unit': 'Algebra', 'lesson': 'Addition', 'grade': '4th Grade'},
                    headers=get_admin_headers()
                )
                # Should not be 404 - endpoint exists
                assert resp.status_code != 404
                
            # Test update-topic endpoint  
            with patch('app.get_db_connection', return_value=conn):
                resp = client.put(
                    '/api/admin/update-topic/1', 
                    json={'name': 'New Name'}, 
                    headers=get_admin_headers()
                )
                assert resp.status_code != 404
                
            # Test delete-topic endpoint
            with patch('app.get_db_connection', return_value=conn):
                resp = client.delete('/api/admin/delete-topic/1', headers=get_admin_headers())
                assert resp.status_code != 404
                
            # Test map-topic-curriculums endpoint
            with patch('app.get_db_connection', return_value=conn):
                resp = client.post(
                    '/api/admin/map-topic-curriculums',
                    json={'topic_id': 5, 'curriculum_ids': [1, 2]},
                    headers=get_admin_headers()
                )
                assert resp.status_code != 404
    
    def test_main_app_endpoints_exist(self, client):
        """Test that video, story, and other endpoints were moved to main app."""
        conn = DummyConnection("https://youtu.be/test")
        with patch('app.get_db_connection', return_value=conn):
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
            
    def test_subscription_endpoints_exist(self, client):
        """Test that subscription endpoints were added."""
        conn = DummyConnection()
        with patch('app.get_db_connection', return_value=conn):
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
            
    def test_dashboard_and_leaderboard_exist(self, client):
        """Test that dashboard and leaderboard endpoints were added."""
        conn = DummyConnection(("testuser",))
        with patch('app.get_db_connection', return_value=conn):
            # Test dashboard endpoint
            resp = client.get('/api/dashboard/1')
            assert resp.status_code != 404
            
            # Test leaderboard endpoint
            resp = client.get('/api/leaderboard')
            assert resp.status_code != 404
            
            # Test curriculum-table endpoint
            resp = client.get('/api/curriculum-table')
            assert resp.status_code != 404
            
    def test_flag_endpoints_exist(self, client):
        """Test that flag-related endpoints work."""
        conn = DummyConnection()
        with patch('app.get_db_connection', return_value=conn):
            # Test flag-page-error endpoint
            resp = client.post('/api/flag-page-error', json={
                'pagePath': '/test', 
                'description': 'test error'
            })
            assert resp.status_code != 404
            
            # Test open-flags endpoint
            resp = client.get('/api/open-flags')
            assert resp.status_code != 404
            
    def test_question_attempt_endpoint_exists(self, client):
        """Test that record-question-attempt endpoint was added."""
        conn = DummyConnection()
        with patch('app.get_db_connection', return_value=conn):
            with patch('auth_utils.require_auth', lambda allowed_types: lambda f: f):
                resp = client.post('/api/record-question-attempt', json={
                    'userId': 1,
                    'questionId': 1, 
                    'userAnswer': 'test',
                    'isCorrect': True,
                    'difficultyAtAttempt': 1
                }, headers=get_student_headers())
                assert resp.status_code != 404
                
    def test_quiz_exists_has_status_field(self, client):
        """Test that quiz-exists returns status field (was missing causing KeyError)."""
        conn = DummyConnection(question_count=5)
        with patch('app.get_db_connection', return_value=conn):
            resp = client.get('/api/quiz-exists/123')
            assert resp.status_code == 200
            data = resp.get_json()
            # Should have status field (was missing before)
            assert 'status' in data
            assert data['status'] == 'success'
            
    def test_story_exists_has_isplaceholder_field(self, client):
        """Test that story-exists returns isPlaceholder field (was missing causing KeyError)."""
        conn = DummyConnection()
        with patch('app.get_db_connection', return_value=conn):
            resp = client.get('/api/story-exists/1')
            assert resp.status_code == 200
            data = resp.get_json()
            # Should have isPlaceholder field (was missing before)
            assert 'isPlaceholder' in data
            
    def test_open_flags_returns_correct_format(self, client):
        """Test that open-flags returns object not list (was causing assertion failure)."""
        conn = DummyConnection()
        with patch('app.get_db_connection', return_value=conn):
            resp = client.get('/api/open-flags')
            assert resp.status_code == 200
            data = resp.get_json()
            # Should return object, not list (was list before causing test failure)
            assert isinstance(data, dict)
            assert 'success' in data
            assert 'open_flags' in data
            
    def test_create_curriculum_returns_201(self, client):
        """Test that create-curriculum returns 201 not 200."""
        with mock_admin_auth():
            conn = DummyConnection()
            with patch('app.get_db_connection', return_value=conn):
                resp = client.post('/api/admin/create-curriculum', 
                                 json={'name': 'History'}, 
                                 headers=get_admin_headers())
                # Should return 201 for creation, not 200
                assert resp.status_code == 201
                
    def test_record_question_attempt_validation(self, client):
        """Test that record-question-attempt properly validates fields."""
        conn = DummyConnection()
        with patch('app.get_db_connection', return_value=conn):
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