#!/usr/bin/env python3
"""
Test the quiz-exists endpoint to ensure it correctly identifies quiz availability.
"""

import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyCursor:
    def __init__(self, question_count=0):
        self.question_count = question_count

    def execute(self, query, params=None):
        self.query = query
        self.params = params

    def fetchone(self):
        return (self.question_count,)

    def close(self):
        pass


class DummyConnection:
    def __init__(self, question_count=0):
        self.cursor_obj = DummyCursor(question_count)

    def cursor(self, cursor_factory=None):
        return self.cursor_obj

    def close(self):
        pass


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_quiz_exists_with_questions(client):
    """Test quiz-exists endpoint when questions exist for the topic."""
    conn = DummyConnection(question_count=5)  # 5 questions exist
    with patch("app.get_db_connection", return_value=conn):
        resp = client.get("/api/quiz-exists/123")
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["quizExists"] == True
    
    # Verify the correct query was executed
    assert "SELECT COUNT(*) FROM tbl_question WHERE topicid = %s" in conn.cursor_obj.query
    assert conn.cursor_obj.params == (123,)


def test_quiz_exists_no_questions(client):
    """Test quiz-exists endpoint when no questions exist for the topic."""
    conn = DummyConnection(question_count=0)  # No questions exist
    with patch("app.get_db_connection", return_value=conn):
        resp = client.get("/api/quiz-exists/456")
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["quizExists"] == False
    
    # Verify the correct query was executed
    assert "SELECT COUNT(*) FROM tbl_question WHERE topicid = %s" in conn.cursor_obj.query
    assert conn.cursor_obj.params == (456,)


def test_quiz_exists_database_error(client):
    """Test quiz-exists endpoint when database error occurs."""
    def raise_exception(*args, **kwargs):
        raise Exception("Database connection failed")
    
    with patch("app.get_db_connection", side_effect=raise_exception):
        resp = client.get("/api/quiz-exists/789")
    
    assert resp.status_code == 500
    data = resp.get_json()
    assert data["status"] == "error"
    assert data["message"] == "Internal error checking quiz availability."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])