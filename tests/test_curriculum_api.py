#!/usr/bin/env python3
"""
Test the curriculum API endpoint that the dashboard uses.
"""

import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


class DummyCursor:
    def __init__(self, rows=None):
        self.rows = rows or []

    def execute(self, query, params=None):
        self.query = query
        self.params = params

    def fetchall(self):
        return self.rows

    def close(self):
        pass


class DummyConnection:
    def __init__(self, rows=None):
        self.cursor_obj = DummyCursor(rows)

    def cursor(self, cursor_factory=None):
        return self.cursor_obj

    def close(self):
        pass


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_curriculum_api_structure(client):
    """Test that the curriculum API returns the expected structure."""
    sample_rows = [
        {
            'gradename': '4th Grade',
            'curriculumtype': 'Math',
            'unitname': 'Addition',
            'topicname': 'Basic Addition',
            'topicid': 1,
            'availablethemes': 'Space,Ocean',
            'defaulttheme': 'Space'
        },
        {
            'gradename': '4th Grade',
            'curriculumtype': 'Math',
            'unitname': 'Subtraction',
            'topicname': 'Basic Subtraction',
            'topicid': 2,
            'availablethemes': 'Forest',
            'defaulttheme': 'Forest'
        },
        {
            'gradename': '5th Grade',
            'curriculumtype': 'Science',
            'unitname': 'Biology',
            'topicname': 'Cells',
            'topicid': 3,
            'availablethemes': 'Laboratory',
            'defaulttheme': 'Laboratory'
        }
    ]
    
    conn = DummyConnection(sample_rows)
    with patch("app.get_db_connection", return_value=conn):
        resp = client.get("/api/curriculum")
    
    assert resp.status_code == 200
    data = resp.get_json()
    
    # Verify the hierarchical structure: Grade > Curriculum > Unit > Topics
    assert "4th Grade" in data
    assert "5th Grade" in data
    
    # Check 4th Grade structure
    grade_4 = data["4th Grade"]
    assert "curriculums" in grade_4
    assert "Math" in grade_4["curriculums"]
    
    math_curriculum = grade_4["curriculums"]["Math"]
    assert "units" in math_curriculum
    assert "Addition" in math_curriculum["units"]
    assert "Subtraction" in math_curriculum["units"]
    
    # Check topic details
    addition_topics = math_curriculum["units"]["Addition"]
    assert len(addition_topics) == 1
    assert addition_topics[0]["name"] == "Basic Addition"
    assert addition_topics[0]["id"] == 1
    assert addition_topics[0]["availableThemes"] == ["Space", "Ocean"]
    assert addition_topics[0]["defaultTheme"] == "Space"
    
    # Check 5th Grade structure
    grade_5 = data["5th Grade"]
    assert "Science" in grade_5["curriculums"]


def test_curriculum_api_empty_result(client):
    """Test curriculum API with no data."""
    conn = DummyConnection([])  # No rows
    with patch("app.get_db_connection", return_value=conn):
        resp = client.get("/api/curriculum")
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == {}


def test_curriculum_api_database_error(client):
    """Test curriculum API when database error occurs."""
    def raise_exception(*args, **kwargs):
        raise Exception("Database connection failed")
    
    with patch("app.get_db_connection", side_effect=raise_exception):
        resp = client.get("/api/curriculum")
    
    assert resp.status_code == 500
    data = resp.get_json()
    assert data["status"] == "error"
    assert "database connection failed" in data["message"].lower()


def test_curriculum_api_query_structure(client):
    """Test that the curriculum API executes the expected query."""
    conn = DummyConnection([])
    with patch("app.get_db_connection", return_value=conn):
        resp = client.get("/api/curriculum")
    
    # Verify the query includes the expected tables and joins
    query = conn.cursor_obj.query
    assert "tbl_topic topic" in query
    assert "tbl_topic unit" in query
    assert "tbl_subject s" in query
    assert "tbl_topicgrade tg" in query
    assert "tbl_grade g" in query
    assert "JOIN" in query
    assert "GROUP BY" in query
    assert "ORDER BY" in query


if __name__ == "__main__":
    pytest.main([__file__, "-v"])