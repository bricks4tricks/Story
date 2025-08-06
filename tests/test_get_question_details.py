import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self, question_row, topic_row):
        self.question_row = question_row
        self.topic_row = topic_row
        self.last_query = ""
        self.executed = []

    def execute(self, query, params=None):
        self.last_query = query
        self.executed.append((query, params))

    def fetchone(self):
        if "FROM tbl_question" in self.last_query:
            return self.question_row
        if "FROM tbl_topic" in self.last_query:
            return self.topic_row
        return None

    def fetchall(self):
        if "FROM tbl_answer" in self.last_query:
            return [{"answername": "A1", "iscorrect": True}]
        if "FROM tbl_step" in self.last_query:
            return [{"stepname": "S1"}]
        return []

    def close(self):
        pass

class DummyConnection:
    def __init__(self, cursor):
        self.cursor_obj = cursor

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
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

@pytest.mark.parametrize("key", ["topicid", "TopicID"])
def test_get_question_details_handles_topicid_variants(client, key):
    question_row = {
        "id": 1,
        key: 42,
        "questionname": "Sample question",
        "questiontype": 1,
        "difficultyrating": 3,
    }
    topic_row = {
        "topicid": 42,
        "TopicName": "Algebra",
        "UnitName": "Unit",
        "CurriculumType": "Math",
    }
    cursor = DummyCursor(question_row, topic_row)
    conn = DummyConnection(cursor)

    with patch("app.get_db_connection", return_value=conn):
        resp = client.get("/api/admin/question/1")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["TopicID"] == 42
    # Verify the topic query received the correct topic ID
    assert cursor.executed[3][1] == (42,)
