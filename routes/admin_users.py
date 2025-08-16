"""
Admin user management routes.

Contains routes for managing users from the admin interface.
"""

import traceback
import psycopg2.extras
from flask import Blueprint, request, jsonify
from auth_utils import require_auth
from db_utils import get_db_connection, release_db_connection
from error_handlers import ValidationError, DatabaseError, validate_required_fields
from version_cache import update_users_version

admin_users_bp = Blueprint('admin_users', __name__, url_prefix='/api/admin')


@admin_users_bp.route('/edit-user/<int:user_id>', methods=['PUT', 'OPTIONS'])
@require_auth(['admin'])
def edit_user(user_id):
    """Edit user details (admin only)."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)

    try:
        data = request.get_json(silent=True)
        if data is None:
            raise ValidationError("Invalid JSON data")
        
        # Validate required fields
        validate_required_fields(data, ['username', 'email', 'userType'])
        
        username = data['username'].strip()
        email = data['email'].strip()
        user_type = data['userType'].strip()
        
        if user_type not in ['Admin', 'Parent', 'Student']:
            raise ValidationError("Invalid user type", field='userType')

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Check for duplicate username/email
            cursor.execute(
                "SELECT id FROM tbl_user WHERE (username = %s OR email = %s) AND id != %s",
                (username, email, user_id)
            )
            if cursor.fetchone():
                raise ValidationError("Username or email is already in use by another account")

            # Update user
            cursor.execute(
                "UPDATE tbl_user SET username = %s, email = %s, usertype = %s WHERE id = %s",
                (username, email, user_type, user_id)
            )
            
            if cursor.rowcount == 0:
                raise ValidationError("User not found or no changes made")

            conn.commit()
            update_users_version()

            return jsonify({"status": "success", "message": "User updated successfully"}), 200
            
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
        print(f"Edit User API Error: {e}")
        traceback.print_exc()
        raise


@admin_users_bp.route('/delete-user/<int:user_id>', methods=['DELETE', 'OPTIONS'])
@require_auth(['admin'])
def delete_user(user_id):
    """Delete a user (admin only)."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    try:
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get user details
            cursor.execute("SELECT usertype FROM tbl_user WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                raise ValidationError("User not found")

            user_type = user[0]

            # Prevent admin deletion
            if user_type == 'Admin':
                raise ValidationError("Admin accounts cannot be deleted")

            # Check for dependent student accounts
            if user_type == 'Parent':
                cursor.execute("SELECT id FROM tbl_user WHERE parentuserid = %s", (user_id,))
                if cursor.fetchone():
                    raise ValidationError(
                        "Cannot delete a parent with student accounts. "
                        "Please delete the student profiles first."
                    )

            # Remove subscription first to avoid foreign key violations
            cursor.execute("DELETE FROM tbl_subscription WHERE user_id = %s", (user_id,))

            # Delete user
            cursor.execute("DELETE FROM tbl_user WHERE id = %s", (user_id,))
            if cursor.rowcount == 0:
                raise ValidationError("User not found or already deleted")

            conn.commit()
            update_users_version()
            
            return jsonify({"status": "success", "message": "User deleted successfully"}), 200
            
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
        print(f"Delete User API Error: {e}")
        traceback.print_exc()
        raise


@admin_users_bp.route('/create-student', methods=['POST', 'OPTIONS'])
@require_auth(['admin'])
def create_student():
    """Create a new student account (admin only)."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    try:
        data = request.get_json(silent=True)
        if data is None:
            raise ValidationError("Invalid JSON data")
        
        # Validate required fields
        validate_required_fields(data, ['username', 'email', 'parentId'])
        
        username = data['username'].strip()
        email = data['email'].strip()
        parent_id = int(data['parentId'])
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verify parent exists
            cursor.execute(
                "SELECT id FROM tbl_user WHERE id = %s AND usertype = 'Parent'", 
                (parent_id,)
            )
            if not cursor.fetchone():
                raise ValidationError("Parent account not found")

            # Check for duplicate username/email
            cursor.execute(
                "SELECT id FROM tbl_user WHERE username = %s OR email = %s", 
                (username, email)
            )
            if cursor.fetchone():
                raise ValidationError("Username or email already exists")

            # Create student account
            cursor.execute(
                """INSERT INTO tbl_user (username, email, passwordhash, usertype, parentuserid) 
                   VALUES (%s, %s, %s, 'Student', %s) RETURNING id""",
                (username, email, 'student_no_password', parent_id)
            )
            
            student_id = cursor.fetchone()[0]
            conn.commit()
            update_users_version()

            return jsonify({
                "status": "success", 
                "message": "Student account created successfully",
                "studentId": student_id
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
        print(f"Create Student API Error: {e}")
        traceback.print_exc()
        raise