import psycopg2
import psycopg2.extras
from psycopg2 import sql
from flask import Flask, jsonify, request, render_template, send_from_directory, redirect, url_for
from flask_cors import CORS
from extensions import bcrypt
import secrets
from datetime import datetime, timedelta
from version_cache import update_users_version
import traceback
import json
import random
import os  # Import os module to access environment variables
from utils import validate_password

# ---------------------------------
# --- NEW IMPORTS FOR EMAIL ---
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# --- END NEW IMPORTS ---

# =================================================================
#  1. SETUP & CONFIGURATION
# =================================================================
app = Flask(__name__)
bcrypt.init_app(app)
# Configure Flask-CORS to allow requests from your frontend domain
# It's crucial to specify the exact origin of your frontend.
# If your frontend is hosted at 'https://www.logicandstories.com', use that.
# If it's just 'https://logicandstories.com', use that. Be precise.
# Also, ensure methods and headers are allowed for preflight.
CORS(app, origins=["https://logicandstories.com", "https://www.logicandstories.com"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     headers=["Content-Type", "Authorization"])


# --- DATABASE CONFIGURATION ---
# Moved to db_utils for reuse across scripts
from db_utils import get_db_connection, release_db_connection
from auth import auth_bp
from admin import admin_bp
from quiz import quiz_bp
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(quiz_bp)



@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


# Define a mapping for questiontype (if using integer in DB)
QUESTION_TYPE_MAP = {
    'MultipleChoice': 1,
    'OpenEnded': 2
}
QUESTION_TYPE_REVERSE_MAP = {
    1: 'MultipleChoice',
    2: 'OpenEnded'
}





@app.route('/api/admin/edit-user/<int:user_id>', methods=['PUT', 'OPTIONS'])
def edit_user(user_id):
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    user_type = data.get('userType')

    if not all([username, email, user_type]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            "SELECT id FROM tbl_user WHERE (username = %s OR email = %s) AND id != %s",
            (username, email, user_id)
        )
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "username or email is already in use by another account."}), 409

        cursor.execute(
            "UPDATE tbl_user SET username = %s, email = %s, usertype = %s WHERE id = %s",
            (username, email, user_type, user_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "User not found or no changes made."}), 404

        conn.commit()
        update_users_version()

        return jsonify({"status": "success", "message": "User updated successfully!"}), 200
    except Exception as e:
        print(f"Edit User API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/admin/delete-user/<int:user_id>', methods=['DELETE', 'OPTIONS'])
def delete_user(user_id):
    if request.method == 'OPTIONS': return jsonify(success=True)
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT usertype FROM tbl_user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "message": "User not found."}), 404

        user_type = user[0] # Access by index as cursor is not dictionary=True here

        if user_type == 'Admin':
            return jsonify({"status": "error", "message": "Admin accounts cannot be deleted."}), 403

        if user_type == 'Parent':
            cursor.execute("SELECT id FROM tbl_user WHERE parentuserid = %s", (user_id,))
            if cursor.fetchone():
                return jsonify({"status": "error", "message": "Cannot delete a parent with student accounts. Please delete the student profiles first."}), 409

        # Remove any subscription rows referencing this user first to avoid
        # foreign key violations when deleting from ``tbl_user``.
        cursor.execute("DELETE FROM tbl_subscription WHERE user_id = %s", (user_id,))

        cursor.execute("DELETE FROM tbl_user WHERE id = %s", (user_id,))
        conn.commit()
        update_users_version()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "User not found or already deleted."}), 404

        return jsonify({"status": "success", "message": "User deleted successfully."}), 200

    except psycopg2.Error as err:
        print(f"Delete User DB Error: {err}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Database error during deletion."}), 500
    except Exception as e:
        print(f"Delete User API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal server error."}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/topics-list', methods=['GET'])
def get_topics_list():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT
                t.id,
                t.TopicName,
                unit.TopicName AS UnitName,
                s.SubjectName AS CurriculumType,
                (SELECT th.themename FROM tbl_topictheme tth JOIN tbl_theme th ON tth.themeid = th.id WHERE tth.topicid = t.id AND tth.isdefault = TRUE LIMIT 1) AS DefaultTheme
            FROM tbl_topic t
            JOIN tbl_topic unit ON t.parenttopicid = unit.id
            JOIN tbl_subject s ON unit.subjectid = s.id
            ORDER BY s.SubjectName, unit.TopicName, t.TopicName;
        """
        cursor.execute(query)
        topics = cursor.fetchall()
        return jsonify(topics)
    except Exception as e:
        print(f"Get Topics List API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/admin/add-question', methods=['POST', 'OPTIONS'])
def add_question():
    if request.method == 'OPTIONS': return jsonify(success=True)

    data = request.get_json()
    topic_id = data.get('topicId')
    question_text = data.get('questionText')
    question_type_str = data.get('questionType')
    answers = data.get('answers')
    steps = data.get('steps')
    difficulty_rating = data.get('difficultyRating', 3)

    if not all([topic_id, question_text, question_type_str, answers, steps]):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    try:
        difficulty_rating = int(difficulty_rating)
        if not (1 <= difficulty_rating <= 5):
            return jsonify({"status": "error", "message": "Difficulty rating must be between 1 and 5."}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid difficulty rating."}), 400


    question_type_to_insert = question_type_str

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        conn.autocommit = False

        question_query = (
            "INSERT INTO tbl_question (topicid, questionname, questiontype, difficultyrating, createdby) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id"
        )
        cursor.execute(
            question_query,
            (topic_id, question_text, question_type_to_insert, difficulty_rating, 'Admin'),
        )
        question_id = cursor.fetchone()[0]

        answer_query = "INSERT INTO tbl_answer (questionid, answername, iscorrect, createdby) VALUES (%s, %s, %s, %s)"
        answer_values = []
        for ans in answers:
            if 'text' not in ans or 'isCorrect' not in ans:
                raise ValueError("Each answer must have 'text' and 'isCorrect' fields.")
            answer_values.append((question_id, ans['text'], ans['isCorrect'], 'Admin'))
        cursor.executemany(answer_query, answer_values)

        step_query = "INSERT INTO tbl_step (questionid, sequenceno, stepname, createdby) VALUES (%s, %s, %s, %s)"
        step_values = []
        for idx, step in enumerate(steps):
            if 'text' not in step:
                 raise ValueError("Each step must have a 'text' field.")
            step_values.append((question_id, idx + 1, step['text'], 'Admin'))
        cursor.executemany(step_query, step_values)

        conn.commit()
        return jsonify({"status": "success", "message": f"Successfully added question (id {question_id})."}), 201
    except Exception as e:
        if conn: conn.rollback()
        print(f"Add Question API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An unexpected error occurred."}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/admin/questions', methods=['GET'])
def get_all_questions():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT
                q.id AS id,
                q.questionname AS questionname,
                q.questiontype AS questiontype,
                q.difficultyrating AS difficultyrating,
                t.TopicName AS topicname,
                unit.TopicName AS unitname
            FROM tbl_question q
            JOIN tbl_topic t ON q.topicid = t.id
            JOIN tbl_topic unit ON t.parenttopicid = unit.id
            ORDER BY q.id DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        questions = []
        for row in rows:
            questions.append({
                'ID': row['id'],
                'QuestionName': row['questionname'],
                'QuestionType': row['questiontype'],
                'DifficultyRating': row['difficultyrating'],
                'TopicName': row['topicname'],
                'UnitName': row['unitname']
            })
        return jsonify(questions)
    except Exception as e:
        print(f"Get All Questions API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/admin/question/<int:question_id>', methods=['GET'])
def get_question_details(question_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT id, topicid, questionname, questiontype, difficultyrating FROM tbl_question WHERE id = %s", (question_id,))
        question = cursor.fetchone()
        if not question:
            return jsonify({"status": "error", "message": "Question not found."}), 404

        question_type_display = question.get('questiontype') or question.get('questiontype')

        cursor.execute("SELECT answername, iscorrect FROM tbl_answer WHERE questionid = %s", (question_id,))
        answers = cursor.fetchall()

        cursor.execute("SELECT stepname FROM tbl_step WHERE questionid = %s ORDER BY sequenceno", (question_id,))
        steps = cursor.fetchall()

        topic_id = question.get('topicid') or question.get('topicid')
        cursor.execute(
            """
            SELECT
                t.id AS topicid,
                t.TopicName,
                unit.TopicName AS UnitName,
                s.SubjectName AS CurriculumType
            FROM tbl_topic t
            JOIN tbl_topic unit ON t.parenttopicid = unit.id
            JOIN tbl_subject s ON unit.subjectid = s.id
            WHERE t.id = %s
            """,
            (topic_id,),
        )
        topic_info = cursor.fetchone()

        question_details = {
            "ID": question.get('id'),
            "TopicID": question.get('topicid'),
            "TopicName": topic_info.get('TopicName') if topic_info else None,
            "UnitName": topic_info.get('UnitName') if topic_info else None,
            "CurriculumType": topic_info.get('CurriculumType') if topic_info else None,
            "QuestionName": question.get('questionname'),
            "QuestionType": question_type_display,
            "DifficultyRating": question.get('difficultyrating'),
            "Answers": [{
                'AnswerName': a.get('answername'),
                'IsCorrect': a.get('iscorrect')
            } for a in answers],
            "Steps": [s.get('stepname') for s in steps]
        }

        return jsonify(question_details), 200

    except Exception as e:
        print(f"Get Question Details API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching question details."}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/admin/edit-question/<int:question_id>', methods=['PUT', 'OPTIONS'])
def edit_question(question_id):
    if request.method == 'OPTIONS': return jsonify(success=True)

    data = request.get_json()
    payload_question_id = data.get('questionId')
    if payload_question_id and payload_question_id != question_id:
        return jsonify({"status": "error", "message": "Mismatched question id in URL and payload."}), 400

    topic_id = data.get('topicId')
    question_text = data.get('questionText')
    question_type_str = data.get('questionType')
    answers = data.get('answers')
    steps = data.get('steps')
    difficulty_rating = data.get('difficultyRating', 3)

    if not all([topic_id, question_text, question_type_str, answers, steps]):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    try:
        difficulty_rating = int(difficulty_rating)
        if not (1 <= difficulty_rating <= 5):
            return jsonify({"status": "error", "message": "Difficulty rating must be between 1 and 5."}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid difficulty rating."}), 400


    question_type_to_update = question_type_str

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        conn.autocommit = False

        question_update_query = "UPDATE tbl_question SET topicid = %s, questionname = %s, questiontype = %s, difficultyrating = %s, lastupdatedon = NOW(), lastupdatedby = %s WHERE id = %s"
        cursor.execute(question_update_query, (topic_id, question_text, question_type_to_update, difficulty_rating, 'Admin', question_id))

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"status": "error", "message": "Question not found or no changes made."}), 404

        cursor.execute("DELETE FROM tbl_answer WHERE questionid = %s", (question_id,))
        cursor.execute("DELETE FROM tbl_step WHERE questionid = %s", (question_id,))

        answer_query = "INSERT INTO tbl_answer (questionid, answername, iscorrect, createdby) VALUES (%s, %s, %s, %s)"
        answer_values = []
        for ans in answers:
            if 'text' not in ans or 'isCorrect' not in ans:
                raise ValueError("Each answer must have 'text' and 'isCorrect' fields.")
            answer_values.append((question_id, ans['text'], ans['isCorrect'], 'Admin'))
        if answer_values:
            cursor.executemany(answer_query, answer_values)

        step_query = "INSERT INTO tbl_step (questionid, sequenceno, stepname, createdby) VALUES (%s, %s, %s, %s)"
        step_values = []
        for idx, step in enumerate(steps):
            if 'text' not in step:
                 raise ValueError("Each step must have a 'text' field.")
            step_values.append((question_id, idx + 1, step['text'], 'Admin'))
        cursor.executemany(step_query, step_values)

        conn.commit()

        return jsonify({"status": "success", "message": f"Question id {question_id} updated successfully!"}), 200

    except Exception as e:
        if conn: conn.rollback()
        print(f"Edit Question API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An unexpected error occurred during question update."}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/delete-question/<int:question_id>', methods=['DELETE', 'OPTIONS'])
def delete_question(question_id):
    if request.method == 'OPTIONS': return jsonify(success=True)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        conn.autocommit = False

        cursor.execute("DELETE FROM tbl_step WHERE questionid = %s", (question_id,))
        cursor.execute("DELETE FROM tbl_answer WHERE questionid = %s", (question_id,))
        cursor.execute("DELETE FROM tbl_question WHERE id = %s", (question_id,))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Question not found or already deleted."}), 404

        return jsonify({"status": "success", "message": "Question and its related data deleted successfully."}), 200

    except psycopg2.Error as err:
        if conn: conn.rollback()
        print(f"Delete Question DB Error: {err}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Database error during deletion: {err}"}), 500
    except Exception as e:
        if conn: conn.rollback()
        print(f"Delete Question API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal server error during deletion."}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/stories', methods=['GET'])
def get_all_stories():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT DISTINCT
                t.id AS topicid,
                t.TopicName AS topicname,
                (
                    SELECT th.themename
                    FROM tbl_topictheme tth
                    JOIN tbl_theme th ON tth.themeid = th.id
                    WHERE tth.topicid = t.id AND tth.isdefault = TRUE
                    LIMIT 1
                ) AS defaulttheme
            FROM tbl_description td
            JOIN tbl_topic t ON td.topicid = t.id
            ORDER BY t.TopicName;
        """
        cursor.execute(query)
        stories_raw = cursor.fetchall()

        stories = []
        for row in stories_raw:
            stories.append({
                'topicid': row['topicid'],
                'TopicName': row['topicname'],
                'DefaultTheme': row['defaulttheme']
            })

        return jsonify(stories)
    except Exception as e:
        print(f"Get All Stories API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/admin/delete-story/<int:topic_id>', methods=['DELETE', 'OPTIONS'])
def delete_story(topic_id):
    if request.method == 'OPTIONS': return jsonify(success=True)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        conn.autocommit = False

        # Delete from tbl_topictheme first
        cursor.execute("DELETE FROM tbl_topictheme WHERE topicid = %s", (topic_id,))

        cursor.execute("SELECT interactiveelementid FROM tbl_description WHERE topicid = %s AND interactiveelementid IS NOT NULL", (topic_id,))
        interactive_element_ids_to_delete = [row[0] for row in cursor.fetchall()]

        if interactive_element_ids_to_delete:
            placeholders = sql.SQL(',').join(sql.Placeholder() * len(interactive_element_ids_to_delete))
            delete_query = sql.SQL("DELETE FROM tbl_interactiveelement WHERE id IN ({})").format(placeholders)
            cursor.execute(delete_query, tuple(interactive_element_ids_to_delete))

        cursor.execute("DELETE FROM tbl_description WHERE topicid = %s", (topic_id,))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Story not found for this topic or already deleted."}), 404

        return jsonify({"status": "success", "message": f"Story for topic id {topic_id} and its associated interactive elements deleted successfully."}), 200

    except psycopg2.Error as err:
        if conn: conn.rollback()
        print(f"Delete Story DB Error: {err}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Database error during deletion: {err}"}), 500
    except Exception as e:
        if conn: conn.rollback()
        print(f"Delete Story API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal server error during deletion."}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/save-story', methods=['POST', 'OPTIONS'])
def save_story():
    if request.method == 'OPTIONS': return jsonify(success=True)

    data = request.get_json()
    topic_id = data.get('topicId')
    story_sections = data.get('storySections')
    default_theme_name = data.get('defaultTheme')

    if not topic_id or story_sections is None:
        return jsonify({"status": "error", "message": "Missing topic id or story sections."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        conn.autocommit = False

        # Delete existing interactive elements and descriptions for this topic
        cursor.execute("SELECT interactiveelementid FROM tbl_description WHERE topicid = %s AND interactiveelementid IS NOT NULL", (topic_id,))
        interactive_element_ids_to_delete = [row[0] for row in cursor.fetchall()]

        if interactive_element_ids_to_delete:
            placeholders = sql.SQL(',').join(sql.Placeholder() * len(interactive_element_ids_to_delete))
            delete_query = sql.SQL("DELETE FROM tbl_interactiveelement WHERE id IN ({})").format(placeholders)
            cursor.execute(delete_query, tuple(interactive_element_ids_to_delete))

        cursor.execute("DELETE FROM tbl_description WHERE topicid = %s", (topic_id,))

        # Handle tbl_topictheme updates
        # First, clear existing themes for this topic
        cursor.execute("DELETE FROM tbl_topictheme WHERE topicid = %s", (topic_id,))

        # Then, insert all themes as available for this topic, and mark the selected one as default
        cursor.execute("SELECT id, themename FROM tbl_theme")
        all_themes = cursor.fetchall()

        for theme_id, theme_name in all_themes:
            is_default = (theme_name == default_theme_name)
            cursor.execute(
                "INSERT INTO tbl_topictheme (topicid, themeid, isdefault, createdby) VALUES (%s, %s, %s, %s)",
                (topic_id, theme_id, is_default, 'Admin')
            )


        for i, section in enumerate(story_sections):
            section_name = section.get('sectionName')
            content_type = section.get('contentType')
            content = section.get('content')
            order = i + 1

            if not section_name or not content_type:
                conn.rollback()
                return jsonify({"status": "error", "message": f"Section {order} is incomplete (missing name or type)."}, 400)

            interactive_element_id_for_db = None
            description_text_for_db = None

            if content_type == 'Paragraph':
                description_text_for_db = content
                if not description_text_for_db:
                    conn.rollback()
                    return jsonify({"status": "error", "message": f"Paragraph in Section '{section_name}' has no text."}), 400
            elif content_type == 'Interactive':
                interactive_data = content
                element_type = interactive_data.get('elementType')
                configuration = interactive_data.get('configuration')

                if not element_type or not isinstance(configuration, dict):
                    conn.rollback()
                    return jsonify({"status": "error", "message": f"Interactive element in Section '{section_name}' is incomplete (missing element type or invalid configuration)."}, 400)

                interactive_query = (
                    "INSERT INTO tbl_interactiveelement (elementtype, configuration, createdby) "
                    "VALUES (%s, %s, %s) RETURNING id"
                )
                cursor.execute(
                    interactive_query,
                    (element_type, json.dumps(configuration), 'Admin'),
                )
                interactive_element_id_for_db = cursor.fetchone()[0]
            else:
                conn.rollback()
                return jsonify({"status": "error", "message": f"Section {order} has an invalid content type: {content_type}"}), 400

            desc_query = "INSERT INTO tbl_description (topicid, sectionname, descriptiontext, interactiveelementid, descriptionorder, contenttype, createdby) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(desc_query, (topic_id, section_name, description_text_for_db, interactive_element_id_for_db, order, content_type, 'Admin'))

        conn.commit()
        return jsonify({"status": "success", "message": f"Story for topic {topic_id} saved successfully."}), 201

    except psycopg2.Error as err:
        if conn: conn.rollback()
        print(f"Save Story DB Error: {err}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "A database error occurred while saving the story."}), 500
    except Exception as e:
        if conn: conn.rollback()
        print(f"Save Story API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An unexpected server error occurred."}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/story/<int:topic_id>', methods=['GET'])
def get_story_for_topic(topic_id):
    conn = None
    story_payload = {"sections": [], "defaultTheme": None, "availableThemes": []}
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        def _get_case_insensitive(row, key):
            """Return value for key in row ignoring case differences."""
            for k, v in row.items():
                if k.lower() == key.lower():
                    return v
            return None

        # Fetch the default theme for this topic
        cursor.execute("""
            SELECT th.themename
            FROM tbl_topictheme tth
            JOIN tbl_theme th ON tth.themeid = th.id
            WHERE tth.topicid = %s AND tth.isdefault = TRUE
            LIMIT 1
        """, (topic_id,))
        default_theme_row = cursor.fetchone()
        if default_theme_row:
            story_payload["defaultTheme"] = _get_case_insensitive(
                default_theme_row, "themename"
            )

        # Fetch all available themes for this topic
        cursor.execute("""
            SELECT th.themename
            FROM tbl_topictheme tth
            JOIN tbl_theme th ON tth.themeid = th.id
            WHERE tth.topicid = %s
            ORDER BY th.themename
        """, (topic_id,))
        available_themes_rows = cursor.fetchall()
        story_payload["availableThemes"] = [
            _get_case_insensitive(row, "themename")
            for row in available_themes_rows
        ]


        cursor.execute("SELECT id, sectionname, descriptiontext, interactiveelementid, descriptionorder, contenttype FROM tbl_description WHERE topicid = %s ORDER BY descriptionorder", (topic_id,))
        sections = cursor.fetchall()

        if not sections:
            # Return a placeholder story when no sections are found
            story_payload["sections"].append(
                {
                    "sectionName": "Coming Soon",
                    "order": 1,
                    "contentType": "Paragraph",
                    "content": "Story coming soon.",
                }
            )
            return jsonify(story_payload)


        for section in sections:
            section_data = {
                "sectionName": section.get('sectionname') or section.get('sectionname'),
                "order": section.get('descriptionorder') or section.get('descriptionorder'),
                "contentType": section.get('contenttype') or section.get('contenttype'),
            }

            if section.get('interactiveelementid') or section.get('interactiveelementid'):
                interactive_id = section.get('interactiveelementid') or section.get('interactiveelementid')
                cursor.execute(
                    "SELECT elementtype, configuration FROM tbl_interactiveelement WHERE id = %s",
                    (interactive_id,)
                )
                interactive_row = cursor.fetchone()

                if interactive_row:
                    section_data['contentType'] = 'Interactive'
                    config_data = {}
                    if interactive_row.get('configuration') or interactive_row.get('configuration'):
                        try:
                            config_data = json.loads(
                                interactive_row.get('configuration')
                                or interactive_row.get('configuration')
                            )
                        except Exception as json_err:
                            print(
                                f"JSON decode error for interactive element {interactive_id}: {json_err}"
                            )
                    section_data['content'] = {
                        "elementType": interactive_row.get('elementtype')
                        or interactive_row.get('elementtype'),
                        "configuration": config_data,
                    }
                else:
                    section_data['contentType'] = 'Paragraph'
                    section_data['content'] = section.get('descriptiontext') or section.get('descriptiontext')
            else:
                section_data['contentType'] = 'Paragraph'
                section_data['content'] = section.get('descriptiontext') or section.get('descriptiontext')

            story_payload["sections"].append(section_data)

        return jsonify(story_payload)

    except Exception as e:
        print(f"Get Story API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/story-exists/<int:topic_id>', methods=['GET'])
def story_exists(topic_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM tbl_description WHERE topicid = %s", (topic_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            return jsonify({"status": "success", "storyExists": True, "isPlaceholder": False}), 200
        else:
            # When no story sections exist, indicate a placeholder will be used
            return jsonify({"status": "success", "storyExists": False, "isPlaceholder": True}), 200

    except Exception as e:
        print(f"Story Exists API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error checking story availability."}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/progress/<int:user_id>', methods=['GET'])
def get_user_progress(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT up.topicid, up.status, t.TopicName, unit.TopicName AS UnitName, s.SubjectName AS CurriculumType
            FROM tbl_userprogress up
            JOIN tbl_topic t ON up.topicid = t.id
            JOIN tbl_topic unit ON t.parenttopicid = unit.id
            JOIN tbl_subject s ON unit.subjectid = s.id
            WHERE up.userid = %s
        """
        cursor.execute(query, (user_id,))
        progress = cursor.fetchall()
        return jsonify(progress)
    except Exception as e:
        print(f"Get Progress API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/progress/update', methods=['POST'])
def update_user_progress():
    data = request.get_json()
    user_id = data.get('userId')
    topic_id = data.get('topicId')
    status = data.get('status')

    if not all([user_id, topic_id, status]):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO tbl_userprogress (userid, topicid, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (userid, topicid)
            DO UPDATE SET status = EXCLUDED.status;
        """
        cursor.execute(query, (user_id, topic_id, status))
        conn.commit()

        return jsonify({"status": "success", "message": "Progress updated."}), 200
    except Exception as e:
        print(f"Update Progress API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/quiz/result', methods=['POST', 'OPTIONS'])
def record_quiz_result():
    """Record a user's quiz score."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    data = request.get_json()
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tbl_quizscore (userid, topicid, score, takenon) VALUES (%s, %s, %s, NOW())",
            (user_id, topic_id, score),
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Score recorded."}), 201
    except Exception as e:
        print(f"Record Quiz Result API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard(user_id):
    """Return progress metrics for the user."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            SELECT up.topicid AS topic_id, t.TopicName
            FROM tbl_userprogress up
            JOIN tbl_topic t ON up.topicid = t.id
            WHERE up.userid = %s AND up.status = 'completed'
            """,
            (user_id,),
        )
        completed = cursor.fetchall()

        cursor.execute(
            """
            SELECT qs.topicid AS topic_id, t.TopicName, qs.score, qs.takenon
            FROM tbl_quizscore qs
            JOIN tbl_topic t ON qs.topicid = t.id
            WHERE qs.userid = %s
            ORDER BY qs.takenon DESC
            """,
            (user_id,),
        )
        quiz_scores = cursor.fetchall()

        cursor.execute(
            """
            SELECT id, title, due_date
            FROM tbl_assignment
            WHERE userid = %s AND due_date >= NOW()
            ORDER BY due_date
            """,
            (user_id,),
        )
        assignments = cursor.fetchall()

        return jsonify({
            "completedModules": completed,
            "quizScores": quiz_scores,
            "upcomingAssignments": assignments,
        })
    except Exception as e:
        print(f"Get Dashboard API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Return top users by average quiz score."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """
            SELECT u.id, u.username,
                   ROUND(AVG(q.score)::numeric, 2) AS average_score,
                   COUNT(*) AS attempts
            FROM tbl_quizscore q
            JOIN tbl_user u ON q.userid = u.id
            GROUP BY u.id, u.username
            ORDER BY average_score DESC
            LIMIT 10;
            """
        )
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Exception as e:
        print(f"Get Leaderboard API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/create-student', methods=['POST', 'OPTIONS'])
def create_student():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    username, password, parent_id = data.get('username'), data.get('password'), data.get('parentId')
    if not all([username, password, parent_id]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    # Server-side password validation
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({"status": "error", "message": message}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Determine plan limit for the parent
        cursor.execute("SELECT plan FROM tbl_user WHERE id = %s", (parent_id,))
        plan_row = cursor.fetchone()
        if not plan_row:
            return jsonify({"status": "error", "message": "Parent not found"}), 404
        plan = plan_row.get('plan', 'Monthly')
        plan_limits = {'Monthly': 1, 'Annual': 3, 'Family': 5}
        limit = plan_limits.get(plan, 1)
        cursor.execute("SELECT COUNT(*) AS student_count FROM tbl_user WHERE parentuserid = %s", (parent_id,))
        current_count = cursor.fetchone()['student_count']
        if current_count >= limit:
            return jsonify({"status": "error", "message": "Student limit reached for your plan"}), 403

        cursor.execute("SELECT id FROM tbl_user WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "This username is already taken"}), 409

        placeholder_email = f"{username.lower()}@logicandstories.student"
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute(
            "INSERT INTO tbl_user (username, email, passwordhash, usertype, parentuserid) VALUES (%s, %s, %s, 'Student', %s)",
            (username, placeholder_email, hashed_password, parent_id)
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Student account created!"}), 201
    except Exception as e:
        print(f"Create Student API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/my-students/<int:parent_id>', methods=['GET'])
def get_my_students(parent_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT id, username, createdon FROM tbl_user WHERE parentuserid = %s", (parent_id,))
        students = cursor.fetchall()
        return jsonify(students), 200
    except Exception as e:
        print(f"Get Students API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/modify-student', methods=['POST', 'OPTIONS'])
def modify_student():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    student_id, new_password = data.get('studentId'), data.get('newPassword')
    if not all([student_id, new_password]):
        return jsonify({"status": "error", "message": "Student id and new password are required"}), 400

    # Server-side password validation
    is_valid, message = validate_password(new_password)
    if not is_valid:
        return jsonify({"status": "error", "message": message}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        cursor.execute(
            "UPDATE tbl_user SET passwordhash = %s WHERE id = %s AND usertype = 'Student'",
            (hashed_password, student_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Student not found or invalid id"}), 404

        conn.commit()
        return jsonify({"status": "success", "message": "Student password updated successfully!"}), 200
    except Exception as e:
        print(f"Modify Student API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/delete-student/<int:student_id>', methods=['DELETE', 'OPTIONS'])
def delete_student_from_parent_portal(student_id):
    if request.method == 'OPTIONS': return jsonify(success=True)
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tbl_user WHERE id = %s AND usertype = 'Student'", (student_id,))
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Student not found or already deleted"}), 404

        conn.commit()
        return jsonify({"status": "success", "message": "Student account deleted successfully."}), 200
    except Exception as e:
        print(f"Delete Student API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/subscription-status/<int:user_id>', methods=['GET', 'OPTIONS'])
def subscription_status(user_id):
    """Return whether a user has an active subscription."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT active, expires_on FROM tbl_subscription WHERE user_id = %s",
            (user_id,),
        )
        row = cursor.fetchone()
        if row:
            active, expires_on = row
            if expires_on and expires_on <= datetime.utcnow():
                cursor.execute(
                    "UPDATE tbl_subscription SET active = FALSE WHERE user_id = %s",
                    (user_id,),
                )
                conn.commit()
                active = False
            if active:
                return (
                    jsonify(
                        {
                            "active": True,
                            "expires_on": expires_on.date().isoformat()
                            if expires_on
                            else None,
                        }
                    ),
                    200,
                )
        return jsonify({"active": False}), 200
    except Exception as e:
        print(f"Subscription Status API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/cancel-subscription/<int:user_id>', methods=['POST', 'OPTIONS'])
def cancel_subscription(user_id):
    """Mark a user's subscription as cancelled."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM tbl_user WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "User not found"}), 404

        cursor.execute(
            "SELECT active FROM tbl_subscription WHERE user_id = %s",
            (user_id,),
        )
        sub = cursor.fetchone()
        if not sub or not sub[0]:
            return (
                jsonify(
                    {"status": "error", "message": "No active subscription to cancel."}
                ),
                400,
            )

        cursor.execute(
            "UPDATE tbl_subscription SET active = FALSE, cancelled_on = NOW() WHERE user_id = %s",
            (user_id,),
        )
        conn.commit()

        return jsonify({"status": "success", "message": "Subscription cancelled."}), 200
    except Exception as e:
        print(f"Cancel Subscription API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/get_curriculums', methods=['GET'])
def get_curriculums():
    """Return a list of curriculum names from the database or a mock list."""
    mock_curriculums = ["Common Core", "IB", "AP"]
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT TRIM(SubjectName) FROM tbl_subject ORDER BY TRIM(SubjectName);"
        )
        rows = cursor.fetchall()
        curriculums = [row[0] for row in rows]
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"get_curriculums error: {e}")
        traceback.print_exc()
        curriculums = mock_curriculums
    finally:
        if conn:
            release_db_connection(conn)
    return jsonify(curriculums)


@app.route('/get_units/<curriculum>', methods=['GET'])
def get_units(curriculum):
    """Return distinct unit names for the given curriculum."""
    # Validate curriculum using the list returned by get_curriculums
    valid_curriculums = get_curriculums().get_json()
    if curriculum not in valid_curriculums:
        return jsonify({"status": "error", "message": "Invalid curriculum."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = sql.SQL(
            """
            SELECT DISTINCT unit.TopicName
            FROM tbl_topic unit
            JOIN tbl_subject s ON unit.subjectid = s.id
            WHERE unit.parenttopicid IS NULL
              AND s.SubjectName = %s
            ORDER BY unit.TopicName;
            """
        )
        cursor.execute(query, (curriculum,))
        rows = cursor.fetchall()
        units = [r[0] for r in rows]
    except Exception as e:
        print(f"get_units error: {e}")
        traceback.print_exc()
        units = []
    finally:
        if conn:
            release_db_connection(conn)
    return jsonify(units)


@app.route('/get_topics/<curriculum>/<unit>', methods=['GET'])
def get_topics(curriculum, unit):
    """Return topics for the given curriculum and unit."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = sql.SQL(
            """
            SELECT t.id, t.TopicName
            FROM tbl_topic t
            JOIN tbl_topic unit ON t.parenttopicid = unit.id
            JOIN tbl_subject s ON unit.subjectid = s.id
              WHERE s.SubjectName = %s
              AND unit.TopicName = %s
            ORDER BY t.TopicName;
            """
        )
        cursor.execute(query, (curriculum, unit))
        topics = [{"id": row["id"], "name": row["topicname"]} for row in cursor.fetchall()]
    except Exception as e:
        print(f"get_topics error: {e}")
        traceback.print_exc()
        topics = []
    finally:
        if conn:
            release_db_connection(conn)
    return jsonify(topics)


@app.route('/api/admin/curriculums', methods=['GET'])
def admin_get_curriculums():
    """Return curriculums, optionally filtered by a search term."""
    search = request.args.get('search', '').strip()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if search:
            cursor.execute(
                "SELECT id, subjectname FROM tbl_subject WHERE subjectname ILIKE %s ORDER BY subjectname;",
                (f"%{search}%",),
            )
        else:
            cursor.execute("SELECT id, subjectname FROM tbl_subject ORDER BY subjectname;")
        rows = cursor.fetchall()
        return jsonify(rows)
    except Exception as e:
        print(f"Admin get curriculums error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/curriculums/<int:subject_id>', methods=['GET'])
def admin_get_curriculum(subject_id):
    """Return a single curriculum by ID."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT id, subjectname FROM tbl_subject WHERE id = %s", (subject_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"status": "error", "message": "Curriculum not found"}), 404
        return jsonify(row)
    except Exception as e:
        print(f"Admin get curriculum error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/curriculum-hierarchy', methods=['GET'])
def admin_curriculum_hierarchy():
    """Return units and topics grouped under each curriculum."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT s.subjectname AS curriculum,
                   unit.topicname AS unitname,
                   t.topicname AS topicname,
                   t.id AS topicid
            FROM tbl_topic t
            JOIN tbl_topic unit ON t.parenttopicid = unit.id
            JOIN tbl_subject s ON unit.subjectid = s.id
            ORDER BY s.subjectname, unit.topicname, t.topicname;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        hierarchy = {}
        for row in rows:
            cur = row['curriculum']
            unit = row['unitname']
            topic = row['topicname']
            tid = row['topicid']
            if cur not in hierarchy:
                hierarchy[cur] = {}
            if unit not in hierarchy[cur]:
                hierarchy[cur][unit] = []
            hierarchy[cur][unit].append({'id': tid, 'name': topic})

        return jsonify(hierarchy)
    except Exception as e:
        print(f"Admin curriculum hierarchy error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/curriculum-table', methods=['GET'])
def get_curriculum_table():
    """Return curriculum data in a flat table format."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT g.GradeName, s.SubjectName AS CurriculumType,
                   unit.TopicName AS UnitName, topic.TopicName
            FROM tbl_topic topic
            JOIN tbl_topic unit ON topic.parenttopicid = unit.id
            JOIN tbl_subject s ON unit.subjectid = s.id
            JOIN tbl_topicgrade tg ON topic.id = tg.topicid
            JOIN tbl_grade g ON tg.gradeid = g.id
            ORDER BY g.id, s.id, unit.id, topic.id;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify(rows)
    except Exception as e:
        print(f"Curriculum table error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/create-curriculum', methods=['POST', 'OPTIONS'])
def create_curriculum():
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    data = request.get_json()
    name = data.get('name') if data else None

    if not name:
        return jsonify({"status": "error", "message": "Missing curriculum name"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tbl_subject (subjectname, subjecttype, createdby) VALUES (%s, 'Curriculum', %s)",
            (name, 'API'),
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Curriculum created."}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Create Curriculum API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/delete-curriculum/<int:subject_id>', methods=['DELETE', 'OPTIONS'])
def delete_curriculum(subject_id):
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Begin transaction as multiple tables are affected
        conn.autocommit = False

        # Collect all topic IDs linked to this curriculum
        cursor.execute("SELECT id FROM tbl_topic WHERE subjectid = %s", (subject_id,))
        topic_ids = [row[0] for row in cursor.fetchall()]

        if topic_ids:
            placeholders = sql.SQL(',').join(sql.Placeholder() * len(topic_ids))

            # Remove theme links for these topics
            cursor.execute(
                sql.SQL("DELETE FROM tbl_topictheme WHERE topicid IN ({})").format(placeholders),
                tuple(topic_ids),
            )

            # Remove descriptions and any linked interactive elements
            cursor.execute(
                sql.SQL(
                    "SELECT interactiveelementid FROM tbl_description "
                    "WHERE topicid IN ({}) AND interactiveelementid IS NOT NULL"
                ).format(placeholders),
                tuple(topic_ids),
            )
            interactive_ids = [row[0] for row in cursor.fetchall()]

            if interactive_ids:
                ie_placeholders = sql.SQL(',').join(sql.Placeholder() * len(interactive_ids))
                cursor.execute(
                    sql.SQL("DELETE FROM tbl_interactiveelement WHERE id IN ({})").format(ie_placeholders),
                    tuple(interactive_ids),
                )

            cursor.execute(
                sql.SQL("DELETE FROM tbl_description WHERE topicid IN ({})").format(placeholders),
                tuple(topic_ids),
            )

            # Remove other topic dependencies
            cursor.execute(
                sql.SQL("DELETE FROM tbl_topicgrade WHERE topicid IN ({})").format(placeholders),
                tuple(topic_ids),
            )

            # Remove steps and answers linked to questions before deleting the questions themselves
            cursor.execute(
                sql.SQL("SELECT id FROM tbl_question WHERE topicid IN ({})").format(placeholders),
                tuple(topic_ids),
            )
            question_ids = [row[0] for row in cursor.fetchall()]
            if question_ids:
                q_placeholders = sql.SQL(',').join(sql.Placeholder() * len(question_ids))
                cursor.execute(
                    sql.SQL("DELETE FROM tbl_step WHERE questionid IN ({})").format(q_placeholders),
                    tuple(question_ids),
                )
                cursor.execute(
                    sql.SQL("DELETE FROM tbl_answer WHERE questionid IN ({})").format(q_placeholders),
                    tuple(question_ids),
                )
                cursor.execute("SELECT to_regclass('tbl_questionattempt')")
                if cursor.fetchone()[0]:
                    cursor.execute(
                        sql.SQL("DELETE FROM tbl_questionattempt WHERE questionid IN ({})").format(q_placeholders),
                        tuple(question_ids),
                    )

            cursor.execute(
                sql.SQL("DELETE FROM tbl_question WHERE topicid IN ({})").format(placeholders),
                tuple(topic_ids),
            )
            cursor.execute(
                sql.SQL("DELETE FROM tbl_userprogress WHERE topicid IN ({})").format(placeholders),
                tuple(topic_ids),
            )
            cursor.execute("SELECT to_regclass('tbl_quizscore')")
            if cursor.fetchone()[0]:
                cursor.execute(
                    sql.SQL("DELETE FROM tbl_quizscore WHERE topicid IN ({})").format(placeholders),
                    tuple(topic_ids),
                )
            cursor.execute(
                sql.SQL("DELETE FROM tbl_usertopicdifficulty WHERE topicid IN ({})").format(placeholders),
                tuple(topic_ids),
            )
            cursor.execute("SELECT to_regclass('tbl_flagreport')")
            if cursor.fetchone()[0]:
                cursor.execute(
                    sql.SQL(
                        "DELETE FROM tbl_flagreport WHERE itemtype = 'Story' AND flaggeditemid IN ({})"
                    ).format(placeholders),
                    tuple(topic_ids),
                )

            # Finally remove the topics themselves
            cursor.execute(
                sql.SQL("DELETE FROM tbl_topic WHERE id IN ({})").format(placeholders),
                tuple(topic_ids),
            )

        # Remove the curriculum
        cursor.execute("DELETE FROM tbl_subject WHERE id = %s", (subject_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Curriculum not found."}), 404

        return jsonify({"status": "success", "message": "Curriculum deleted."}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Delete Curriculum API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/update-curriculum/<int:subject_id>', methods=['PUT', 'OPTIONS'])
def update_curriculum(subject_id):
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({"status": "error", "message": "Missing curriculum name"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tbl_subject SET subjectname = %s WHERE id = %s", (name, subject_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Curriculum not found or unchanged."}), 404

        return jsonify({"status": "success", "message": "Curriculum updated."}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Update Curriculum API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/curriculum', methods=['GET'])
def get_curriculum():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT
                g.GradeName,
                s.SubjectName AS CurriculumType,
                unit.TopicName AS UnitName,
                topic.TopicName,
                topic.id AS topicid,
                string_agg(DISTINCT th.themename, ',' ORDER BY th.themename) AS AvailableThemes,
                (SELECT dth.themename FROM tbl_topictheme tth JOIN tbl_theme dth ON tth.themeid = dth.id WHERE tth.topicid = topic.id AND tth.isdefault = TRUE LIMIT 1) AS DefaultTheme
            FROM tbl_topic topic
            JOIN tbl_topic unit ON topic.parenttopicid = unit.id
            JOIN tbl_subject s ON unit.subjectid = s.id
            JOIN tbl_topicgrade tg ON topic.id = tg.topicid
            JOIN tbl_grade g ON tg.gradeid = g.id
            LEFT JOIN tbl_topictheme tt ON topic.id = tt.topicid
            LEFT JOIN tbl_theme th ON tt.themeid = th.id
            GROUP BY g.id, s.id, unit.id, topic.id, g.GradeName, s.SubjectName, unit.TopicName, topic.TopicName
            ORDER BY g.id, s.id, unit.id, topic.id;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        curriculum_data = {}
        # This mapping is for frontend display, so it's kept here.
        # In a very large app, this might come from a config or DB.
        grade_color_map = {
            "4th Grade": {"icon": "4th", "color": "fde047"},
            "5th Grade": {"icon": "5th", "color": "fb923c"},
            "6th Grade": {"icon": "6th", "color": "a78bfa"},
            "7th Grade": {"icon": "7th", "color": "60a5fa"},
            "8th Grade": {"icon": "8th", "color": "f472b6"},
            "9th Grade": {"icon": "9th", "color": "818cf8"},
            "10th Grade": {"icon": "10th", "color": "34d399"},
            "11th Grade": {"icon": "11th", "color": "22d3ee"},
            "Algebra 1": {"icon": "Alg1", "color": "fcd34d"},
            "Geometry": {"icon": "Geom", "color": "2dd4bf"},
            "Pre-Calculus": {"icon": "Pre-C", "color": "a3e635"},
            "Calculus": {"icon": "Calc", "color": "f87171"},
            "Statistics": {"icon": "Stats", "color": "c084fc"},
            "Contest Math (AMC)": {"icon": "AMC", "color": "e11d48"},
            "IB Math AA SL": {"icon": "AA SL", "color": "f9a8d4"},
            "IB Math AA HL": {"icon": "AA HL", "color": "f0abfc"},
            "IB Math AI SL": {"icon": "AI SL", "color": "a5f3fc"},
            "IB Math AI HL": {"icon": "AI HL", "color": "bbf7d0"},
        }
        for row in rows:
            grade_name = row.get('gradename') or row.get('GradeName')
            curriculum_type = row.get('curriculumtype') or row.get('CurriculumType')
            unit_name = row.get('unitname') or row.get('UnitName')
            topic_name = row.get('topicname') or row.get('TopicName')
            topic_id = row.get('topicid') or row.get('topicid')
            available_themes_str = row.get('availablethemes') or row.get('AvailableThemes')
            default_theme = row.get('defaulttheme') or row.get('DefaultTheme')
            
            clean_grade_name = ' '.join(grade_name.replace('grade', 'Grade').split()).strip()
            if clean_grade_name not in curriculum_data:
                style = grade_color_map.get(clean_grade_name, { "icon": clean_grade_name[:3], "color": "94a3b8" })
                curriculum_data[clean_grade_name] = {**style, "curriculums": {}}
            if curriculum_type not in curriculum_data[clean_grade_name]['curriculums']:
                curriculum_data[clean_grade_name]['curriculums'][curriculum_type] = {"units": {}}
            if unit_name not in curriculum_data[clean_grade_name]['curriculums'][curriculum_type]['units']:
                curriculum_data[clean_grade_name]['curriculums'][curriculum_type]['units'][unit_name] = []
            
            available_themes = available_themes_str.split(',') if available_themes_str else []

            curriculum_data[clean_grade_name]['curriculums'][curriculum_type]['units'][unit_name].append({
                "name": topic_name,
                "id": topic_id,
                "availableThemes": available_themes,
                "defaultTheme": default_theme
            })

        return jsonify(curriculum_data)
    except Exception as e:
        print(f"API Error in get_curriculum: {e}")
        traceback.print_exc()
        return jsonify({ "status": "error", "message": str(e) }), 500
    finally:
        if conn:
            release_db_connection(conn)

# --- QUIZ ENDPOINTS ---

@app.route('/api/user/topic-difficulty/<int:user_id>/<int:topic_id>', methods=['GET'])
def get_user_topic_difficulty(user_id, topic_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT currentdifficulty FROM tbl_usertopicdifficulty WHERE userid = %s AND topicid = %s"
        cursor.execute(query, (user_id, topic_id))
        result = cursor.fetchone()
        difficulty = result['currentdifficulty'] if result else 1
        return jsonify({"status": "success", "difficulty": difficulty}), 200
    except Exception as e:
        print(f"Get User Topic Difficulty API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching user difficulty."}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/user/update-topic-difficulty', methods=['POST', 'OPTIONS'])
def update_user_topic_difficulty():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    user_id = data.get('userId')
    topic_id = data.get('topicId')
    new_difficulty = data.get('newDifficulty')

    if not all([user_id, topic_id, new_difficulty]):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    try:
        new_difficulty = int(new_difficulty)
        if not (1 <= new_difficulty <= 5):
            return jsonify({"status": "error", "message": "Difficulty must be between 1 and 5."}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid difficulty rating."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO tbl_usertopicdifficulty (userid, topicid, currentdifficulty)
            VALUES (%s, %s, %s)
            ON CONFLICT (userid, topicid)
            DO UPDATE SET currentdifficulty = EXCLUDED.currentdifficulty;
        """
        cursor.execute(query, (user_id, topic_id, new_difficulty))
        conn.commit()
        return jsonify({"status": "success", "message": "User difficulty updated."}), 200
    except Exception as e:
        print(f"Update User Topic Difficulty API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error updating user difficulty."}), 500
    finally:
        if conn:
            release_db_connection(conn)


# The quiz question endpoint is now provided via ``quiz_bp`` in ``quiz.py``.
# The original implementation in this file was duplicated and is removed to
# avoid conflicting route handlers. ``quiz_bp`` continues to be registered
# so ``/api/quiz/question/<user_id>/<topic_id>/<difficulty_level>`` remains
# accessible.

# --- FLAGGING ENDPOINTS ---

@app.route('/api/flag-item', methods=['POST', 'OPTIONS'])
def flag_item():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    user_id = data.get('userId')
    flagged_item_id = data.get('flaggedItemId')
    item_type = data.get('itemType')
    reason = data.get('reason')

    if not all([user_id, flagged_item_id, item_type]):
        return jsonify({"status": "error", "message": "Missing required fields for flagging."}), 400

    if item_type not in ['Question', 'Story']:
        return jsonify({"status": "error", "message": "Invalid item type for flagging. Must be 'Question' or 'Story'."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO tbl_flagreport (userid, flaggeditemid, itemtype, reason, status)
            VALUES (%s, %s, %s, %s, 'Pending');
        """
        cursor.execute(insert_query, (user_id, flagged_item_id, item_type, reason))
        conn.commit()

        return jsonify({"status": "success", "message": "Item flagged successfully. An admin will review it."}), 201
    except Exception as e:
        print(f"Flag Item API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error while flagging item."}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/flagged-items', methods=['GET'])
def get_flagged_items():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT
                fr.id AS "FlagID",
                fr.userid AS "UserID",
                u.username AS "ReporterUsername",
                fr.flaggeditemid AS "FlaggedItemID",
                fr.itemtype AS "ItemType",
                CASE
                    WHEN fr.itemtype = 'Question' THEN q.questionname
                    WHEN fr.itemtype = 'Story' THEN t.TopicName
                    ELSE 'N/A'
                END AS "ItemName",
                fr.reason AS "Reason",
                fr.status AS "Status",
                fr.ReportedOn AS "ReportedOn",
                fr.ResolvedOn AS "ResolvedOn",
                ru.username AS "ResolvedByUsername"
            FROM tbl_flagreport fr
            LEFT JOIN tbl_user u ON fr.userid = u.id
            LEFT JOIN tbl_question q ON fr.itemtype = 'Question' AND fr.flaggeditemid = q.id
            LEFT JOIN tbl_topic t ON fr.itemtype = 'Story' AND fr.flaggeditemid = t.id
            LEFT JOIN tbl_user ru ON fr.ResolvedBy = ru.id
            ORDER BY fr.ReportedOn DESC;
        """
        cursor.execute(query)
        flags = cursor.fetchall()

        return jsonify(flags), 200
    except Exception as e:
        print(f"Get Flagged Items API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching flagged items."}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/admin/update-flag-status/<int:flag_id>', methods=['PUT', 'OPTIONS'])
def update_flag_status(flag_id):
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    new_status = data.get('status')
    admin_id = data.get('adminId')

    if not all([new_status, admin_id]):
        return jsonify({"status": "error", "message": "Missing status or admin id."}), 400

    if new_status not in ['Pending', 'Reviewed', 'Dismissed']:
        return jsonify({"status": "error", "message": "Invalid status. Must be 'Pending', 'Reviewed', or 'Dismissed'."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if new_status == 'Pending':
            update_query = """
                UPDATE tbl_flagreport
                SET status = %s, ResolvedOn = NULL, ResolvedBy = NULL
                WHERE id = %s;
            """
            cursor.execute(update_query, (new_status, flag_id))
        else:
            update_query = """
                UPDATE tbl_flagreport
                SET status = %s, ResolvedOn = NOW(), ResolvedBy = %s
                WHERE id = %s;
            """
            cursor.execute(update_query, (new_status, admin_id, flag_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Flag report not found or status already set."}), 404

        return jsonify({"status": "success", "message": f"Flag {flag_id} status updated to {new_status}."}), 200
    except Exception as e:
        print(f"Update Flag status API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error updating flag status."}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/admin/delete-flag/<int:flag_id>', methods=['DELETE', 'OPTIONS'])
def delete_flag(flag_id):
    """Delete a flag report by its ID."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        delete_query = "DELETE FROM tbl_flagreport WHERE id = %s;"
        cursor.execute(delete_query, (flag_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Flag not found or already deleted."}), 404

        return jsonify({"status": "success", "message": "Flag deleted successfully."}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Delete Flag API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error deleting flag."}), 500
    finally:
        if conn:
            release_db_connection(conn)

# --- QUESTION ATTEMPT LOGGING ENDPOINT ---
@app.route('/api/record-question-attempt', methods=['POST', 'OPTIONS'])
def record_question_attempt():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    user_id = data.get('userId')
    question_id = data.get('questionId')
    user_answer = data.get('userAnswer')
    is_correct = data.get('isCorrect')
    difficulty_at_attempt = data.get('difficultyAtAttempt')

    if not all([user_id, question_id, user_answer is not None, is_correct is not None, difficulty_at_attempt is not None]):
        return jsonify({"status": "error", "message": "Missing required fields for question attempt."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO tbl_questionattempt (userid, questionid, useranswer, iscorrect, difficultyatattempt)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (user_id, question_id, user_answer, is_correct, difficulty_at_attempt))
        conn.commit()
        return jsonify({"status": "success", "message": "Question attempt recorded successfully."}), 201
    except Exception as e:
        print(f"Record Question Attempt API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error recording question attempt."}), 500
    finally:
        if conn:
            release_db_connection(conn)

# --- ADMIN ENDPOINT TO GET ALL QUESTION ATTEMPTS ---
@app.route('/api/admin/question-attempts', methods=['GET'])
def get_all_question_attempts():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT
                qa.id AS "AttemptID",
                qa.attempttime AS "attempttime",
                qa.useranswer AS "useranswer",
                qa.iscorrect AS "iscorrect",
                qa.difficultyatattempt AS "difficultyatattempt",
                u.username AS "AttemptingUsername",
                q.questionname AS "QuestionText",
                t.TopicName AS "TopicName",
                unit.TopicName AS "UnitName",
                s.SubjectName AS "CurriculumType",
                string_agg(TRIM(a.answername), ',' ) FILTER (WHERE a.iscorrect = TRUE) AS "CorrectAnswer"
            FROM tbl_questionattempt qa
            JOIN tbl_user u ON qa.userid = u.id
            JOIN tbl_question q ON qa.questionid = q.id
            JOIN tbl_topic t ON q.topicid = t.id
            JOIN tbl_topic unit ON t.parenttopicid = unit.id
            JOIN tbl_subject s ON unit.subjectid = s.id
            LEFT JOIN tbl_answer a ON q.id = a.questionid AND a.iscorrect = TRUE
            GROUP BY qa.id, qa.attempttime, qa.useranswer, qa.iscorrect, qa.difficultyatattempt, u.username, q.questionname, t.TopicName, unit.TopicName, s.SubjectName
            ORDER BY qa.attempttime DESC;
        """
        cursor.execute(query)
        attempts = cursor.fetchall()

        return jsonify(attempts), 200
    except Exception as e:
        print(f"Get All Question Attempts API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching question attempts."}), 500
    finally:
        if conn:
            release_db_connection(conn)


@app.route('/api/open-flags', methods=['GET'])
def get_open_flags():
    """Return all flags that are still pending review."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT
                fr.id AS "FlagID",
                fr.userid AS "UserID",
                fr.flaggeditemid AS "FlaggedItemID",
                fr.itemtype AS "ItemType",
                CASE
                    WHEN fr.itemtype = 'Question' THEN q.questionname
                    WHEN fr.itemtype = 'Story' THEN t.TopicName
                    ELSE 'N/A'
                END AS "ItemName",
                fr.reason AS "Reason",
                fr.ReportedOn AS "ReportedOn"
            FROM tbl_flagreport fr
            LEFT JOIN tbl_question q ON fr.itemtype = 'Question' AND fr.flaggeditemid = q.id
            LEFT JOIN tbl_topic t ON fr.itemtype = 'Story' AND fr.flaggeditemid = t.id
            WHERE fr.status = 'Pending'
            ORDER BY fr.ReportedOn DESC;
        """
        cursor.execute(query)
        flags = cursor.fetchall()
        return jsonify(flags), 200
    except Exception as e:
        print(f"Get Open Flags API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching open flags."}), 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/api/flag-page-error', methods=['POST', 'OPTIONS'])
def flag_page_error():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    user_id = data.get("userId") or 0
    page_path = data.get('pagePath')
    description = data.get('description')

    if not all([page_path, description]):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO tbl_flagreport (userid, flaggeditemid, itemtype, reason)
            VALUES (%s, %s, %s, %s);
        """
        reason_combined = f"{page_path}: {description}"
        cursor.execute(insert_query, (user_id, 0, 'Story', reason_combined))
        conn.commit()
        return jsonify({"status": "success", "message": "Error reported. Thank you!"}), 201
    except Exception as e:
        print(f"Flag Page Error API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error while reporting."}), 500
    finally:
        if conn:
            release_db_connection(conn)


# =================================================================
#  2. ERROR HANDLERS
# =================================================================

@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith('/api/'):
        return jsonify({'status': 'error', 'message': 'Not found'}), 404
    return render_template('404.html'), 404

# =================================================================
# =================================================================
#  3. FRONTEND ROUTES (Serve HTML Pages)
# =================================================================

@app.route('/')
def serve_home():
    return render_template('index.html')

@app.route('/index.html')
def serve_index():
    return render_template('index.html')

@app.route('/admin-login.html')
def serve_admin_login():
    return redirect(url_for('serve_signin'))

@app.route('/admin.html')
def serve_admin():
    return render_template('admin.html')

@app.route('/dashboard.html')
def serve_dashboard():
    return render_template('dashboard.html')

@app.route('/forgot-password.html')
def serve_forgot_password():
    return render_template('forgot-password.html')

@app.route('/parent-login.html')
def serve_parent_login():
    return redirect(url_for('serve_signin'))

@app.route('/student-login.html')
def serve_student_login():
    return redirect(url_for('serve_signin'))

@app.route('/signin.html')
def serve_signin():
    return render_template('signin.html')

@app.route('/parent-portal.html')
def serve_parent_portal():
    return render_template('parent-portal.html')

@app.route('/quiz-player.html')
def serve_quiz_player():
    return render_template('quiz-player.html')

@app.route('/reset-password.html')
def serve_reset_password():
    return render_template('reset-password.html')

@app.route('/signup.html')
def serve_signup():
    return render_template('signup.html')

@app.route('/choose-plan.html')
def serve_choose_plan():
    return render_template('choose-plan.html')

@app.route('/story-player.html')
def serve_story_player():
    return render_template('story-player.html')

@app.route('/progress-dashboard.html')
def serve_progress_dashboard():
    return render_template('progress-dashboard.html')

@app.route('/blog.html')
@app.route('/blog')
def serve_blog():
    return render_template('blog.html')

@app.route('/terms-of-service.html')
def serve_terms_of_service():
    return render_template('terms-of-service.html')

@app.route('/privacy-policy.html')
def serve_privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)


# =================================================================
#  4. RUN THE SERVER
# =================================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
