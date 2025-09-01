#!/usr/bin/env python3
"""
Debug script to check user signin and userType values
"""

import psycopg2
import os
from datetime import datetime

def check_signin_debug():
    """Check what's in the database for signin debugging"""
    
    # Database connection
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        DATABASE_URL = "postgresql://root:5ijBwqeThiTcfMLbo6cofrSExSZ8FrXg@dpg-d24k1tbe5dus73dccms0-a.oregon-postgres.render.com/educational_platform_db_0z56"
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("=== SIGNIN DEBUG INFO ===")
        print(f"Timestamp: {datetime.now()}")
        print()
        
        # Get all users with usertype
        cursor.execute("SELECT id, username, usertype, parentuserid FROM tbl_user ORDER BY id")
        users = cursor.fetchall()
        
        print("ALL USERS:")
        print("ID | Username | UserType | ParentUserID")
        print("-" * 45)
        for user in users:
            parent_id = str(user[3]) if user[3] is not None else 'None'
            print(f"{user[0]:2d} | {user[1]:10s} | {user[2]:8s} | {parent_id:10s}")
        
        print()
        print("ADMIN USERS:")
        cursor.execute("SELECT id, username, usertype FROM tbl_user WHERE usertype = 'Admin'")
        admin_users = cursor.fetchall()
        
        if admin_users:
            for admin in admin_users:
                print(f"  - ID {admin[0]}: {admin[1]} (Type: {admin[2]})")
        else:
            print("  No admin users found!")
        
        print()
        print("DEBUGGING SIGNIN FLOW:")
        print("1. Check if your username exists in the list above")
        print("2. Verify your usertype is exactly 'Admin' (case sensitive)")
        print("3. If usertype is wrong, run: UPDATE tbl_user SET usertype = 'Admin' WHERE username = 'your_username';")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    check_signin_debug()