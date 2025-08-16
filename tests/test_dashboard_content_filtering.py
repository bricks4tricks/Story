#!/usr/bin/env python3
"""
Test the enhanced dashboard content filtering functionality.
Tests the JavaScript logic that only shows available content.
"""

import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_dashboard_html_loads(client):
    """Test that the dashboard HTML loads correctly."""
    resp = client.get("/dashboard.html")
    assert resp.status_code == 200
    
    # Check that the HTML contains the new content filtering functions
    html_content = resp.get_data(as_text=True)
    
    # Verify key JavaScript functions are present
    assert "checkStoryExists" in html_content
    assert "checkQuizExists" in html_content
    assert "checkVideoExists" in html_content
    assert "checkCurriculumHasContent" in html_content
    assert "checkUnitHasContent" in html_content
    
    # Verify the enhanced renderTopicsList function
    assert "renderTopicsList = async ()" in html_content
    assert "Promise.all([" in html_content
    assert "checkStoryExists(topic.id)" in html_content
    assert "checkQuizExists(topic.id)" in html_content
    assert "checkVideoExists(topic.id)" in html_content
    
    # Verify loading states and messaging
    assert "Loading topics..." in html_content
    assert "No topics with available content found for this unit." in html_content
    assert "No curriculums with available content found for this grade." in html_content
    assert "No units with available content found for this curriculum." in html_content


def test_dashboard_api_endpoints_referenced(client):
    """Test that the dashboard references the correct API endpoints."""
    resp = client.get("/dashboard.html")
    assert resp.status_code == 200
    
    html_content = resp.get_data(as_text=True)
    
    # Verify the new quiz-exists endpoint is referenced
    assert "/api/quiz-exists/" in html_content
    
    # Verify existing endpoints are still referenced
    assert "/api/story-exists/" in html_content
    assert "/api/video/" in html_content
    assert "/api/curriculum" in html_content


def test_dashboard_button_conditional_rendering(client):
    """Test that the dashboard conditionally renders buttons based on content."""
    resp = client.get("/dashboard.html")
    assert resp.status_code == 200
    
    html_content = resp.get_data(as_text=True)
    
    # Verify conditional button rendering logic
    assert "if (storyExists)" in html_content
    assert "if (quizExists)" in html_content 
    assert "if (videoExists)" in html_content
    assert "start-story-btn" in html_content
    assert "start-quiz-btn" in html_content
    assert "watch-video-btn" in html_content
    
    # Verify that buttons are only added when content exists
    assert "buttonsHTML += " in html_content


def test_dashboard_content_skip_logic(client):
    """Test that topics without content are skipped."""
    resp = client.get("/dashboard.html")
    assert resp.status_code == 200
    
    html_content = resp.get_data(as_text=True)
    
    # Verify logic to skip topics without any content
    assert "if (!storyExists && !quizExists && !videoExists)" in html_content
    assert "continue; // Skip this topic if no content is available" in html_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])