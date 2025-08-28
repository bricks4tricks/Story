"""
Curriculum management routes.

Contains routes for managing educational content like subjects, topics, and questions.
"""

import traceback
import psycopg2.extras
from flask import Blueprint, request, jsonify
from auth_utils import require_auth, require_user_access
from db_utils import get_db_connection, release_db_connection
from error_handlers import ValidationError, DatabaseError, validate_required_fields, validate_integer_range
from security_utils import sanitizer

curriculum_bp = Blueprint('curriculum', __name__, url_prefix='/api')


@curriculum_bp.route('/get-curriculums', methods=['GET', 'OPTIONS'])
@require_user_access
def get_curriculums():
    """Get available curriculums/subjects."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    try:
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT DISTINCT s.id, s.subjectname as name, s.description
                FROM tbl_subject s
                INNER JOIN tbl_topicsubject ts ON s.id = ts.subjectid
                INNER JOIN tbl_topic t ON ts.topicid = t.id
                ORDER BY s.subjectname
            """)
            
            subjects = cursor.fetchall()
            return jsonify([dict(subject) for subject in subjects]), 200
            
        except psycopg2.Error as e:
            raise DatabaseError(f"Database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
                
    except Exception as e:
        print(f"Get Curriculums API Error: {e}")
        traceback.print_exc()
        raise


@curriculum_bp.route('/get-units/<int:curriculum_id>', methods=['GET', 'OPTIONS'])
@require_user_access
def get_units(curriculum_id):
    """Get units (topics) for a specific curriculum."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    try:
        validate_integer_range(curriculum_id, 'curriculum_id', min_val=1)
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT t.id, t.topicname as name, t.description, t.grade_level
                FROM tbl_topic t
                INNER JOIN tbl_topicsubject ts ON t.id = ts.topicid
                WHERE ts.subjectid = %s
                ORDER BY t.grade_level, t.topicname
            """, (curriculum_id,))
            
            topics = cursor.fetchall()
            return jsonify([dict(topic) for topic in topics]), 200
            
        except psycopg2.Error as e:
            raise DatabaseError(f"Database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
                
    except Exception as e:
        print(f"Get Units API Error: {e}")
        traceback.print_exc()
        raise


@curriculum_bp.route('/admin/create-curriculum', methods=['POST', 'OPTIONS'])
@require_auth(['admin'])
def create_curriculum():
    """Create a new curriculum/subject (admin only)."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    try:
        data = request.get_json(silent=True)
        if data is None:
            raise ValidationError("Invalid JSON data")
        
        validate_required_fields(data, ['name'])
        
        name = sanitizer.sanitize_html(data['name'].strip())
        description = sanitizer.sanitize_html(data.get('description', '').strip())
        
        if len(name) < 2:
            raise ValidationError("Curriculum name must be at least 2 characters", field='name')
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check for duplicate name
            cursor.execute("SELECT id FROM tbl_subject WHERE subjectname = %s", (name,))
            if cursor.fetchone():
                raise ValidationError("A curriculum with this name already exists")
            
            # Create curriculum
            cursor.execute(
                "INSERT INTO tbl_subject (subjectname, description) VALUES (%s, %s) RETURNING id",
                (name, description)
            )
            
            curriculum_id = cursor.fetchone()[0]
            conn.commit()
            
            return jsonify({
                "status": "success",
                "message": "Curriculum created successfully",
                "curriculumId": curriculum_id
            }), 201
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
                
    except Exception as e:
        print(f"Create Curriculum API Error: {e}")
        traceback.print_exc()
        raise


@curriculum_bp.route('/admin/create-topic', methods=['POST', 'OPTIONS'])
@require_auth(['admin'])
def create_topic():
    """Create a new topic (admin only)."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    try:
        data = request.get_json(silent=True)
        if data is None:
            raise ValidationError("Invalid JSON data")
        
        validate_required_fields(data, ['name', 'subjectId'])
        
        name = sanitizer.sanitize_html(data['name'].strip())
        subject_id = validate_integer_range(data['subjectId'], 'subjectId', min_val=1)
        description = sanitizer.sanitize_html(data.get('description', '').strip())
        grade_level = data.get('gradeLevel')
        
        if grade_level is not None:
            grade_level = validate_integer_range(grade_level, 'gradeLevel', min_val=1, max_val=12)
        
        if len(name) < 2:
            raise ValidationError("Topic name must be at least 2 characters", field='name')
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verify subject exists
            cursor.execute("SELECT id FROM tbl_subject WHERE id = %s", (subject_id,))
            if not cursor.fetchone():
                raise ValidationError("Subject not found")
            
            # Create topic
            cursor.execute(
                "INSERT INTO tbl_topic (topicname, description, grade_level) VALUES (%s, %s, %s) RETURNING id",
                (name, description, grade_level)
            )
            
            topic_id = cursor.fetchone()[0]
            
            # Link topic to subject
            cursor.execute(
                "INSERT INTO tbl_topicsubject (topicid, subjectid) VALUES (%s, %s)",
                (topic_id, subject_id)
            )
            
            conn.commit()
            
            return jsonify({
                "status": "success",
                "message": "Topic created successfully",
                "topicId": topic_id
            }), 201
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
                
    except Exception as e:
        print(f"Create Topic API Error: {e}")
        traceback.print_exc()
        raise


@curriculum_bp.route('/admin/search-curriculums', methods=['GET', 'OPTIONS'])
@require_auth(['admin'])
def search_curriculums():
    """Search curriculums (admin only)."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    try:
        # Validate and sanitize search parameter
        search_term_raw = request.args.get('q', '').strip()
        search_term = ''
        if search_term_raw:
            # Limit length to prevent DOS attacks
            if len(search_term_raw) > 100:
                return jsonify(success=False, message="Search term too long"), 400
            
            # Remove dangerous characters but allow basic search terms
            search_term = ''.join(c for c in search_term_raw if c.isalnum() or c.isspace() or c in '-_.@')
            search_term = search_term.strip()
            
            # Prevent SQL injection patterns in search
            dangerous_patterns = ['--', '/*', '*/', ';', 'union', 'select', 'drop', 'insert', 'update', 'delete']
            search_lower = search_term.lower()
            for pattern in dangerous_patterns:
                if pattern in search_lower:
                    return jsonify(success=False, message="Invalid search term"), 400
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            if search_term:
                cursor.execute("""
                    SELECT id, subjectname as name, description
                    FROM tbl_subject
                    WHERE subjectname ILIKE %s OR description ILIKE %s
                    ORDER BY subjectname
                """, (f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute("""
                    SELECT id, subjectname as name, description
                    FROM tbl_subject
                    ORDER BY subjectname
                """)
            
            subjects = cursor.fetchall()
            return jsonify([dict(subject) for subject in subjects]), 200
            
        except psycopg2.Error as e:
            raise DatabaseError(f"Database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
                
    except Exception as e:
        print(f"Search Curriculums API Error: {e}")
        traceback.print_exc()
        raise