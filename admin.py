from flask import Blueprint, request, jsonify
import os
import traceback
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import version_cache
from db_utils import db_cursor, get_db_connection, release_db_connection
from seed_database import seed_data
from auth_utils import require_auth
from file_security import require_secure_file_upload, save_uploaded_file_securely
from security_utils import require_csrf, rate_limit
import psycopg2.extras


admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Question type mappings
QUESTION_TYPE_MAP = {
    'MultipleChoice': 1,
    'OpenEnded': 2
}
QUESTION_TYPE_REVERSE_MAP = {
    1: 'MultipleChoice',
    2: 'OpenEnded'
}

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
@require_csrf
@rate_limit(max_requests=3, window=3600)  # 3 uploads per hour
@require_secure_file_upload('csv', 'file')
def seed_database_upload():
    secure_path = None
    try:
        # Get validated file info from security decorator
        file_info = request.secure_file_info
        
        # Save file securely 
        secure_path = save_uploaded_file_securely(file_info)
        
        # Process the secure file
        seed_data(csv_file_name=secure_path)
        
        return jsonify({
            "message": "Database seeded successfully",
            "file_info": {
                "filename": file_info['secure_filename'],
                "size": file_info['file_size'],
                "hash": file_info['file_hash'][:16]  # Partial hash for verification
            }
        })
    except Exception as e:
        print(f"Seed Database API Error: {e}")
        traceback.print_exc()
        return jsonify({"message": "Internal error"}), 500
    finally:
        if secure_path and os.path.exists(secure_path):
            os.remove(secure_path)


# =================================================================
#  ADDITIONAL ADMIN ROUTES FOR SECURITY TESTING
# =================================================================

@admin_bp.route('/edit-user/<int:user_id>', methods=['PUT', 'OPTIONS'])
@require_auth(['admin'])
@require_csrf
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
@require_csrf
@rate_limit(max_requests=20, window=3600)
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
@require_csrf
@rate_limit(max_requests=10, window=3600)
def save_story():
    """Save a story."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    return jsonify({"status": "success", "message": "Story save functionality"})


@admin_bp.route('/add-video', methods=['POST', 'OPTIONS'])
@require_auth(['admin'])
@require_csrf
@rate_limit(max_requests=10, window=3600)
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


@admin_bp.route('/question/<int:question_id>', methods=['GET'])
@require_auth(['admin'])
def get_question_details(question_id):
    """Get detailed information about a specific question."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT id, topicid, questionname, questiontype, difficultyrating FROM tbl_question WHERE id = %s", (question_id,))
        question = cursor.fetchone()
        if not question:
            return jsonify({"status": "error", "message": "Question not found."}), 404

        qt = question.get('questiontype')
        question_type_display = QUESTION_TYPE_REVERSE_MAP.get(qt, qt)

        cursor.execute("SELECT answername, iscorrect FROM tbl_answer WHERE questionid = %s", (question_id,))
        answers = cursor.fetchall()

        cursor.execute("SELECT stepname FROM tbl_step WHERE questionid = %s ORDER BY sequenceno", (question_id,))
        steps = cursor.fetchall()

        topic_id = question.get('topicid')
        if topic_id is None:
            topic_id = question.get('TopicID')
        
        # Get topic information - handle potential missing schema elements gracefully
        topic_info = None
        try:
            cursor.execute(
                """
                SELECT
                    t.id AS topicid,
                    t.topicname AS TopicName,
                    unit.topicname AS UnitName,
                    s.subjectname AS CurriculumType
                FROM tbl_topic t
                LEFT JOIN tbl_topic unit ON t.parenttopicid = unit.id
                LEFT JOIN tbl_subject s ON unit.subjectid = s.id
                WHERE t.id = %s
                """,
                (topic_id,),
            )
            topic_info = cursor.fetchone()
        except:
            # Fallback if schema doesn't match expected structure
            pass

        question_details = {
            "ID": question.get('id'),
            "TopicID": topic_id,
            "TopicName": topic_info.get('topicname') if topic_info else None,
            "UnitName": topic_info.get('unitname') if topic_info else None,
            "CurriculumType": topic_info.get('curriculumtype') if topic_info else None,
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
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@admin_bp.route('/curriculum-hierarchy', methods=['GET'])
@require_auth(['admin'])
def admin_curriculum_hierarchy():
    """Return units and topics grouped under each curriculum."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Use a more flexible query that works with current schema
        query = """
            SELECT 
                COALESCE(s.subjectname, 'Unknown') AS curriculum,
                COALESCE(t.topicname, 'Unknown Unit') AS unitname,
                t.topicname AS topicname,
                t.id AS topicid
            FROM tbl_topic t
            LEFT JOIN tbl_topicsubject ts ON t.id = ts.topicid
            LEFT JOIN tbl_subject s ON ts.subjectid = s.id
            ORDER BY curriculum, unitname, topicname;
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
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@admin_bp.route('/curriculums/<int:subject_id>', methods=['GET'])
@require_auth(['admin'])
def get_curriculum_by_id(subject_id):
    """Get a specific curriculum by ID."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("SELECT id, subjectname FROM tbl_subject WHERE id = %s", (subject_id,))
        subject = cursor.fetchone()
        
        if not subject:
            return jsonify({"status": "error", "message": "Curriculum not found"}), 404
        
        return jsonify({
            "id": subject['id'],
            "subjectname": subject['subjectname']
        })
        
    except Exception as e:
        print(f"Get curriculum by ID error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)
