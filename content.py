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
        return jsonify(success=True, storyExists=(count > 0))
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
        return jsonify(success=True, quizExists=(count > 0))
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
        
        query = """
            SELECT
                g.gradename,
                s.subjectname AS CurriculumType,
                unit.topicname AS UnitName,
                topic.topicname,
                topic.id AS topicid
            FROM tbl_topic topic
            JOIN tbl_topic unit ON topic.parenttopicid = unit.id
            JOIN tbl_subject s ON unit.subjectid = s.id
            JOIN tbl_topicgrade tg ON topic.id = tg.topicid
            JOIN tbl_grade g ON tg.gradeid = g.id
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
            grade_name = row[0]
            curriculum_type = row[1]
            unit_name = row[2]
            topic_name = row[3]
            topic_id = row[4]
            
            clean_grade_name = ' '.join(grade_name.replace('grade', 'Grade').split()).strip()
            if clean_grade_name not in curriculum_data:
                style = grade_color_map.get(clean_grade_name, { "icon": clean_grade_name[:3], "color": "94a3b8" })
                curriculum_data[clean_grade_name] = {**style, "curriculums": {}}
            if curriculum_type not in curriculum_data[clean_grade_name]['curriculums']:
                curriculum_data[clean_grade_name]['curriculums'][curriculum_type] = {"units": {}}
            if unit_name not in curriculum_data[clean_grade_name]['curriculums'][curriculum_type]['units']:
                curriculum_data[clean_grade_name]['curriculums'][curriculum_type]['units'][unit_name] = []

            curriculum_data[clean_grade_name]['curriculums'][curriculum_type]['units'][unit_name].append({
                "name": topic_name,
                "id": topic_id,
                "availableThemes": [],
                "defaultTheme": None
            })

        return jsonify(curriculum_data)
    except Exception as e:
        print(f"API Error in get_curriculum: {e}")
        traceback.print_exc()
        return jsonify({ "status": "error", "message": str(e) }), 500
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


@content_bp.route('/curriculums_simple', methods=['GET'])  # Use different name to avoid conflicts
def get_curriculums():
    """Return a list of curriculum names from the database or a mock list."""
    mock_curriculums = ["Common Core", "IB", "AP"]
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT TRIM(subjectname) FROM tbl_subject ORDER BY TRIM(subjectname);"
        )
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
