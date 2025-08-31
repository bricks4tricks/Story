"""
Flagging system blueprint for content moderation and issue reporting.
Handles all flagging-related API endpoints.
"""

from flask import Blueprint, jsonify, request
import traceback
from auth_utils import require_auth
from db_utils import release_db_connection
# Make flagging.get_db_connection patchable via app.get_db_connection for tests
import app
def get_db_connection():
    return app.get_db_connection()

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
        
        cursor.execute("SELECT flagid as FlagID, item_type as ItemType, item_name as ItemName FROM tbl_flag WHERE status = 'open'")
        flags = cursor.fetchall()
        
        # Handle both dict (from tests) and tuple (from real DB) formats
        result = []
        for flag in flags:
            if isinstance(flag, dict):
                result.append(flag)
            else:
                result.append({
                    'FlagID': flag[0],
                    'ItemType': flag[1], 
                    'ItemName': flag[2]
                })
        
        return jsonify(result)
        
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
    # Handle both new and legacy field names
    page_url = data.get('page_url') or data.get('pagePath')
    error_description = data.get('error_description') or data.get('description')
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
        """, (user_id, page_url, error_description, user_agent))
        
        conn.commit()
        
        return jsonify(status="success", message="Error reported successfully"), 201
        
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


