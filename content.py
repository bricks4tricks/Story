"""
Content management blueprint for stories, videos, and curriculum.
Handles all content-related API endpoints.
"""

from flask import Blueprint, jsonify, request
import traceback
from auth_utils import require_auth
from db_utils import get_db_connection, release_db_connection

content_bp = Blueprint('content', __name__, url_prefix='/api')

# =================================================================
#  CONTENT MANAGEMENT ENDPOINTS
# =================================================================

@content_bp.route('/video/<int:topic_id>', methods=['GET'])
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


@content_bp.route('/story/<int:topic_id>', methods=['GET'])
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
            return jsonify(success=True, story=result[0])
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


@content_bp.route('/story-exists/<int:topic_id>', methods=['GET'])
def story_exists(topic_id):
    """Check if a story exists for a specific topic."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tbl_story WHERE topicid = %s", (topic_id,))
        count = cursor.fetchone()[0]
        return jsonify(success=True, exists=(count > 0))
    except Exception as e:
        print(f"Story Exists API Error: {e}")
        return jsonify(success=False, message="Failed to check story existence"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@content_bp.route('/quiz-exists/<int:topic_id>', methods=['GET'])
def quiz_exists(topic_id):
    """Check if a quiz exists for a specific topic."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tbl_question WHERE topicid = %s", (topic_id,))
        count = cursor.fetchone()[0]
        return jsonify(success=True, exists=(count > 0))
    except Exception as e:
        print(f"Quiz Exists API Error: {e}")
        return jsonify(success=False, message="Failed to check quiz existence"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@content_bp.route('/curriculum', methods=['GET'])
def get_curriculum():
    """Get curriculum data for the frontend."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get curriculum hierarchy
        cursor.execute("""
            SELECT 
                c.id as curriculum_id,
                c.name as curriculum_name,
                c.description as curriculum_description,
                l.id as lesson_id,
                l.name as lesson_name,
                l.description as lesson_description,
                l.order_index as lesson_order,
                t.id as topic_id,
                t.name as topic_name,
                t.description as topic_description,
                t.order_index as topic_order
            FROM tbl_curriculum c
            LEFT JOIN tbl_lesson l ON c.id = l.curriculum_id
            LEFT JOIN tbl_topic t ON l.id = t.lesson_id
            ORDER BY c.name, l.order_index, t.order_index
        """)
        
        rows = cursor.fetchall()
        curriculum_dict = {}
        
        for row in rows:
            curr_id = row[0]
            if curr_id not in curriculum_dict:
                curriculum_dict[curr_id] = {
                    'id': curr_id,
                    'name': row[1],
                    'description': row[2],
                    'lessons': {}
                }
            
            lesson_id = row[3]
            if lesson_id and lesson_id not in curriculum_dict[curr_id]['lessons']:
                curriculum_dict[curr_id]['lessons'][lesson_id] = {
                    'id': lesson_id,
                    'name': row[4],
                    'description': row[5],
                    'order_index': row[6],
                    'topics': []
                }
            
            if row[7]:  # topic_id exists
                topic = {
                    'id': row[7],
                    'name': row[8],
                    'description': row[9],
                    'order_index': row[10]
                }
                if lesson_id:
                    curriculum_dict[curr_id]['lessons'][lesson_id]['topics'].append(topic)
        
        # Convert to list format
        curriculum_list = []
        for curr in curriculum_dict.values():
            curr['lessons'] = list(curr['lessons'].values())
            curriculum_list.append(curr)
        
        return jsonify(success=True, curriculum=curriculum_list)
        
    except Exception as e:
        print(f"Get Curriculum API Error: {e}")
        return jsonify(success=False, message="Failed to fetch curriculum"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@content_bp.route('/curriculum-table', methods=['GET'])
def get_curriculum_table():
    """Get curriculum data formatted for table display."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.id as curriculum_id,
                c.name as curriculum_name,
                l.id as lesson_id,
                l.name as lesson_name,
                t.id as topic_id,
                t.name as topic_name
            FROM tbl_curriculum c
            LEFT JOIN tbl_lesson l ON c.id = l.curriculum_id
            LEFT JOIN tbl_topic t ON l.id = t.lesson_id
            ORDER BY c.name, l.order_index, t.order_index
        """)
        
        rows = cursor.fetchall()
        table_data = []
        
        for row in rows:
            table_data.append({
                'curriculum_id': row[0],
                'curriculum_name': row[1],
                'lesson_id': row[2],
                'lesson_name': row[3],
                'topic_id': row[4],
                'topic_name': row[5]
            })
        
        return jsonify(success=True, data=table_data)
        
    except Exception as e:
        print(f"Get Curriculum Table API Error: {e}")
        return jsonify(success=False, message="Failed to fetch curriculum table"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)