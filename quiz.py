from flask import Blueprint, request, jsonify
import traceback
from db_utils import release_db_connection
# Make quiz.get_db_connection patchable via app.get_db_connection for tests
import app
def get_db_connection():
    return app.get_db_connection()

quiz_bp = Blueprint('quiz', __name__, url_prefix='/api')

@quiz_bp.route('/quiz/question/<int:user_id>/<int:topic_id>/<int:difficulty_level>', methods=['GET'])
def get_quiz_question(user_id, topic_id, difficulty_level):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        difficulty_level = max(1, min(5, difficulty_level))
        query = """
            SELECT Q.id, Q.questionname, Q.questiontype, Q.difficultyrating
            FROM tbl_question Q
            WHERE Q.topicid = %s AND Q.difficultyrating = %s
            ORDER BY RANDOM() LIMIT 1;
        """
        question = None
        # Try progressively easier difficulties until a question is found
        for diff in range(difficulty_level, 0, -1):
            cursor.execute(query, (topic_id, diff))
            question = cursor.fetchone()
            if question:
                difficulty_level = diff
                break
        if not question:
            return jsonify({"status": "error", "message": "No questions found for this topic."}), 404
        question_id = question[0]
        # Always fetch answers so that OpenEnded questions still return the
        # correct answer for display in the UI.  Convert the raw tuples into a
        # list of dictionaries matching the front-end's expected shape.
        cursor.execute(
            "SELECT answername, iscorrect FROM tbl_answer WHERE questionid = %s",
            (question_id,),
        )
        answers = [
            {"AnswerName": row[0], "IsCorrect": row[1]}
            for row in cursor.fetchall()
        ]

        cursor.execute(
            "SELECT stepname FROM tbl_step WHERE questionid = %s ORDER BY sequenceno",
            (question_id,),
        )
        steps = [row[0] for row in cursor.fetchall()]

        response_data = {
            "status": "success",
            "question": {
                "id": question[0],
                "text": question[1],
                "type": question[2],
                "difficulty": question[3],
                "answers": answers,
                "steps": steps,
            },
        }
        return jsonify(response_data), 200
    except Exception as e:
        print(f"Get Quiz Question API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching quiz question."}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@quiz_bp.route('/quiz/result', methods=['POST', 'OPTIONS'])
def record_quiz_result():
    """Record a user's quiz score."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    
    user_id = data.get('userId')
    topic_id = data.get('topicId')
    score = data.get('score')

    if None in (user_id, topic_id, score):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    try:
        score = int(score)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Score must be an integer between 0 and 100."}), 400

    if not 0 <= score <= 100:
        return jsonify({"status": "error", "message": "Score must be an integer between 0 and 100."}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tbl_quizscore (userid, topicid, score) VALUES (%s, %s, %s)",
            (user_id, topic_id, score),
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Score recorded."}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Record Quiz Result API Error: {e}")
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)
