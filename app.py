import psycopg2
import psycopg2.extras
from psycopg2 import sql
from flask import Flask, jsonify, request, render_template, send_from_directory, redirect, url_for
from flask_cors import CORS
from extensions import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from version_cache import update_users_version
import traceback
import json
import random
import os
import re
from utils import validate_password
from env_validator import validate_environment
from auth_utils import require_auth, require_user_access

# =================================================================
#  1. SETUP & CONFIGURATION
# =================================================================

# Validate environment variables before application setup (skip during testing)
if not os.environ.get('PYTEST_CURRENT_TEST'):
    validate_environment(fail_fast=True)

app = Flask(__name__)

# Load configuration
from config import get_config
config = get_config()
app.config.from_object(config)

bcrypt.init_app(app)

# Configure Flask-CORS
CORS(app, origins=["https://logicandstories.com", "https://www.logicandstories.com"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     headers=["Content-Type", "Authorization"])


@app.after_request
def inject_preferences_script(response):
    """Ensure the preferences script is added to every HTML response."""
    if response.direct_passthrough:
        return response

    content_type = response.headers.get('Content-Type', '').lower()
    if content_type.startswith('text/html'):
        script_tag = "<script src='/static/js/preferences.js'></script>"
        data = response.get_data(as_text=True)
        if script_tag not in data:
            new_data, count = re.subn(r'</body>', f'{script_tag}</body>', data, flags=re.IGNORECASE)
            if count:
                response.set_data(new_data)
    return response


# --- DATABASE CONFIGURATION ---
from db_utils import get_db_connection, release_db_connection, ensure_topicsubject_table

# Import blueprints
from auth import auth_bp
from admin import admin_bp
from quiz import quiz_bp
from content import content_bp
from user_management import user_mgmt_bp
from flagging import flagging_bp
from subscription import subscription_bp
from routes.analytics import analytics_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(content_bp)
app.register_blueprint(user_mgmt_bp)
app.register_blueprint(flagging_bp)
app.register_blueprint(subscription_bp)
app.register_blueprint(analytics_bp)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route('/get_curriculums', methods=['GET'])
def get_curriculums_route():
    """Legacy route for get_curriculums - simple implementation."""
    mock_curriculums = ["Common Core", "IB", "AP"]
    from db_utils import get_db_connection, release_db_connection
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT TRIM(subjectname) FROM tbl_subject ORDER BY TRIM(subjectname);")
        rows = cursor.fetchall()
        curriculums = [row[0] for row in rows if row[0]]
        return jsonify(curriculums) if curriculums else jsonify(mock_curriculums)
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"get_curriculums error: {e}")
        return jsonify(mock_curriculums)
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


# =================================================================
#  STATIC ROUTES AND TEMPLATE SERVING
# =================================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin-login.html')
def admin_login():
    return render_template('iygighukijh.html')


@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')


@app.route('/progress-dashboard.html')
def progress_dashboard():
    return render_template('progress-dashboard.html')


@app.route('/settings.html')
def settings():
    return render_template('settings.html')


@app.route('/quiz-player.html')
def quiz_player():
    return render_template('quiz-player.html')


@app.route('/story-player.html')
def story_player():
    return render_template('story-player.html')


@app.route('/video-player.html')
def video_player():
    return render_template('video-player.html')


@app.route('/leaderboard.html')
def leaderboard():
    return render_template('leaderboard.html')


@app.route('/parent-portal.html')
def parent_portal():
    return render_template('parent-portal.html')


@app.route('/choose-plan.html')
def choose_plan():
    return render_template('choose-plan.html')


@app.route('/blog.html')
def blog():
    return render_template('blog.html')


@app.route('/terms-of-service.html')
def terms_of_service():
    return render_template('terms-of-service.html')


@app.route('/privacy-policy.html')
def privacy_policy():
    return render_template('privacy-policy.html')


@app.route('/signin.html')
def signin():
    return render_template('signin.html')


@app.route('/signup.html')
def signup():
    return render_template('signup.html')


@app.route('/forgot-password.html')
def forgot_password():
    return render_template('forgot-password.html')


@app.route('/reset-password.html')
def reset_password():
    return render_template('reset-password.html')


@app.route('/404.html')
def not_found_page():
    return render_template('404.html')


# =================================================================
#  MISSING API ENDPOINTS 
# =================================================================

@app.route('/api/video/<int:topic_id>', methods=['GET'])
def get_video(topic_id):
    """Get video URL for a specific topic."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT youtubeurl FROM tbl_video WHERE topicid = %s", (topic_id,))
        result = cursor.fetchone()
        if result:
            return jsonify(success=True, youtubeUrl=result[0])
        else:
            return jsonify(success=False, message="Video not found"), 404
    except Exception as e:
        print(f"Get Video API Error: {e}")
        return jsonify(success=False, message="Failed to fetch video"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/story/<int:topic_id>', methods=['GET'])
def get_story(topic_id):
    """Get story content for a specific topic."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT story FROM tbl_story WHERE topicid = %s", (topic_id,))
        result = cursor.fetchone()
        if result:
            # Replace newlines with <br> tags for HTML display
            formatted_story = result[0].replace('\n', '<br>')
            return jsonify(success=True, story=formatted_story)
        else:
            return jsonify(success=False, message="Story not found"), 404
    except Exception as e:
        print(f"Get Story API Error: {e}")
        return jsonify(success=False, message="Failed to fetch story"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/story-exists/<int:topic_id>', methods=['GET'])
def story_exists(topic_id):
    """Check if a story exists for a topic."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tbl_story WHERE topicid = %s", (topic_id,))
        count = cursor.fetchone()[0]
        return jsonify(storyExists=count > 0, isPlaceholder=count == 0)
    except Exception as e:
        print(f"Story Exists API Error: {e}")
        return jsonify(storyExists=False, isPlaceholder=True), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/quiz-exists/<int:topic_id>', methods=['GET'])
def quiz_exists(topic_id):
    """Check if quiz questions exist for a topic."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tbl_question WHERE topicid = %s", (topic_id,))
        count = cursor.fetchone()[0]
        return jsonify(status="success", quizExists=count > 0, questionCount=count)
    except Exception as e:
        print(f"Quiz Exists API Error: {e}")
        return jsonify(status="success", quizExists=False, questionCount=0)
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/dashboard/<int:user_id>', methods=['GET'])
@require_auth(['student', 'admin'])
def get_dashboard(user_id):
    """Get dashboard data for a user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic user info
        cursor.execute("SELECT username FROM tbl_user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify(success=False, message="User not found"), 404
            
        # Get progress data (simplified for now)
        dashboard_data = {
            "username": user[0],
            "totalTopics": 0,
            "completedTopics": 0,
            "currentScore": 0
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        print(f"Dashboard API Error: {e}")
        return jsonify(success=False, message="Failed to fetch dashboard"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard data."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Simple leaderboard query (fixed column references)
        query = """
            SELECT u.id, u.username, 
                   COALESCE(AVG(qr.score), 0) as average_score,
                   COUNT(qr.id) as attempts
            FROM tbl_user u
            LEFT JOIN tbl_quiz_result qr ON u.id = qr.user_id
            WHERE u.usertype = 'Student'
            GROUP BY u.id, u.username
            ORDER BY average_score DESC
            LIMIT 10
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        leaderboard = []
        for row in results:
            leaderboard.append({
                "id": row[0],
                "username": row[1], 
                "average_score": float(row[2]),
                "attempts": row[3]
            })
        
        return jsonify(leaderboard)
    except Exception as e:
        print(f"Leaderboard API Error: {e}")
        return jsonify([]), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/curriculum-table', methods=['GET'])
def get_curriculum_table():
    """Get curriculum table data."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fixed query without lesson_id reference
        query = """
            SELECT DISTINCT
                g.gradename,
                s.subjectname AS curriculumtype,
                t.topicname AS unitname,
                t.topicname
            FROM tbl_topic t
            LEFT JOIN tbl_topicsubject ts ON t.id = ts.topicid
            LEFT JOIN tbl_subject s ON ts.subjectid = s.id
            LEFT JOIN tbl_grade g ON g.subjectid = s.id
            ORDER BY gradename, curriculumtype, unitname, topicname
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        curriculum_data = []
        for row in results:
            curriculum_data.append({
                "gradename": row[0] or "Unknown Grade",
                "curriculumtype": row[1] or "Unknown Curriculum", 
                "unitname": row[2] or "Unknown Unit",
                "topicname": row[3] or "Unknown Topic"
            })
        
        return jsonify(curriculum_data)
    except Exception as e:
        print(f"Get Curriculum Table API Error: {e}")
        return jsonify([]), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/subscription-status/<int:user_id>', methods=['GET'])
@require_auth(['student', 'parent', 'admin'])
def get_subscription_status(user_id):
    """Get subscription status for a user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT active, expires_on FROM tbl_subscription 
            WHERE user_id = %s
        """, (user_id,))
        subscription = cursor.fetchone()
        
        if not subscription:
            return jsonify(active=False, expires_on=None)
            
        return jsonify(active=subscription[0], expires_on=subscription[1])
    except Exception as e:
        print(f"Subscription Status API Error: {e}")
        return jsonify(active=False), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/cancel-subscription/<int:user_id>', methods=['POST'])
@require_auth(['student', 'parent', 'admin'])
def cancel_subscription(user_id):
    """Cancel subscription for a user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tbl_subscription SET active = false 
            WHERE user_id = %s
        """, (user_id,))
        
        if cursor.rowcount == 0:
            return jsonify(success=False, message="No subscription found"), 400
            
        conn.commit()
        return jsonify(success=True, message="Subscription cancelled")
    except Exception as e:
        print(f"Cancel Subscription API Error: {e}")
        if conn:
            conn.rollback()
        return jsonify(success=False, message="Failed to cancel subscription"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/renew-subscription/<int:user_id>', methods=['POST'])
@require_auth(['admin'])
def renew_subscription(user_id):
    """Renew subscription for a user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Renew for 30 days
        from datetime import datetime, timedelta
        new_expires = datetime.now() + timedelta(days=30)
        
        cursor.execute("""
            UPDATE tbl_subscription 
            SET active = true, expires_on = %s
            WHERE user_id = %s
        """, (new_expires, user_id))
        
        if cursor.rowcount == 0:
            # Create new subscription if none exists
            cursor.execute("""
                INSERT INTO tbl_subscription (user_id, active, expires_on)
                VALUES (%s, true, %s)
            """, (user_id, new_expires))
            
        conn.commit()
        return jsonify(success=True, message="Subscription renewed")
    except Exception as e:
        print(f"Renew Subscription API Error: {e}")
        if conn:
            conn.rollback()
        return jsonify(success=False, message="Failed to renew subscription"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/open-flags', methods=['GET'])
def get_open_flags():
    """Get open flag count."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tbl_flag WHERE status = 'open'")
        count = cursor.fetchone()[0]
        
        return jsonify({"success": True, "open_flags": count})
    except Exception as e:
        print(f"Open Flags API Error: {e}")
        return jsonify({"success": True, "open_flags": 0}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/flag-page-error', methods=['POST'])
def flag_page_error():
    """Flag a page error."""
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify(success=False, message="Missing description"), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tbl_flag (item_type, description, page_path, status)
            VALUES (%s, %s, %s, %s)
        """, ('Page', data['description'], data.get('pagePath', ''), 'open'))
        
        conn.commit()
        return jsonify(success=True, message="Error flagged successfully"), 201
    except Exception as e:
        print(f"Flag Page Error API Error: {e}")
        if conn:
            conn.rollback()
        return jsonify(success=False, message="Failed to flag error"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@app.route('/api/record-question-attempt', methods=['POST'])
@require_auth(['student', 'admin'])
def record_question_attempt():
    """Record a question attempt."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    
    user_id = data.get('userId')
    question_id = data.get('questionId')
    user_answer = data.get('userAnswer')
    is_correct = data.get('isCorrect')
    difficulty = data.get('difficultyAtAttempt')
    
    # Validate required fields
    if None in (user_answer, is_correct, difficulty):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    # Check for zero IDs (allowed per test requirements)
    if user_id is None or question_id is None:
        return jsonify({"status": "error", "message": "Missing userId or questionId"}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tbl_question_attempt 
            (user_id, question_id, user_answer, is_correct, difficulty_at_attempt, time_taken_seconds)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, question_id, user_answer, is_correct, difficulty, data.get('timeTakenSeconds')))
        
        conn.commit()
        return jsonify({"status": "success", "message": "Question attempt recorded"}), 201
        
    except Exception as e:
        print(f"Record Question Attempt Error: {e}")
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "message": "Failed to record attempt"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


# =================================================================
#  ERROR HANDLERS
# =================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify(success=False, message="Internal server error"), 500


# =================================================================
#  APPLICATION STARTUP
# =================================================================

if __name__ == '__main__':
    # Ensure database tables exist
    conn = None
    try:
        conn = get_db_connection()
        ensure_topicsubject_table(conn)
    except Exception as e:
        print(f"Warning: Could not initialize database tables: {e}")
    finally:
        if conn:
            release_db_connection(conn)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)