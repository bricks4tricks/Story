#!/usr/bin/env python3
"""
Admin Password Reset Utility
Usage: python admin_password_reset.py [username] [new_password]
"""

import sys
import secrets
import string
from extensions import bcrypt
from db_utils import get_db_connection, release_db_connection

def generate_secure_password(length=16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def reset_admin_password(username="admin", new_password=None):
    """Reset admin user password."""
    # Generate secure password if none provided
    if new_password is None:
        new_password = generate_secure_password()
        print(f"🔐 Generated secure password: {new_password}")
        print("⚠️  IMPORTANT: Save this password securely - it won't be shown again!")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists and is admin
        cursor.execute(
            "SELECT id, username, usertype FROM tbl_user WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return False
            
        if user[2] != 'Admin':
            print(f"❌ User '{username}' is not an admin (type: {user[2]})")
            return False
        
        # Generate new password hash
        password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Update password
        cursor.execute(
            "UPDATE tbl_user SET passwordhash = %s WHERE username = %s",
            (password_hash, username)
        )
        
        conn.commit()
        print(f"✅ Password reset successful for admin user '{username}'")
        print(f"   New password: {new_password}")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    
    print(f"Resetting password for admin user: {username}")
    reset_admin_password(username, password)