"""
Flagging system blueprint for content moderation and issue reporting.
Handles all flagging-related API endpoints.
"""

from flask import Blueprint, jsonify, request
import traceback
from auth_utils import require_auth
from db_utils import get_db_connection, release_db_connection

flagging_bp = Blueprint('flagging', __name__, url_prefix='/api')

# =================================================================
#  FLAGGING SYSTEM ENDPOINTS
# =================================================================

@flagging_bp.route('/flag-item', methods=['POST', 'OPTIONS'])
@require_auth(['student', 'parent', 'admin'])
def flag_item():
    """Flag content for review."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    data = request.get_json()
    user_id = data.get('user_id')
    content_type = data.get('content_type')  # 'story', 'question', 'video'
    content_id = data.get('content_id')
    reason = data.get('reason')
    description = data.get('description', '')
    
    if not all([user_id, content_type, content_id, reason]):
        return jsonify(success=False, message="Missing required fields"), 400
    
    # Validate content type
    valid_types = ['story', 'question', 'video']
    if content_type not in valid_types:
        return jsonify(success=False, message="Invalid content type"), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if item already flagged by this user
        cursor.execute("""
            SELECT id FROM tbl_flag 
            WHERE user_id = %s AND content_type = %s AND content_id = %s AND status = 'open'
        """, (user_id, content_type, content_id))
        
        if cursor.fetchone():
            return jsonify(success=False, message="You have already flagged this item"), 400
        
        # Create flag
        cursor.execute("""
            INSERT INTO tbl_flag (user_id, content_type, content_id, reason, description, status, created_at)
            VALUES (%s, %s, %s, %s, %s, 'open', NOW())
            RETURNING id
        """, (user_id, content_type, content_id, reason, description))
        
        flag_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify(success=True, message="Item flagged successfully", flag_id=flag_id)
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Flag Item API Error: {e}")
        return jsonify(success=False, message="Failed to flag item"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@flagging_bp.route('/open-flags', methods=['GET'])
def get_open_flags():
    """Get count of open flags for display."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tbl_flag WHERE status = 'open'")
        count = cursor.fetchone()[0]
        
        return jsonify(success=True, open_flags=count)
        
    except Exception as e:
        print(f"Open Flags API Error: {e}")
        return jsonify(success=False, message="Failed to fetch open flags count"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@flagging_bp.route('/flag-page-error', methods=['POST', 'OPTIONS'])
def flag_page_error():
    """Flag a page error for technical review."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    data = request.get_json()
    page_url = data.get('page_url')
    error_description = data.get('error_description')
    # Sanitize User-Agent header - limit length and remove dangerous characters
    user_agent = request.headers.get('User-Agent', '')[:500]  # Limit to 500 chars
    user_agent = ''.join(c for c in user_agent if c.isprintable())  # Remove non-printable chars
    user_id = data.get('user_id')  # Optional, for logged-in users
    
    if not all([page_url, error_description]):
        return jsonify(success=False, message="Missing required fields"), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Log the page error
        cursor.execute("""
            INSERT INTO tbl_page_error (user_id, page_url, error_description, user_agent, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
        """, (user_id, page_url, error_description, user_agent))
        
        error_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify(success=True, message="Error reported successfully", error_id=error_id)
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Flag Page Error API Error: {e}")
        return jsonify(success=False, message="Failed to report error"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@flagging_bp.route('/record-question-attempt', methods=['POST', 'OPTIONS'])
@require_auth(['student', 'parent'])
def record_question_attempt():
    """Record a question attempt for analytics."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    data = request.get_json()
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    selected_answer = data.get('selected_answer')
    is_correct = data.get('is_correct')
    time_taken = data.get('time_taken')  # in seconds
    
    if not all([user_id, question_id, selected_answer is not None, is_correct is not None]):
        return jsonify(success=False, message="Missing required fields"), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Record the question attempt
        cursor.execute("""
            INSERT INTO tbl_question_attempt 
            (user_id, question_id, selected_answer, is_correct, time_taken, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (user_id, question_id, selected_answer, is_correct, time_taken))
        
        attempt_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify(success=True, message="Question attempt recorded", attempt_id=attempt_id)
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Record Question Attempt API Error: {e}")
        return jsonify(success=False, message="Failed to record attempt"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)