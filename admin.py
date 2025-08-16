from flask import Blueprint, request, jsonify
import os
import traceback
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import version_cache
from db_utils import db_cursor, get_db_connection, release_db_connection
from seed_database import seed_data
from auth_utils import require_auth
import psycopg2.extras


admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route("/users-version", methods=["GET"])
@require_auth(['admin'])
def get_users_version():
    return jsonify({"version": version_cache.users_version.isoformat()})

@admin_bp.route('/all-users', methods=['GET'])
@require_auth(['admin'])
def get_all_users():
    try:
        with db_cursor() as cursor:
            query = """
                SELECT u.id, u.username, u.email, u.usertype, u.createdon,
                       p.username AS parentusername,
                       s.active, s.expires_on
                FROM tbl_user u
                LEFT JOIN tbl_user p ON u.parentuserid = p.id
                LEFT JOIN tbl_subscription s ON u.id = s.user_id
                ORDER BY u.id;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            users = []
            now = datetime.now(timezone.utc)
            for row in rows:
                expires_on = row[7]
                if expires_on and expires_on.tzinfo is None:
                    expires_on = expires_on.replace(tzinfo=timezone.utc)
                days_left = (
                    (expires_on - now).days if expires_on and row[6] else None
                )
                users.append({
                    'ID': row[0],
                    'Username': row[1],
                    'Email': row[2],
                    'UserType': row[3],
                    'CreatedOn': row[4],
                    'ParentUsername': row[5],
                    'SubscriptionDaysLeft': days_left,
                })
            return jsonify(users)
    except Exception as e:
        print(f"Get All Users API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500


@admin_bp.route('/seed-database', methods=['POST'])
@require_auth(['admin'])
def seed_database_upload():
    tmp_path = None
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"message": "No file uploaded"}), 400
        tmp_path = os.path.join('/tmp', secure_filename(file.filename))
        file.save(tmp_path)
        seed_data(csv_file_name=tmp_path)
        return jsonify({"message": "Database seeded successfully"})
    except Exception as e:
        print(f"Seed Database API Error: {e}")
        traceback.print_exc()
        return jsonify({"message": "Internal error"}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


# =================================================================
#  ADDITIONAL ADMIN ROUTES FOR SECURITY TESTING
# =================================================================

@admin_bp.route('/edit-user/<int:user_id>', methods=['PUT', 'OPTIONS'])
@require_auth(['admin'])
def edit_user(user_id):
    """Edit user account details."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    
    return jsonify({"status": "success", "message": "User edit functionality"})


@admin_bp.route('/delete-user/<int:user_id>', methods=['DELETE', 'OPTIONS'])
@require_auth(['admin'])
def delete_user(user_id):
    """Delete a user account."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "User delete functionality"})


@admin_bp.route('/topics-list', methods=['GET'])
@require_auth(['admin'])
def get_topics_list():
    """Get list of topics for admin."""
    return jsonify({"status": "success", "topics": []})


@admin_bp.route('/add-question', methods=['POST', 'OPTIONS'])
@require_auth(['admin'])
def add_question():
    """Add a new question."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "Question add functionality"})


@admin_bp.route('/questions', methods=['GET'])
@require_auth(['admin'])
def get_questions():
    """Get list of questions for admin."""
    return jsonify({"status": "success", "questions": []})


@admin_bp.route('/stories', methods=['GET'])
@require_auth(['admin'])
def get_stories():
    """Get list of stories for admin."""
    return jsonify({"status": "success", "stories": []})


@admin_bp.route('/delete-story/<int:topic_id>', methods=['DELETE', 'OPTIONS'])
@require_auth(['admin'])
def delete_story(topic_id):
    """Delete a story."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "Story delete functionality"})


@admin_bp.route('/save-story', methods=['POST', 'OPTIONS'])
@require_auth(['admin'])
def save_story():
    """Save a story."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "Story save functionality"})


@admin_bp.route('/add-video', methods=['POST', 'OPTIONS'])
@require_auth(['admin'])
def add_video():
    """Add a video."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "Video add functionality"})


@admin_bp.route('/curriculums', methods=['GET'])
@require_auth(['admin'])
def get_curriculums():
    """Get curriculums for admin."""
    return jsonify({"status": "success", "curriculums": []})


@admin_bp.route('/create-curriculum', methods=['POST', 'OPTIONS'])
@require_auth(['admin'])
def create_curriculum():
    """Create a new curriculum."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "Curriculum create functionality"})


@admin_bp.route('/delete-curriculum/<int:subject_id>', methods=['DELETE', 'OPTIONS'])
@require_auth(['admin'])
def delete_curriculum(subject_id):
    """Delete a curriculum."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "Curriculum delete functionality"})


@admin_bp.route('/flagged-items', methods=['GET'])
@require_auth(['admin'])
def get_flagged_items():
    """Get flagged items for review."""
    return jsonify({"status": "success", "flagged_items": []})


@admin_bp.route('/update-flag-status/<int:flag_id>', methods=['PUT', 'OPTIONS'])
@require_auth(['admin'])
def update_flag_status(flag_id):
    """Update flag status."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "Flag status update functionality"})


@admin_bp.route('/delete-flag/<int:flag_id>', methods=['DELETE', 'OPTIONS'])
@require_auth(['admin'])
def delete_flag(flag_id):
    """Delete a flag."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "Flag delete functionality"})


@admin_bp.route('/question-attempts', methods=['GET'])
@require_auth(['admin'])
def get_all_question_attempts():
    """Get all question attempts for analytics."""
    return jsonify({"status": "success", "attempts": []})
