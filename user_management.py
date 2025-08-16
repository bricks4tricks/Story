"""
User management blueprint for student/parent operations and progress tracking.
Handles user-related API endpoints excluding authentication.
"""

from flask import Blueprint, jsonify, request
import traceback
from auth_utils import require_auth, require_user_access
from db_utils import get_db_connection, release_db_connection
from version_cache import update_users_version

user_mgmt_bp = Blueprint('user_mgmt', __name__, url_prefix='/api')

# =================================================================
#  USER MANAGEMENT ENDPOINTS
# =================================================================

@user_mgmt_bp.route('/progress/<int:user_id>', methods=['GET'])
@require_user_access
def get_progress(user_id):
    """Get user progress data."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get quiz progress
        cursor.execute("""
            SELECT 
                t.name as topic_name,
                qr.score,
                qr.total_questions,
                qr.created_at
            FROM tbl_quiz_result qr
            JOIN tbl_topic t ON qr.topic_id = t.id
            WHERE qr.user_id = %s
            ORDER BY qr.created_at DESC
        """, (user_id,))
        
        quiz_results = []
        for row in cursor.fetchall():
            quiz_results.append({
                'topic_name': row[0],
                'score': row[1],
                'total_questions': row[2],
                'completed_at': row[3].isoformat() if row[3] else None
            })
        
        # Get story progress
        cursor.execute("""
            SELECT 
                t.name as topic_name,
                sp.created_at
            FROM tbl_story_progress sp
            JOIN tbl_topic t ON sp.topic_id = t.id
            WHERE sp.user_id = %s
            ORDER BY sp.created_at DESC
        """, (user_id,))
        
        story_progress = []
        for row in cursor.fetchall():
            story_progress.append({
                'topic_name': row[0],
                'completed_at': row[1].isoformat() if row[1] else None
            })
        
        return jsonify(
            success=True,
            quiz_results=quiz_results,
            story_progress=story_progress
        )
        
    except Exception as e:
        print(f"Get Progress API Error: {e}")
        return jsonify(success=False, message="Failed to fetch progress"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@user_mgmt_bp.route('/progress/update', methods=['POST'])
@require_auth(['student', 'parent'])
def update_progress():
    """Update user progress for stories or videos."""
    data = request.get_json()
    user_id = data.get('user_id')
    topic_id = data.get('topic_id')
    content_type = data.get('content_type')  # 'story' or 'video'
    
    if not all([user_id, topic_id, content_type]):
        return jsonify(success=False, message="Missing required fields"), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if content_type == 'story':
            # Record story completion
            cursor.execute("""
                INSERT INTO tbl_story_progress (user_id, topic_id, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id, topic_id) DO NOTHING
            """, (user_id, topic_id))
        elif content_type == 'video':
            # Record video completion
            cursor.execute("""
                INSERT INTO tbl_video_progress (user_id, topic_id, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id, topic_id) DO NOTHING
            """, (user_id, topic_id))
        
        conn.commit()
        return jsonify(success=True, message="Progress updated successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Update Progress API Error: {e}")
        return jsonify(success=False, message="Failed to update progress"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@user_mgmt_bp.route('/dashboard/<int:user_id>', methods=['GET'])
@require_user_access
def get_dashboard_data(user_id):
    """Get dashboard data for a user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("""
            SELECT username, email, usertype, plan
            FROM tbl_user 
            WHERE id = %s
        """, (user_id,))
        
        user_info = cursor.fetchone()
        if not user_info:
            return jsonify(success=False, message="User not found"), 404
        
        # Get recent quiz results
        cursor.execute("""
            SELECT 
                t.name as topic_name,
                qr.score,
                qr.total_questions,
                qr.created_at
            FROM tbl_quiz_result qr
            JOIN tbl_topic t ON qr.topic_id = t.id
            WHERE qr.user_id = %s
            ORDER BY qr.created_at DESC
            LIMIT 10
        """, (user_id,))
        
        recent_quizzes = []
        for row in cursor.fetchall():
            recent_quizzes.append({
                'topic_name': row[0],
                'score': row[1],
                'total_questions': row[2],
                'percentage': (row[1] / row[2] * 100) if row[2] > 0 else 0,
                'completed_at': row[3].isoformat() if row[3] else None
            })
        
        # Get progress statistics
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT sp.topic_id) as stories_completed,
                COUNT(DISTINCT vp.topic_id) as videos_completed,
                COUNT(DISTINCT qr.topic_id) as quizzes_completed
            FROM tbl_user u
            LEFT JOIN tbl_story_progress sp ON u.id = sp.user_id
            LEFT JOIN tbl_video_progress vp ON u.id = vp.user_id
            LEFT JOIN tbl_quiz_result qr ON u.id = qr.user_id
            WHERE u.id = %s
        """, (user_id,))
        
        stats = cursor.fetchone()
        
        dashboard_data = {
            'user': {
                'username': user_info[0],
                'email': user_info[1],
                'usertype': user_info[2],
                'plan': user_info[3]
            },
            'stats': {
                'stories_completed': stats[0] or 0,
                'videos_completed': stats[1] or 0,
                'quizzes_completed': stats[2] or 0
            },
            'recent_quizzes': recent_quizzes
        }
        
        return jsonify(success=True, data=dashboard_data)
        
    except Exception as e:
        print(f"Dashboard API Error: {e}")
        return jsonify(success=False, message="Failed to fetch dashboard data"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@user_mgmt_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard data showing top performing users."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                u.username,
                u.id,
                COALESCE(AVG(qr.score::float / qr.total_questions * 100), 0) as avg_score,
                COUNT(qr.id) as quiz_count
            FROM tbl_user u
            LEFT JOIN tbl_quiz_result qr ON u.id = qr.user_id
            WHERE u.usertype = 'student'
            GROUP BY u.id, u.username
            HAVING COUNT(qr.id) > 0
            ORDER BY avg_score DESC, quiz_count DESC
            LIMIT 20
        """)
        
        leaderboard = []
        for i, row in enumerate(cursor.fetchall(), 1):
            leaderboard.append({
                'rank': i,
                'username': row[0],
                'user_id': row[1],
                'average_score': round(row[2], 1),
                'quiz_count': row[3]
            })
        
        return jsonify(success=True, leaderboard=leaderboard)
        
    except Exception as e:
        print(f"Leaderboard API Error: {e}")
        return jsonify(success=False, message="Failed to fetch leaderboard"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


# =================================================================
#  PARENT-STUDENT MANAGEMENT
# =================================================================

@user_mgmt_bp.route('/create-student', methods=['POST', 'OPTIONS'])
@require_auth(['parent'])
def create_student():
    """Create a new student account linked to a parent."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    parent_id = data.get('parent_id')
    
    if not all([username, email, password, parent_id]):
        return jsonify(success=False, message="Missing required fields"), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT id FROM tbl_user WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify(success=False, message="Username or email already exists"), 400
        
        # Create student account
        from extensions import bcrypt
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO tbl_user (username, email, passwordhash, usertype, parentuserid, created_at)
            VALUES (%s, %s, %s, 'student', %s, NOW())
            RETURNING id
        """, (username, email, password_hash, parent_id))
        
        student_id = cursor.fetchone()[0]
        conn.commit()
        
        update_users_version()
        
        return jsonify(success=True, message="Student account created successfully", student_id=student_id)
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Create Student API Error: {e}")
        return jsonify(success=False, message="Failed to create student account"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@user_mgmt_bp.route('/my-students/<int:parent_id>', methods=['GET'])
@require_user_access
def get_my_students(parent_id):
    """Get all students linked to a parent account."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, created_at
            FROM tbl_user
            WHERE parentuserid = %s AND usertype = 'student'
            ORDER BY created_at DESC
        """, (parent_id,))
        
        students = []
        for row in cursor.fetchall():
            students.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'created_at': row[3].isoformat() if row[3] else None
            })
        
        return jsonify(success=True, students=students)
        
    except Exception as e:
        print(f"Get My Students API Error: {e}")
        return jsonify(success=False, message="Failed to fetch students"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@user_mgmt_bp.route('/modify-student', methods=['POST', 'OPTIONS'])
@require_auth(['parent'])
def modify_student():
    """Modify student account details."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    data = request.get_json()
    student_id = data.get('student_id')
    username = data.get('username')
    email = data.get('email')
    parent_id = data.get('parent_id')
    
    if not all([student_id, parent_id]):
        return jsonify(success=False, message="Missing required fields"), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify the student belongs to this parent
        cursor.execute("SELECT id FROM tbl_user WHERE id = %s AND parentuserid = %s", (student_id, parent_id))
        if not cursor.fetchone():
            return jsonify(success=False, message="Student not found or access denied"), 403
        
        # Update student info
        update_fields = []
        update_values = []
        
        if username:
            update_fields.append("username = %s")
            update_values.append(username)
        if email:
            update_fields.append("email = %s")
            update_values.append(email)
        
        if update_fields:
            update_values.append(student_id)
            query = f"UPDATE tbl_user SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, update_values)
            conn.commit()
        
        update_users_version()
        
        return jsonify(success=True, message="Student account updated successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Modify Student API Error: {e}")
        return jsonify(success=False, message="Failed to update student account"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@user_mgmt_bp.route('/delete-student/<int:student_id>', methods=['DELETE', 'OPTIONS'])
@require_auth(['parent'])
def delete_student(student_id):
    """Delete a student account."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    data = request.get_json() or {}
    parent_id = data.get('parent_id')
    
    if not parent_id:
        return jsonify(success=False, message="Parent ID required"), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify the student belongs to this parent
        cursor.execute("SELECT id FROM tbl_user WHERE id = %s AND parentuserid = %s", (student_id, parent_id))
        if not cursor.fetchone():
            return jsonify(success=False, message="Student not found or access denied"), 403
        
        # Delete student account and related data
        cursor.execute("DELETE FROM tbl_quiz_result WHERE user_id = %s", (student_id,))
        cursor.execute("DELETE FROM tbl_story_progress WHERE user_id = %s", (student_id,))
        cursor.execute("DELETE FROM tbl_video_progress WHERE user_id = %s", (student_id,))
        cursor.execute("DELETE FROM tbl_user WHERE id = %s", (student_id,))
        
        conn.commit()
        update_users_version()
        
        return jsonify(success=True, message="Student account deleted successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Delete Student API Error: {e}")
        return jsonify(success=False, message="Failed to delete student account"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)