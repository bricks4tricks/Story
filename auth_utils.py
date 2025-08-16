"""
Authentication utilities for LogicAndStories application.
Provides session-based authentication for API endpoints.
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Dict, List, Optional, Callable, Any, Union
from flask import request, jsonify, g, Response
from db_utils import get_db_connection, release_db_connection


class SessionManager:
    """Manages user sessions with token-based authentication."""
    
    @staticmethod
    def create_session(user_id: int, user_type: str = 'student') -> Optional[str]:
        """Create a new session token for a user."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Clean up expired sessions
            cursor.execute(
                "DELETE FROM tbl_user_session WHERE expires_at < NOW()"
            )
            
            # Create new session
            cursor.execute(
                """INSERT INTO tbl_user_session (user_id, session_token, user_type, expires_at, created_at)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (user_id) DO UPDATE SET
                   session_token = EXCLUDED.session_token,
                   expires_at = EXCLUDED.expires_at,
                   created_at = EXCLUDED.created_at""",
                (user_id, token, user_type, expires_at, datetime.now(timezone.utc))
            )
            conn.commit()
            return token
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Session creation error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
    
    @staticmethod
    def validate_session(token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token and return user info."""
        if not token:
            return None
            
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT s.user_id, s.user_type, u.username 
                   FROM tbl_user_session s
                   JOIN tbl_user u ON s.user_id = u.id
                   WHERE s.session_token = %s AND s.expires_at > NOW()""",
                (token,)
            )
            
            result = cursor.fetchone()
            if result:
                return {
                    'user_id': result[0],
                    'user_type': result[1],
                    'username': result[2]
                }
            return None
            
        except Exception as e:
            print(f"Session validation error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
    
    @staticmethod
    def destroy_session(token: str) -> None:
        """Destroy a session token."""
        if not token:
            return
            
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM tbl_user_session WHERE session_token = %s",
                (token,)
            )
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Session destruction error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)


def require_auth(allowed_user_types: List[str] = None) -> Callable:
    """
    Decorator to require authentication for endpoints.
    
    Args:
        allowed_user_types: List of user types allowed to access the endpoint
        
    Returns:
        Decorator function that validates session and sets g.current_user
    """
    if allowed_user_types is None:
        allowed_user_types = ['student', 'parent', 'admin']
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Union[Response, Any]:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"status": "error", "message": "Authentication required"}), 401
            
            token = auth_header.split(' ')[1]
            user_info = SessionManager.validate_session(token)
            
            if not user_info:
                return jsonify({"status": "error", "message": "Invalid or expired session"}), 401
            
            if user_info['user_type'] not in allowed_user_types:
                return jsonify({"status": "error", "message": "Insufficient permissions"}), 403
            
            # Store user info in Flask's g object for use in the endpoint
            g.current_user = user_info
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_user_access(f: Callable) -> Callable:
    """
    Decorator to ensure user can only access their own data.
    Requires that the endpoint has a user_id parameter or userId in request data.
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Union[Response, Any]:
        if not hasattr(g, 'current_user'):
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        
        # Check URL parameter
        requested_user_id = kwargs.get('user_id')
        
        # Check request data if no URL parameter
        if requested_user_id is None:
            data = request.get_json(silent=True) or {}
            requested_user_id = data.get('userId')
        
        if requested_user_id is None:
            return jsonify({"status": "error", "message": "User ID required"}), 400
        
        # Allow admins to access any user's data
        if g.current_user['user_type'] == 'admin':
            return f(*args, **kwargs)
        
        # For parents, allow access to their student accounts
        if g.current_user['user_type'] == 'parent':
            # Check if requested_user_id is a student under this parent
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT 1 FROM tbl_user WHERE id = %s AND parentid = %s",
                    (requested_user_id, g.current_user['user_id'])
                )
                
                if cursor.fetchone():
                    return f(*args, **kwargs)
                    
            except Exception as e:
                print(f"Parent access check error: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    release_db_connection(conn)
        
        # For students, only allow access to their own data
        if int(requested_user_id) != g.current_user['user_id']:
            return jsonify({"status": "error", "message": "Access denied: can only access your own data"}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def create_session_table() -> None:
    """Create the user session table if it doesn't exist."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tbl_user_session (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                user_type VARCHAR(20) NOT NULL DEFAULT 'student',
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                UNIQUE(user_id)
            )
        """)
        
        # Create index for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_session_token 
            ON tbl_user_session(session_token)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_session_expires 
            ON tbl_user_session(expires_at)
        """)
        
        conn.commit()
        print("✅ Session table created successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Session table creation error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


if __name__ == "__main__":
    # Create session table when run directly
    create_session_table()