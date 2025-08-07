import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

class DummyCursor:
    def __init__(self, question_row=None, answer_rows=None, step_rows=None, questions_by_diff=None):
        self.question_row = question_row
        self.answer_rows = answer_rows or []
        self.step_rows = step_rows or []
        self.questions_by_diff = questions_by_diff
        self.last_query = None
        self.last_params = None

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params

    def fetchone(self):
        if self.questions_by_diff is not None and self.last_params:
            diff = self.last_params[1]
            return self.questions_by_diff.get(diff)
        return self.question_row

    def fetchall(self):
        if self.last_query and 'tbl_answer' in self.last_query:
            return self.answer_rows
        if self.last_query and 'tbl_step' in self.last_query:
            return self.step_rows
        return []

    def close(self):
        pass


class DummyConnection:
    def __init__(self, question_row=None, answer_rows=None, step_rows=None, questions_by_diff=None):
        self.cursor_obj = DummyCursor(question_row, answer_rows, step_rows, questions_by_diff)

    def cursor(self, dictionary=False, cursor_factory=None):
        return self.cursor_obj

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_quiz_question_multiple_choice(client):
    question = (1, "What is 1+1?", "MultipleChoice", 3)
    answers = [("2", True), ("3", False)]
    steps = [("Add the numbers",), ("Check your work",)]
    conn = DummyConnection(question, answers, steps)
    with patch('quiz.get_db_connection', return_value=conn):
        resp = client.get('/api/quiz/question/1/1/3')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    q = data['question']
    assert q['id'] == 1
    assert q['text'] == "What is 1+1?"
    assert q['type'] == 'MultipleChoice'
    assert q['difficulty'] == 3
    expected_answers = [
        {"AnswerName": "2", "IsCorrect": True},
        {"AnswerName": "3", "IsCorrect": False},
    ]
    assert q['answers'] == expected_answers
    assert q['steps'] == [s[0] for s in steps]

def test_quiz_question_open_ended(client):
    question = (5, "Explain gravity", "OpenEnded", 2)
    answers = [("Because of mass", True)]
    conn = DummyConnection(question, answers)
    with patch('quiz.get_db_connection', return_value=conn):
        resp = client.get('/api/quiz/question/1/2/2')
    assert resp.status_code == 200
    data = resp.get_json()
    q = data['question']
    assert q['type'] == 'OpenEnded'
    expected_answers = [{"AnswerName": "Because of mass", "IsCorrect": True}]
    assert q['answers'] == expected_answers
    assert q['steps'] == []

def test_quiz_question_not_found(client):
    conn = DummyConnection(None, [])
    with patch('quiz.get_db_connection', return_value=conn):
        resp = client.get('/api/quiz/question/1/2/2')
    assert resp.status_code == 404
@pytest.mark.parametrize("input_diff,clamped", [(0, 1), (99, 5)])
def test_quiz_question_clamped_difficulty(client, input_diff, clamped):
    question = (42, "Clamped question", "MultipleChoice", clamped)
    answers = [("answer", True)]
    conn = DummyConnection(question, answers)
    with patch('quiz.get_db_connection', return_value=conn):
        resp = client.get(f'/api/quiz/question/1/1/{input_diff}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    q = data['question']
    assert q['difficulty'] == clamped


def test_quiz_question_fallback_to_easier(client):
    questions = {
        5: None,
        4: None,
        3: (7, "Easier question", "OpenEnded", 3)
    }
    conn = DummyConnection(questions_by_diff=questions)
    with patch('quiz.get_db_connection', return_value=conn):
        resp = client.get('/api/quiz/question/1/1/5')
    assert resp.status_code == 200
    data = resp.get_json()
    q = data['question']
    assert q['id'] == 7
    assert q['difficulty'] == 3
