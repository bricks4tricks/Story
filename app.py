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