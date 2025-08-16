"""
Enhanced admin authentication security for LogicAndStories.

Provides additional security measures specifically for admin users,
including session isolation and enhanced logging.
"""

import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List
from flask import request, jsonify, g
from functools import wraps
from db_utils import get_db_connection, release_db_connection
from auth_utils import SessionManager
from security_utils import rate_limiter

# Configure admin-specific logging
admin_logger = logging.getLogger('admin_security')
admin_logger.setLevel(logging.INFO)


class AdminSessionManager(SessionManager):
    """Enhanced session manager specifically for admin users."""
    
    @staticmethod
    def create_admin_session(user_id: int, ip_address: str, user_agent: str) -> Optional[str]:
        """Create an admin session with enhanced security tracking."""
        token = secrets.token_urlsafe(48)  # Longer token for admins
        expires_at = datetime.now(timezone.utc) + timedelta(hours=4)  # Shorter session
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Log admin login attempt
            admin_logger.info(f"Admin login attempt for user {user_id} from {ip_address}")
            
            # Clean up expired admin sessions
            cursor.execute(
                "DELETE FROM tbl_admin_session WHERE expires_at < NOW()"
            )
            
            # Check for concurrent admin sessions (limit to 3)
            cursor.execute(
                "SELECT COUNT(*) FROM tbl_admin_session WHERE user_id = %s",
                (user_id,)
            )
            session_count = cursor.fetchone()[0]
            
            if session_count >= 3:
                # Remove oldest session
                cursor.execute(
                    """DELETE FROM tbl_admin_session 
                       WHERE user_id = %s 
                       ORDER BY created_at ASC 
                       LIMIT 1""",
                    (user_id,)
                )
            
            # Create new admin session with enhanced tracking
            cursor.execute(
                """INSERT INTO tbl_admin_session 
                   (user_id, session_token, expires_at, ip_address, user_agent, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, token, expires_at, ip_address[:255], user_agent[:500], 
                 datetime.now(timezone.utc))
            )
            
            conn.commit()
            admin_logger.info(f"Admin session created for user {user_id}")
            return token
            
        except Exception as e:
            if conn:
                conn.rollback()
            admin_logger.error(f"Admin session creation failed for user {user_id}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
    
    @staticmethod
    def validate_admin_session(token: str, ip_address: str) -> Optional[Dict[str, any]]:
        """Validate admin session with IP verification."""
        if not token:
            return None
            
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT s.user_id, u.username, s.ip_address, s.created_at
                   FROM tbl_admin_session s
                   JOIN tbl_user u ON s.user_id = u.id
                   WHERE s.session_token = %s 
                   AND s.expires_at > NOW() 
                   AND u.usertype = 'Admin'""",
                (token,)
            )
            
            result = cursor.fetchone()
            if result:
                stored_ip = result[2]
                
                # IP verification (optional - can be disabled for dynamic IPs)
                if stored_ip != ip_address:
                    admin_logger.warning(
                        f"IP mismatch for admin {result[1]}: stored={stored_ip}, current={ip_address}"
                    )
                    # Uncomment the following lines to enforce strict IP checking
                    # return None
                
                # Update last activity
                cursor.execute(
                    "UPDATE tbl_admin_session SET last_activity = %s WHERE session_token = %s",
                    (datetime.now(timezone.utc), token)
                )
                conn.commit()
                
                return {
                    'user_id': result[0],
                    'user_type': 'admin',
                    'username': result[1],
                    'session_created': result[3]
                }
            
            return None
            
        except Exception as e:
            admin_logger.error(f"Admin session validation error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
    
    @staticmethod
    def destroy_admin_session(token: str) -> None:
        """Destroy admin session and log the action."""
        if not token:
            return
            
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get session info before deletion
            cursor.execute(
                """SELECT s.user_id, u.username 
                   FROM tbl_admin_session s
                   JOIN tbl_user u ON s.user_id = u.id
                   WHERE s.session_token = %s""",
                (token,)
            )
            
            result = cursor.fetchone()
            if result:
                admin_logger.info(f"Admin session destroyed for user {result[1]} (ID: {result[0]})")
            
            cursor.execute(
                "DELETE FROM tbl_admin_session WHERE session_token = %s",
                (token,)
            )
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            admin_logger.error(f"Admin session destruction error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
    
    @staticmethod
    def get_active_admin_sessions(user_id: int) -> List[Dict]:
        """Get all active sessions for an admin user."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT session_token, ip_address, user_agent, created_at, last_activity
                   FROM tbl_admin_session 
                   WHERE user_id = %s AND expires_at > NOW()
                   ORDER BY created_at DESC""",
                (user_id,)
            )
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'token': row[0][:8] + '...',  # Masked token
                    'ip_address': row[1],
                    'user_agent': row[2][:100] + '...' if len(row[2]) > 100 else row[2],
                    'created_at': row[3].isoformat(),
                    'last_activity': row[4].isoformat() if row[4] else None
                })
            
            return sessions
            
        except Exception as e:
            admin_logger.error(f"Error getting admin sessions: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)


def require_admin_auth(f):
    """Enhanced admin authentication decorator with additional security."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Rate limiting for admin endpoints
        client_id = request.remote_addr or 'unknown'
        if not rate_limiter.is_allowed(client_id, max_requests=10, window=300):
            admin_logger.warning(f"Rate limit exceeded for admin endpoint from {client_id}")
            return jsonify({"status": "error", "message": "Rate limit exceeded"}), 429
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            admin_logger.warning(f"Admin endpoint access without token from {client_id}")
            return jsonify({"status": "error", "message": "Admin authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        ip_address = request.remote_addr or 'unknown'
        
        user_info = AdminSessionManager.validate_admin_session(token, ip_address)
        
        if not user_info:
            admin_logger.warning(f"Invalid admin session attempt from {ip_address}")
            return jsonify({"status": "error", "message": "Invalid or expired admin session"}), 401
        
        # Store admin info in Flask's g object
        g.current_admin = user_info
        
        # Log admin action
        admin_logger.info(
            f"Admin action: {request.method} {request.path} by {user_info['username']} from {ip_address}"
        )
        
        return f(*args, **kwargs)
    return decorated_function


def create_admin_session_table() -> None:
    """Create the admin session table if it doesn't exist."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tbl_admin_session (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                ip_address VARCHAR(255),
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                CONSTRAINT admin_user_check CHECK (
                    (SELECT usertype FROM tbl_user WHERE id = user_id) = 'Admin'
                )
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_session_token 
            ON tbl_admin_session(session_token)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_session_expires 
            ON tbl_admin_session(expires_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_session_user_id 
            ON tbl_admin_session(user_id)
        """)
        
        conn.commit()
        print("✅ Admin session table created successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Admin session table creation error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


if __name__ == "__main__":
    # Create admin session table when run directly
    create_admin_session_table()