#!/usr/bin/env python3
"""
Signin Troubleshooting Utility
Usage: python signin_troubleshoot.py [username]
"""

import sys
from db_utils import get_db_connection, release_db_connection
from datetime import datetime, timezone

def troubleshoot_signin(username):
    """Diagnose signin issues for a user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"🔍 Troubleshooting signin for user: {username}")
        print("=" * 50)
        
        # Check if user exists
        cursor.execute(
            "SELECT id, username, usertype, parentuserid, isactive FROM tbl_user WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user:
            print("❌ User not found in database")
            return False
            
        user_id, username, usertype, parent_id, is_active = user
        print(f"✅ User found:")
        print(f"   ID: {user_id}")
        print(f"   Type: {usertype}")
        print(f"   Active: {is_active}")
        print(f"   Parent ID: {parent_id}")
        
        if not is_active:
            print("❌ User account is inactive")
            return False
            
        # Check subscription requirements
        if usertype == 'Admin':
            print("✅ Admin user - no subscription required")
            return True
            
        if usertype == 'Student':
            if not parent_id:
                print("❌ Student user missing parent ID")
                print("   Students must be linked to a parent account")
                return False
            check_user_id = parent_id
            print(f"🔍 Checking parent's subscription (ID: {parent_id})")
        else:
            check_user_id = user_id
            print(f"🔍 Checking user's subscription")
            
        # Check subscription
        cursor.execute(
            "SELECT active, expires_on FROM tbl_subscription WHERE user_id = %s",
            (check_user_id,)
        )
        sub = cursor.fetchone()
        
        if not sub:
            print("❌ No subscription record found")
            print("   User needs an active subscription to sign in")
            return False
            
        active, expires_on = sub
        now_utc = datetime.now(timezone.utc)
        
        print(f"📋 Subscription details:")
        print(f"   Active: {active}")
        print(f"   Expires: {expires_on}")
        
        if expires_on:
            if expires_on.tzinfo is None:
                expires_on = expires_on.replace(tzinfo=timezone.utc)
            if expires_on <= now_utc:
                print("❌ Subscription has expired")
                return False
            days_left = (expires_on - now_utc).days
            print(f"   Days remaining: {days_left}")
            
        if not active:
            print("❌ Subscription is inactive")
            return False
            
        print("✅ All checks passed - signin should work")
        return True
        
    except Exception as e:
        print(f"❌ Error during troubleshooting: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else input("Enter username to troubleshoot: ")
    troubleshoot_signin(username)