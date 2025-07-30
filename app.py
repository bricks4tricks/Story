import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import secrets
from datetime import datetime, timedelta
import traceback
import json
import random
import re
import os # Import os module to access environment variables

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
bcrypt = Bcrypt(app)
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
from db_utils import get_db_connection

# Define a mapping for QuestionType (if using integer in DB)
QUESTION_TYPE_MAP = {
    'MultipleChoice': 1,
    'OpenEnded': 2
}
QUESTION_TYPE_REVERSE_MAP = {
    1: 'MultipleChoice',
    2: 'OpenEnded'
}

# Password validation regex and message
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$"
PASSWORD_REQUIREMENTS_MESSAGE = "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character (!@#$%^&*()_+)."

def validate_password(password):
    """
    Validates a password against predefined security requirements.
    Returns True and None on success, False and an error message on failure.
    """
    if not re.fullmatch(PASSWORD_REGEX, password):
        return False, PASSWORD_REQUIREMENTS_MESSAGE
    return True, None



# --- UPDATED: EMAIL CONFIGURATION FROM ENVIRONMENT VARIABLES ---
# Retrieve SMTP settings from environment variables with sensible defaults for local testing.
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587)) # Ensure port is an integer
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'admin@bricks4tricks.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'jxuf jldh muge nwry') # This should be your App Password, not your regular email password
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'admin@bricks4tricks.com')

# --- UPDATED: Frontend Base URL Configuration ---
# This will allow you to set the frontend URL dynamically based on your deployment.
# For production, you can override it by setting FRONTEND_BASE_URL
# as an environment variable. By default, this is set to
# https://logicandstories.com.
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', 'https://logicandstories.com')

# Function to send email
def send_email(receiver_email, subject, html_content):
    """Sends an HTML email."""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # Use TLS encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {e}")
        traceback.print_exc()
        return False

# --- NEW: Load email template content ---
# This template is embedded directly in the Python script for simplicity.
# In a larger application, you might load this from a separate HTML file.
RESET_PASSWORD_EMAIL_TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logic and Stories - Password Reset Request</title>
    <style>
        /* Inlining basic styles for better email client compatibility */
        body {
            font-family: 'Nunito', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #0f172a; /* slate-900 */
            color: #e2e8f0; /* gray-200 */
        }
        .font-pacifico {
            font-family: 'Pacifico', cursive;
        }
        .gradient-text {
            background: linear-gradient(to right, #fde047, #fb923c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .glow-button {
            box-shadow: 0 0 15px rgba(253, 224, 71, 0.5), 0 0 5px rgba(251, 146, 60, 0.4);
        }
        /* Ensure responsive behavior for email clients */
        @media only screen and (max-width: 600px) {
            .container {
                padding: 10px !important;
            }
            .content-block {
                padding: 20px !important;
            }
            .button {
                padding: 12px 25px !important;
                font-size: 16px !important;
            }
        }
    </style>
</head>
<body style="background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 0; font-family: 'Nunito', sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 32px 16px; box-sizing: border-box;">
        <!-- Header/Logo -->
        <div style="text-align: center; margin-bottom: 32px;">
            <a href="#" style="font-size: 36px; font-family: 'Pacifico', cursive; background: linear-gradient(to right, #fde047, #fb923c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-decoration: none;">Logic and Stories</a>
        </div>

        <!-- Email Content Block -->
        <div style="background-color: #1e293b; border-radius: 16px; padding: 24px 32px; border: 1px solid #334155;">
            <h2 style="font-size: 28px; font-weight: bold; color: #ffffff; text-align: center; margin-bottom: 24px;">Password Reset Request</h2>

            <p style="font-size: 18px; color: #cbd5e1; margin-bottom: 16px;">Hi there,</p>

            <p style="font-size: 18px; color: #cbd5e1; margin-bottom: 24px;">
                We received a request to reset the password for your Logic and Stories account.
                To reset your password, please click the button below:
            </p>

            <div style="text-align: center; margin-bottom: 32px;">
                <a href="{{RESET_LINK}}" style="display: inline-block; background-color: #fde047; color: #1e293b; font-weight: bold; padding: 12px 32px; border-radius: 9999px; text-decoration: none; transition: all 0.2s ease-in-out; box-shadow: 0 0 15px rgba(253, 224, 71, 0.5), 0 0 5px rgba(251, 146, 60, 0.4);">
                    Reset Your Password
                </a>
            </div>

            <p style="font-size: 18px; color: #cbd5e1; margin-bottom: 16px;">
                This link is valid for <strong>1 hour</strong>. If you do not reset your password within this time,
                you will need to submit another request.
            </p>

            <p style="font-size: 18px; color: #cbd5e1; margin-bottom: 24px;">
                If you did not request a password reset, please ignore this email. Your password will remain unchanged.
            </p>

            <p style="font-size: 18px; color: #cbd5e1;">Thanks,</p>
            <p style="font-size: 18px; color: #cbd5e1;">The Logic and Stories Team</p>
        </div>

        <!-- Footer -->
        <div style="text-align: center; color: #64748b; font-size: 14px; margin-top: 32px;">
            <p>&copy; 2024 Logic and Stories. All Rights Reserved.</p>
            <p style="margin-top: 8px;">
                If you have any questions, please contact our support team at
                <a href="mailto:support@logicandstories.com" style="color: #fde047; text-decoration: underline;">support@logicandstories.com</a>.
            </p>
        </div>
    </div>
</body>
</html>
"""
# --- END NEW EMAIL CONFIGURATION AND TEMPLATE ---


# =================================================================
#  2. API ENDPOINTS
# =================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"}), 200

@app.route('/api/signup', methods=['POST', 'OPTIONS'])
def signup_user():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    username, email, password = data.get('username'), data.get('email'), data.get('password')
    if not all([username, email, password]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    # Server-side password validation
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({"status": "error", "message": message}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT ID FROM tbl_User WHERE Username = %s OR Email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Username or email already exists"}), 409

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute(
            "INSERT INTO tbl_User (Username, Email, PasswordHash, UserType) VALUES (%s, %s, %s, 'Parent')",
            (username, email, hashed_password)
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Parent account created successfully!"}), 201
    except Exception as e:
        print(f"Signup API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/signin', methods=['POST', 'OPTIONS'])
def signin_user():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    if not all([username, password]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM tbl_User WHERE Username = %s", (username,))
        user = cursor.fetchone()
        # Column names returned by psycopg2 are lowercase unless explicitly
        # quoted when the table was created. Handle either case gracefully.
        password_hash = None
        user_type = None
        if user:
            password_hash = user.get('PasswordHash') or user.get('passwordhash')
            user_type = user.get('UserType') or user.get('usertype')

        if password_hash and bcrypt.check_password_hash(password_hash, password):
            # Column case may vary depending on how the table was created. Use
            # ``get`` with fallbacks to avoid ``KeyError`` if the database
            # returns lowercase column names such as ``id`` or ``username``.
            user_id = user.get('ID') or user.get('id')
            user_name = user.get('Username') or user.get('username')
            return jsonify({
                "status": "success",
                "message": "Login successful!",
                "user": {
                    "id": user_id,
                    "username": user_name,
                    "userType": user_type
                }
            }), 200
        else:
            return jsonify({"status": "error", "message": "Invalid username or password"}), 401
    except Exception as e:
        print(f"Signin API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/admin-signin', methods=['POST', 'OPTIONS'])
def admin_signin():
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM tbl_User WHERE Username = %s", (username,))
        user = cursor.fetchone()
        password_hash = None
        user_type = None
        if user:
            password_hash = user.get('PasswordHash') or user.get('passwordhash')
            # Handle case variations for the UserType column returned by the
            # database (e.g. "usertype" vs "UserType").
            user_type = user.get('UserType') or user.get('usertype')

        if (
            password_hash
            and bcrypt.check_password_hash(password_hash, password)
            and user_type == 'Admin'
        ):
            # As above, support lowercase column names to avoid ``KeyError`` if
            # the database was created without quoting identifiers.
            user_id = user.get('ID') or user.get('id')
            user_name = user.get('Username') or user.get('username')
            return jsonify({
                "status": "success",
                "message": "Admin login successful!",
                "user": {"id": user_id, "username": user_name, "userType": user_type}
            }), 200
        else:
            return jsonify({"status": "error", "message": "Invalid credentials or not an admin"}), 401
    except psycopg2.Error as e:
        print(f"Admin Signin DB Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Database error"}), 500
    except Exception as e:
        print(f"Admin Signin API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/admin/all-users', methods=['GET'])
def get_all_users():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT u.ID, u.Username, u.Email, u.UserType, u.CreatedOn, p.Username AS ParentUsername
            FROM tbl_User u
            LEFT JOIN tbl_User p ON u.ParentUserID = p.ID
            ORDER BY u.ID;
        """
        cursor.execute(query)
        users = cursor.fetchall()
        return jsonify(users)
    except Exception as e:
        print(f"Get All Users API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()


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
            "SELECT ID FROM tbl_User WHERE (Username = %s OR Email = %s) AND ID != %s",
            (username, email, user_id)
        )
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Username or email is already in use by another account."}), 409

        cursor.execute(
            "UPDATE tbl_User SET Username = %s, Email = %s, UserType = %s WHERE ID = %s",
            (username, email, user_type, user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "User not found or no changes made."}), 404

        return jsonify({"status": "success", "message": "User updated successfully!"}), 200
    except Exception as e:
        print(f"Edit User API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/admin/delete-user/<int:user_id>', methods=['DELETE', 'OPTIONS'])
def delete_user(user_id):
    if request.method == 'OPTIONS': return jsonify(success=True)
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT UserType FROM tbl_User WHERE ID = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "message": "User not found."}), 404

        user_type = user[0] # Access by index as cursor is not dictionary=True here

        if user_type == 'Admin':
            return jsonify({"status": "error", "message": "Admin accounts cannot be deleted."}), 403

        if user_type == 'Parent':
            cursor.execute("SELECT ID FROM tbl_User WHERE ParentUserID = %s", (user_id,))
            if cursor.fetchone():
                return jsonify({"status": "error", "message": "Cannot delete a parent with student accounts. Please delete the student profiles first."}), 409

        cursor.execute("DELETE FROM tbl_User WHERE ID = %s", (user_id,))
        conn.commit()

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
        if conn and conn.closed == 0:
            conn.close()


@app.route('/api/admin/topics-list', methods=['GET'])
def get_topics_list():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT
                t.ID,
                t.TopicName,
                unit.TopicName AS UnitName,
                s.SubjectName AS CurriculumType,
                (SELECT th.ThemeName FROM tbl_TopicTheme tth JOIN tbl_Theme th ON tth.ThemeID = th.ID WHERE tth.TopicID = t.ID AND tth.IsDefault = TRUE LIMIT 1) AS DefaultTheme
            FROM tbl_Topic t
            JOIN tbl_Topic unit ON t.ParentTopicID = unit.ID
            JOIN tbl_Subject s ON unit.SubjectID = s.ID
            WHERE t.Active = 1
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
        if conn and conn.closed == 0:
            conn.close()

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
            "INSERT INTO tbl_Question (TopicID, QuestionName, QuestionType, DifficultyRating, CreatedBy) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING ID"
        )
        cursor.execute(
            question_query,
            (topic_id, question_text, question_type_to_insert, difficulty_rating, 'Admin'),
        )
        question_id = cursor.fetchone()[0]

        answer_query = "INSERT INTO tbl_Answer (QuestionID, AnswerName, IsCorrect, CreatedBy) VALUES (%s, %s, %s, %s)"
        answer_values = []
        for ans in answers:
            if 'text' not in ans or 'isCorrect' not in ans:
                raise ValueError("Each answer must have 'text' and 'isCorrect' fields.")
            answer_values.append((question_id, ans['text'], ans['isCorrect'], 'Admin'))
        cursor.executemany(answer_query, answer_values)

        step_query = "INSERT INTO tbl_Step (QuestionID, SequenceNo, StepName, CreatedBy) VALUES (%s, %s, %s, %s)"
        step_values = []
        for idx, step in enumerate(steps):
            if 'text' not in step:
                 raise ValueError("Each step must have a 'text' field.")
            step_values.append((question_id, idx + 1, step['text'], 'Admin'))
        cursor.executemany(step_query, step_values)

        conn.commit()
        return jsonify({"status": "success", "message": f"Successfully added question (ID {question_id})."}), 201
    except Exception as e:
        if conn: conn.rollback()
        print(f"Add Question API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An unexpected error occurred."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/admin/questions', methods=['GET'])
def get_all_questions():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT
                q.ID,
                q.QuestionName,
                q.QuestionType,
                q.DifficultyRating,
                t.TopicName,
                unit.TopicName AS UnitName
            FROM tbl_Question q
            JOIN tbl_Topic t ON q.TopicID = t.ID
            JOIN tbl_Topic unit ON t.ParentTopicID = unit.ID
            ORDER BY q.ID DESC;
        """
        cursor.execute(query)
        questions = cursor.fetchall()
        return jsonify(questions)
    except Exception as e:
        print(f"Get All Questions API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/admin/question/<int:question_id>', methods=['GET'])
def get_question_details(question_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT ID, TopicID, QuestionName, QuestionType, DifficultyRating FROM tbl_Question WHERE ID = %s", (question_id,))
        question = cursor.fetchone()
        if not question:
            return jsonify({"status": "error", "message": "Question not found."}), 404

        question_type_display = question['QuestionType']

        cursor.execute("SELECT AnswerName, IsCorrect FROM tbl_Answer WHERE QuestionID = %s", (question_id,))
        answers = cursor.fetchall()

        cursor.execute("SELECT StepName FROM tbl_Step WHERE QuestionID = %s ORDER BY SequenceNo", (question_id,))
        steps = cursor.fetchall()

        cursor.execute("""
            SELECT
                t.ID AS TopicID,
                t.TopicName,
                unit.TopicName AS UnitName,
                s.SubjectName AS CurriculumType
            FROM tbl_Topic t
            JOIN tbl_Topic unit ON t.ParentTopicID = unit.ID
            JOIN tbl_Subject s ON unit.SubjectID = s.ID
            WHERE t.ID = %s
        """, (question['TopicID'],))
        topic_info = cursor.fetchone()

        question_details = {
            "ID": question['ID'],
            "TopicID": question['TopicID'],
            "TopicName": topic_info['TopicName'] if topic_info else None,
            "UnitName": topic_info['UnitName'] if topic_info else None,
            "CurriculumType": topic_info['CurriculumType'] if topic_info else None,
            "QuestionName": question['QuestionName'],
            "QuestionType": question_type_display,
            "DifficultyRating": question['DifficultyRating'],
            "Answers": answers,
            "Steps": [s['StepName'] for s in steps]
        }

        return jsonify(question_details), 200

    except Exception as e:
        print(f"Get Question Details API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching question details."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/admin/edit-question/<int:question_id>', methods=['PUT', 'OPTIONS'])
def edit_question(question_id):
    if request.method == 'OPTIONS': return jsonify(success=True)

    data = request.get_json()
    payload_question_id = data.get('questionId')
    if payload_question_id and payload_question_id != question_id:
        return jsonify({"status": "error", "message": "Mismatched question ID in URL and payload."}), 400

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

        question_update_query = "UPDATE tbl_Question SET TopicID = %s, QuestionName = %s, QuestionType = %s, DifficultyRating = %s, LastUpdatedOn = NOW(), LastUpdatedBy = %s WHERE ID = %s"
        cursor.execute(question_update_query, (topic_id, question_text, question_type_to_update, difficulty_rating, 'Admin', question_id))

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"status": "error", "message": "Question not found or no changes made."}), 404

        cursor.execute("DELETE FROM tbl_Answer WHERE QuestionID = %s", (question_id,))
        cursor.execute("DELETE FROM tbl_Step WHERE QuestionID = %s", (question_id,))

        answer_query = "INSERT INTO tbl_Answer (QuestionID, AnswerName, IsCorrect, CreatedBy) VALUES (%s, %s, %s, %s)"
        answer_values = []
        for ans in answers:
            if 'text' not in ans or 'isCorrect' not in ans:
                raise ValueError("Each answer must have 'text' and 'isCorrect' fields.")
            answer_values.append((question_id, ans['text'], ans['isCorrect'], 'Admin'))
        if answer_values:
            cursor.executemany(answer_query, answer_values)

        step_query = "INSERT INTO tbl_Step (QuestionID, SequenceNo, StepName, CreatedBy) VALUES (%s, %s, %s, %s)"
        step_values = []
        for idx, step in enumerate(steps):
            if 'text' not in step:
                 raise ValueError("Each step must have a 'text' field.")
            step_values.append((question_id, idx + 1, step['text'], 'Admin'))
        cursor.executemany(step_query, step_values)

        conn.commit()

        return jsonify({"status": "success", "message": f"Question ID {question_id} updated successfully!"}), 200

    except Exception as e:
        if conn: conn.rollback()
        print(f"Edit Question API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An unexpected error occurred during question update."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()


@app.route('/api/admin/delete-question/<int:question_id>', methods=['DELETE', 'OPTIONS'])
def delete_question(question_id):
    if request.method == 'OPTIONS': return jsonify(success=True)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        conn.autocommit = False

        cursor.execute("DELETE FROM tbl_Step WHERE QuestionID = %s", (question_id,))
        cursor.execute("DELETE FROM tbl_Answer WHERE QuestionID = %s", (question_id,))
        cursor.execute("DELETE FROM tbl_Question WHERE ID = %s", (question_id,))

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
        if conn and conn.closed == 0:
            conn.close()


@app.route('/api/admin/stories', methods=['GET'])
def get_all_stories():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT DISTINCT
                t.ID AS TopicID,
                t.TopicName,
                (SELECT th.ThemeName FROM tbl_TopicTheme tth JOIN tbl_Theme th ON tth.ThemeID = th.ID WHERE tth.TopicID = t.ID AND tth.IsDefault = TRUE LIMIT 1) AS DefaultTheme
            FROM tbl_Description td
            JOIN tbl_Topic t ON td.TopicID = t.ID
            ORDER BY t.TopicName;
        """
        cursor.execute(query)
        stories = cursor.fetchall()
        return jsonify(stories)
    except Exception as e:
        print(f"Get All Stories API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/admin/delete-story/<int:topic_id>', methods=['DELETE', 'OPTIONS'])
def delete_story(topic_id):
    if request.method == 'OPTIONS': return jsonify(success=True)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        conn.autocommit = False

        # Delete from tbl_TopicTheme first
        cursor.execute("DELETE FROM tbl_TopicTheme WHERE TopicID = %s", (topic_id,))

        cursor.execute("SELECT InteractiveElementID FROM tbl_Description WHERE TopicID = %s AND InteractiveElementID IS NOT NULL", (topic_id,))
        interactive_element_ids_to_delete = [row[0] for row in cursor.fetchall()]

        if interactive_element_ids_to_delete:
            placeholders = ','.join(['%s'] * len(interactive_element_ids_to_delete))
            cursor.execute(f"DELETE FROM tbl_InteractiveElement WHERE ID IN ({placeholders})", tuple(interactive_element_ids_to_delete))

        cursor.execute("DELETE FROM tbl_Description WHERE TopicID = %s", (topic_id,))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Story not found for this topic or already deleted."}), 404

        return jsonify({"status": "success", "message": f"Story for topic ID {topic_id} and its associated interactive elements deleted successfully."}), 200

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
        if conn and conn.closed == 0:
            conn.close()


@app.route('/api/admin/save-story', methods=['POST', 'OPTIONS'])
def save_story():
    if request.method == 'OPTIONS': return jsonify(success=True)

    data = request.get_json()
    topic_id = data.get('topicId')
    story_sections = data.get('storySections')
    default_theme_name = data.get('defaultTheme')

    if not topic_id or story_sections is None:
        return jsonify({"status": "error", "message": "Missing topic ID or story sections."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        conn.autocommit = False

        # Delete existing interactive elements and descriptions for this topic
        cursor.execute("SELECT InteractiveElementID FROM tbl_Description WHERE TopicID = %s AND InteractiveElementID IS NOT NULL", (topic_id,))
        interactive_element_ids_to_delete = [row[0] for row in cursor.fetchall()]

        if interactive_element_ids_to_delete:
            placeholders = ','.join(['%s'] * len(interactive_element_ids_to_delete))
            cursor.execute(f"DELETE FROM tbl_InteractiveElement WHERE ID IN ({placeholders})", tuple(interactive_element_ids_to_delete))

        cursor.execute("DELETE FROM tbl_Description WHERE TopicID = %s", (topic_id,))

        # Handle tbl_TopicTheme updates
        # First, clear existing themes for this topic
        cursor.execute("DELETE FROM tbl_TopicTheme WHERE TopicID = %s", (topic_id,))

        # Then, insert all themes as available for this topic, and mark the selected one as default
        cursor.execute("SELECT ID, ThemeName FROM tbl_Theme")
        all_themes = cursor.fetchall()

        for theme_id, theme_name in all_themes:
            is_default = (theme_name == default_theme_name)
            cursor.execute(
                "INSERT INTO tbl_TopicTheme (TopicID, ThemeID, IsDefault, CreatedBy) VALUES (%s, %s, %s, %s)",
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
                    "INSERT INTO tbl_InteractiveElement (ElementType, Configuration, CreatedBy) "
                    "VALUES (%s, %s, %s) RETURNING ID"
                )
                cursor.execute(
                    interactive_query,
                    (element_type, json.dumps(configuration), 'Admin'),
                )
                interactive_element_id_for_db = cursor.fetchone()[0]
            else:
                conn.rollback()
                return jsonify({"status": "error", "message": f"Section {order} has an invalid content type: {content_type}"}), 400

            desc_query = "INSERT INTO tbl_Description (TopicID, SectionName, DescriptionText, InteractiveElementID, DescriptionOrder, ContentType, CreatedBy) VALUES (%s, %s, %s, %s, %s, %s, %s)"
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
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/story/<int:topic_id>', methods=['GET'])
def get_story_for_topic(topic_id):
    conn = None
    story_payload = {"sections": [], "defaultTheme": None, "availableThemes": []}
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Fetch the default theme for this topic
        cursor.execute("""
            SELECT th.ThemeName
            FROM tbl_TopicTheme tth
            JOIN tbl_Theme th ON tth.ThemeID = th.ID
            WHERE tth.TopicID = %s AND tth.IsDefault = TRUE
            LIMIT 1
        """, (topic_id,))
        default_theme_row = cursor.fetchone()
        if default_theme_row:
            story_payload["defaultTheme"] = default_theme_row['ThemeName']

        # Fetch all available themes for this topic
        cursor.execute("""
            SELECT th.ThemeName
            FROM tbl_TopicTheme tth
            JOIN tbl_Theme th ON tth.ThemeID = th.ID
            WHERE tth.TopicID = %s
            ORDER BY th.ThemeName
        """, (topic_id,))
        available_themes_rows = cursor.fetchall()
        story_payload["availableThemes"] = [row['ThemeName'] for row in available_themes_rows]


        cursor.execute("SELECT ID, SectionName, DescriptionText, InteractiveElementID, DescriptionOrder, ContentType FROM tbl_Description WHERE TopicID = %s ORDER BY DescriptionOrder", (topic_id,))
        sections = cursor.fetchall()

        if not sections:
            # If no sections, but topic exists, still return default and available themes if found
            if story_payload["defaultTheme"] is not None or len(story_payload["availableThemes"]) > 0:
                return jsonify(story_payload)
            else:
                return jsonify({"status": "error", "message": "No story found for this topic."}), 404


        for section in sections:
            section_data = {
                "sectionName": section['SectionName'],
                "order": section['DescriptionOrder'],
                "contentType": section['ContentType']
            }

            if section['InteractiveElementID']:
                interactive_id = section['InteractiveElementID']
                cursor.execute("SELECT ElementType, Configuration FROM tbl_InteractiveElement WHERE ID = %s", (interactive_id,))
                interactive_row = cursor.fetchone()

                if interactive_row:
                    section_data['contentType'] = 'Interactive'
                    section_data['content'] = {
                        "elementType": interactive_row['ElementType'],
                        "configuration": json.loads(interactive_row['Configuration']) # Ensure JSON is parsed
                    }
                else:
                    section_data['contentType'] = 'Paragraph'
                    section_data['content'] = section['DescriptionText']
            else:
                section_data['contentType'] = 'Paragraph'
                section_data['content'] = section['DescriptionText']

            story_payload["sections"].append(section_data)

        return jsonify(story_payload)

    except Exception as e:
        print(f"Get Story API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/story_exists/<int:topic_id>', methods=['GET'])
def story_exists(topic_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM tbl_Description WHERE TopicID = %s", (topic_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            return jsonify({"status": "success", "storyExists": True}), 200
        else:
            return jsonify({"status": "success", "storyExists": False}), 200

    except Exception as e:
        print(f"Story Exists API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error checking story availability."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()


@app.route('/api/progress/<int:user_id>', methods=['GET'])
def get_user_progress(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT up.TopicID, up.Status, t.TopicName, unit.TopicName AS UnitName, s.SubjectName AS CurriculumType
            FROM tbl_UserProgress up
            JOIN tbl_Topic t ON up.TopicID = t.ID
            JOIN tbl_Topic unit ON t.ParentTopicID = unit.ID
            JOIN tbl_Subject s ON unit.SubjectID = s.ID
            WHERE up.UserID = %s
        """
        cursor.execute(query, (user_id,))
        progress = cursor.fetchall()
        return jsonify(progress)
    except Exception as e:
        print(f"Get Progress API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

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
            INSERT INTO tbl_UserProgress (UserID, TopicID, Status)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE Status = %s;
        """
        cursor.execute(query, (user_id, topic_id, status, status))
        conn.commit()

        return jsonify({"status": "success", "message": "Progress updated."}), 200
    except Exception as e:
        print(f"Update Progress API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

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
        cursor.execute("SELECT ID FROM tbl_User WHERE Username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "This username is already taken"}), 409

        placeholder_email = f"{username.lower()}@logicandstories.student"
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute(
            "INSERT INTO tbl_User (Username, Email, PasswordHash, UserType, ParentUserID) VALUES (%s, %s, %s, 'Student', %s)",
            (username, placeholder_email, hashed_password, parent_id)
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Student account created!"}), 201
    except Exception as e:
        print(f"Create Student API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/my-students/<int:parent_id>', methods=['GET'])
def get_my_students(parent_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT ID, Username, CreatedOn FROM tbl_User WHERE ParentUserID = %s", (parent_id,))
        students = cursor.fetchall()
        return jsonify(students), 200
    except Exception as e:
        print(f"Get Students API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/modify-student', methods=['POST', 'OPTIONS'])
def modify_student():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    student_id, new_password = data.get('studentId'), data.get('newPassword')
    if not all([student_id, new_password]):
        return jsonify({"status": "error", "message": "Student ID and new password are required"}), 400

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
            "UPDATE tbl_User SET PasswordHash = %s WHERE ID = %s AND UserType = 'Student'",
            (hashed_password, student_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Student not found or invalid ID"}), 404

        conn.commit()
        return jsonify({"status": "success", "message": "Student password updated successfully!"}), 200
    except Exception as e:
        print(f"Modify Student API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/delete-student/<int:student_id>', methods=['DELETE', 'OPTIONS'])
def delete_student_from_parent_portal(student_id):
    if request.method == 'OPTIONS': return jsonify(success=True)
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tbl_User WHERE ID = %s AND UserType = 'Student'", (student_id,))
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Student not found or already deleted"}), 404

        conn.commit()
        return jsonify({"status": "success", "message": "Student account deleted successfully."}), 200
    except Exception as e:
        print(f"Delete Student API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT ID FROM tbl_User WHERE Email = %s", (email,))
        user = cursor.fetchone()
        if user:
            token, expiry = secrets.token_hex(32), datetime.now() + timedelta(hours=1)
            cursor.execute("UPDATE tbl_User SET ResetToken = %s, ResetTokenExpiry = %s WHERE ID = %s", (token, expiry, user['ID']))
            conn.commit()
            
            # --- UPDATED: Use FRONTEND_BASE_URL for the reset link ---
            reset_link = f"{FRONTEND_BASE_URL}/reset-password.html?token={token}" # Dynamically construct URL
            email_content = RESET_PASSWORD_EMAIL_TEMPLATE_HTML.replace('{{RESET_LINK}}', reset_link)
            
            if send_email(email, "Logic and Stories - Password Reset", email_content):
                return jsonify({"status": "success", "message": "If an account exists, a password reset link has been sent to your email."}), 200
            else:
                # If email sending fails, still return success to avoid leaking user existence
                print(f"Warning: Failed to send password reset email to {email}")
                return jsonify({"status": "success", "message": "If an account exists, a password reset link has been sent to your email (but there was an issue sending the email)."}), 200
            # --- END UPDATED: Send email with reset link ---
        else:
            # Always return success to avoid leaking whether an email exists in the system
            return jsonify({"status": "success", "message": "If an account exists, a password reset link has been sent to your email."}), 200
    except Exception as e:
        print(f"Forgot Password API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

@app.route('/api/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    token, new_password = data.get('token'), data.get('newPassword') # Changed 'password' to 'newPassword' for clarity as per HTML
    if not all([token, new_password]):
        return jsonify({"status": "error", "message": "Token and new password are required."}), 400

    # Server-side password validation
    is_valid, message = validate_password(new_password)
    if not is_valid:
        return jsonify({"status": "error", "message": message}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT ID FROM tbl_User WHERE ResetToken = %s AND ResetTokenExpiry > NOW()", (token,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "message": "Invalid or expired reset token."}), 400
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        cursor.execute(
            "UPDATE tbl_User SET PasswordHash = %s, ResetToken = NULL, ResetTokenExpiry = NULL WHERE ID = %s",
            (hashed_password, user['ID'])
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Password has been reset successfully."}), 200
    except Exception as e:
        print(f"Reset Password API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

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
                topic.ID AS TopicID,
                GROUP_CONCAT(DISTINCT th.ThemeName ORDER BY th.ThemeName SEPARATOR ',') AS AvailableThemes,
                (SELECT dth.ThemeName FROM tbl_TopicTheme tth JOIN tbl_Theme dth ON tth.ThemeID = dth.ID WHERE tth.TopicID = topic.ID AND tth.IsDefault = TRUE LIMIT 1) AS DefaultTheme
            FROM tbl_Topic topic
            JOIN tbl_Topic unit ON topic.ParentTopicID = unit.ID
            JOIN tbl_Subject s ON unit.SubjectID = s.ID
            JOIN tbl_TopicGrade tg ON topic.ID = tg.TopicID
            JOIN tbl_Grade g ON tg.GradeID = g.ID
            LEFT JOIN tbl_TopicTheme tt ON topic.ID = tt.TopicID
            LEFT JOIN tbl_Theme th ON tt.ThemeID = th.ID
            WHERE topic.Active = 1 AND unit.Active = 1
            GROUP BY g.ID, s.ID, unit.ID, topic.ID, g.GradeName, s.SubjectName, unit.TopicName, topic.TopicName
            ORDER BY g.ID, s.ID, unit.ID, topic.ID;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        curriculum_data = {}
        # This mapping is for frontend display, so it's kept here.
        # In a very large app, this might come from a config or DB.
        grade_color_map = { "4th Grade": { "icon": "4th", "color": "fde047" }, "5th Grade": { "icon": "5th", "color": "fb923c" }, "6th Grade": { "icon": "6th", "color": "a78bfa" }, "7th Grade": { "icon": "7th", "color": "60a5fa" }, "8th Grade": { "icon": "8th", "color": "f472b6" }, "9th Grade": { "icon": "9th", "color": "818cf8" }, "10th Grade": { "icon": "10th", "color": "34d399" }, "11th Grade": { "icon": "11th", "color": "22d3ee" }, "Pre-Calculus": { "icon": "Pre-C", "color": "a3e635" }, "Calculus": { "icon": "Calc", "color": "f87171" }, "Statistics": { "icon": "Stats", "color": "c084fc" }, "Contest Math (AMC)": { "icon": "AMC", "color": "e11d48" }, "IB Math AA SL": { "icon": "AA SL", "color": "f9a8d4" }, "IB Math AA HL": { "icon": "AA HL", "color": "f0abfc" }, "IB Math AI SL": { "icon": "AI SL", "color": "a5f3fc" }, "IB Math AI HL": { "icon": "AI HL", "color": "bbf7d0" } }
        for row in rows:
            grade_name, curriculum_type, unit_name, topic_name, topic_id, available_themes_str, default_theme = \
                row['GradeName'], row['CurriculumType'], row['UnitName'], row['TopicName'], row['TopicID'], row['AvailableThemes'], row['DefaultTheme']
            
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
        if conn and conn.closed == 0:
            conn.close()

# --- QUIZ ENDPOINTS ---

@app.route('/api/user/topic-difficulty/<int:user_id>/<int:topic_id>', methods=['GET'])
def get_user_topic_difficulty(user_id, topic_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT CurrentDifficulty FROM tbl_UserTopicDifficulty WHERE UserID = %s AND TopicID = %s"
        cursor.execute(query, (user_id, topic_id))
        result = cursor.fetchone()
        difficulty = result['CurrentDifficulty'] if result else 1
        return jsonify({"status": "success", "difficulty": difficulty}), 200
    except Exception as e:
        print(f"Get User Topic Difficulty API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching user difficulty."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

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
            INSERT INTO tbl_UserTopicDifficulty (UserID, TopicID, CurrentDifficulty)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE CurrentDifficulty = %s;
        """
        cursor.execute(query, (user_id, topic_id, new_difficulty, new_difficulty))
        conn.commit()
        return jsonify({"status": "success", "message": "User difficulty updated."}), 200
    except Exception as e:
        print(f"Update User Topic Difficulty API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error updating user difficulty."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()


@app.route('/api/quiz/question/<int:user_id>/<int:topic_id>/<int:difficulty_level>', methods=['GET'])
def get_quiz_question(user_id, topic_id, difficulty_level):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        difficulty_level = max(1, min(5, difficulty_level))

        query = """
            SELECT Q.ID, Q.QuestionName, Q.QuestionType, Q.DifficultyRating
            FROM tbl_Question Q
            WHERE Q.TopicID = %s AND Q.DifficultyRating = %s
            ORDER BY RAND() LIMIT 1;
        """
        cursor.execute(query, (topic_id, difficulty_level))
        question = cursor.fetchone()

        if not question:
            for offset in range(1, 5):
                lower_diff = difficulty_level - offset
                upper_diff = difficulty_level + offset

                if lower_diff >= 1:
                    cursor.execute(query, (topic_id, lower_diff))
                    question = cursor.fetchone()
                    if question: break
                if upper_diff <= 5 and not question:
                    cursor.execute(query, (topic_id, upper_diff))
                    question = cursor.fetchone()
                    if question: break

            if not question:
                query_any = """
                    SELECT Q.ID, Q.QuestionName, Q.QuestionType, Q.DifficultyRating
                    FROM tbl_Question Q
                    WHERE Q.TopicID = %s
                    ORDER BY RAND() LIMIT 1;
                """
                cursor.execute(query_any, (topic_id,))
                question = cursor.fetchone()

        if not question:
            return jsonify({"status": "error", "message": "No questions found for this topic."}), 404

        question_id = question['ID']
        question_type = question['QuestionType']

        answers = []
        steps = []

        if question_type == 'MultipleChoice':
            cursor.execute("SELECT AnswerName, IsCorrect FROM tbl_Answer WHERE QuestionID = %s", (question_id,))
            answers = cursor.fetchall()
        elif question_type == 'OpenEnded':
            cursor.execute("SELECT AnswerName, IsCorrect FROM tbl_Answer WHERE QuestionID = %s AND IsCorrect = TRUE", (question_id,))
            correct_answer_row = cursor.fetchone()
            if correct_answer_row:
                answers = [{"AnswerName": correct_answer_row['AnswerName'], "IsCorrect": True}]

        cursor.execute("SELECT StepName FROM tbl_Step WHERE QuestionID = %s ORDER BY SequenceNo", (question_id,))
        steps = [s['StepName'] for s in cursor.fetchall()]

        response_data = {
            "status": "success",
            "question": {
                "id": question['ID'],
                "text": question['QuestionName'],
                "type": question['QuestionType'],
                "difficulty": question['DifficultyRating'],
                "answers": answers,
                "steps": steps
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Get Quiz Question API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching quiz question."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

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
            INSERT INTO tbl_FlagReport (UserID, FlaggedItemID, ItemType, Reason, Status)
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
        if conn and conn.closed == 0:
            conn.close()


@app.route('/api/admin/flagged-items', methods=['GET'])
def get_flagged_items():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT
                fr.ID AS FlagID,
                fr.UserID,
                u.Username AS ReporterUsername,
                fr.FlaggedItemID,
                fr.ItemType,
                CASE
                    WHEN fr.ItemType = 'Question' THEN q.QuestionName
                    WHEN fr.ItemType = 'Story' THEN t.TopicName
                    ELSE 'N/A'
                END AS ItemName,
                fr.Reason,
                fr.Status,
                fr.ReportedOn,
                fr.ResolvedOn,
                ru.Username AS ResolvedByUsername
            FROM tbl_FlagReport fr
            JOIN tbl_User u ON fr.UserID = u.ID
            LEFT JOIN tbl_Question q ON fr.ItemType = 'Question' AND fr.FlaggedItemID = q.ID
            LEFT JOIN tbl_Topic t ON fr.ItemType = 'Story' AND fr.FlaggedItemID = t.ID
            LEFT JOIN tbl_User ru ON fr.ResolvedBy = ru.ID
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
        if conn and conn.closed == 0:
            conn.close()


@app.route('/api/admin/update-flag-status/<int:flag_id>', methods=['PUT', 'OPTIONS'])
def update_flag_status(flag_id):
    if request.method == 'OPTIONS': return jsonify(success=True)
    data = request.get_json()
    new_status = data.get('status')
    admin_id = data.get('adminId')

    if not all([new_status, admin_id]):
        return jsonify({"status": "error", "message": "Missing status or admin ID."}), 400

    if new_status not in ['Pending', 'Reviewed', 'Dismissed']:
        return jsonify({"status": "error", "message": "Invalid status. Must be 'Pending', 'Reviewed', or 'Dismissed'."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        update_query = """
            UPDATE tbl_FlagReport
            SET Status = %s, ResolvedOn = NOW(), ResolvedBy = %s
            WHERE ID = %s;
        """
        cursor.execute(update_query, (new_status, admin_id, flag_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Flag report not found or status already set."}), 404

        return jsonify({"status": "success", "message": f"Flag {flag_id} status updated to {new_status}."}), 200
    except Exception as e:
        print(f"Update Flag Status API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error updating flag status."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()

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
            INSERT INTO tbl_QuestionAttempt (UserID, QuestionID, UserAnswer, IsCorrect, DifficultyAtAttempt)
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
        if conn and conn.closed == 0:
            conn.close()

# --- ADMIN ENDPOINT TO GET ALL QUESTION ATTEMPTS ---
@app.route('/api/admin/question-attempts', methods=['GET'])
def get_all_question_attempts():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT
                qa.ID AS AttemptID,
                qa.AttemptTime,
                qa.UserAnswer,
                qa.IsCorrect,
                qa.DifficultyAtAttempt,
                u.Username AS AttemptingUsername,
                q.QuestionName AS QuestionText,
                t.TopicName AS TopicName,
                unit.TopicName AS UnitName,
                s.SubjectName AS CurriculumType,
                GROUP_CONCAT(TRIM(CASE WHEN a.IsCorrect = TRUE THEN a.AnswerName ELSE NULL END)) AS CorrectAnswer
            FROM tbl_QuestionAttempt qa
            JOIN tbl_User u ON qa.UserID = u.ID
            JOIN tbl_Question q ON qa.QuestionID = q.ID
            JOIN tbl_Topic t ON q.TopicID = t.ID
            JOIN tbl_Topic unit ON t.ParentTopicID = unit.ID
            JOIN tbl_Subject s ON unit.SubjectID = s.ID
            LEFT JOIN tbl_Answer a ON q.ID = a.QuestionID AND a.IsCorrect = TRUE
            GROUP BY qa.ID, qa.AttemptTime, qa.UserAnswer, qa.IsCorrect, qa.DifficultyAtAttempt, u.Username, q.QuestionName, t.TopicName, unit.TopicName, s.SubjectName
            ORDER BY qa.AttemptTime DESC;
        """
        cursor.execute(query)
        attempts = cursor.fetchall()

        return jsonify(attempts), 200
    except Exception as e:
        print(f"Get All Question Attempts API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error fetching question attempts."}), 500
    finally:
        if conn and conn.closed == 0:
            conn.close()


# =================================================================
#  3. FRONTEND ROUTES (Serve HTML Pages)
# =================================================================

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/admin-login.html')
def serve_admin_login():
    return render_template('admin-login.html')

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
    return render_template('parent-login.html')

@app.route('/student-login.html')
def serve_student_login():
    return render_template('student-login.html')

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

@app.route('/story-player.html')
def serve_story_player():
    return render_template('story-player.html')

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
