"""
Test script to verify that admin.py endpoints are properly secured.
This tests the critical authentication bypass vulnerability found in admin.py.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

from app import app
import json


def test_admin_py_endpoints_require_authentication():
    """Test that admin.py endpoints reject unauthenticated requests."""
    
    admin_py_endpoints = [
        ('/api/admin/users-version', 'GET', {}),
        ('/api/admin/all-users', 'GET', {}),
        ('/api/admin/seed-database', 'POST', {}),
    ]
    
    with app.test_client() as client:
        failed_endpoints = []
        protected_count = 0
        
        print("🔒 Testing admin.py Critical Security Fixes")
        print("=" * 50)
        
        for endpoint, method, data in admin_py_endpoints:
            print(f"Testing {method} {endpoint}...")
            
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'POST':
                response = client.post(endpoint, json=data, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 401:
                print(f"✅ {endpoint} properly protected")
                protected_count += 1
            else:
                print(f"❌ {endpoint} SECURITY BREACH! Status: {response.status_code}")
                failed_endpoints.append((endpoint, response.status_code))
        
        print(f"\n🔒 admin.py Security Test Results:")
        print(f"✅ Protected endpoints: {protected_count}")
        print(f"❌ Vulnerable endpoints: {len(failed_endpoints)}")
        
        if failed_endpoints:
            print("\n🚨 CRITICAL SECURITY VULNERABILITIES IN admin.py:")
            for endpoint, status in failed_endpoints:
                print(f"   - {endpoint} (HTTP {status})")
            print("\n⚠️  These endpoints expose:")
            print("   - Complete user database dump (/all-users)")
            print("   - Database seeding/corruption (/seed-database)")
            print("   - Version information disclosure (/users-version)")
            return False
        else:
            print("\n🛡️ All admin.py endpoints properly secured!")
            print("✅ Critical authentication bypass vulnerability FIXED!")
            return True


def test_admin_py_with_invalid_token():
    """Test that invalid admin tokens are rejected by admin.py endpoints."""
    
    with app.test_client() as client:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer fake_admin_token_456'
        }
        
        # Test the most critical endpoint - all-users data dump
        response = client.get('/api/admin/all-users', headers=headers)
        
        print(f"Invalid admin token test (admin.py): {response.status_code}")
        if response.status_code == 401:
            print("✅ Invalid admin token properly rejected by admin.py")
            return True
        else:
            print("❌ Invalid admin token was accepted by admin.py!")
            return False


if __name__ == "__main__":
    print("🚨 Testing Critical admin.py Security Vulnerability Fix")
    print("=" * 60)
    print("This tests the authentication bypass found in admin.py that allowed:")
    print("- Anonymous access to ALL user data via /api/admin/all-users")
    print("- Database seeding/corruption via /api/admin/seed-database")
    print("- Information disclosure via /api/admin/users-version")
    print("=" * 60)
    
    print("\n1. Testing admin.py endpoint authentication...")
    auth_test = test_admin_py_endpoints_require_authentication()
    
    print("\n2. Testing admin.py invalid token rejection...")
    token_test = test_admin_py_with_invalid_token()
    
    if auth_test and token_test:
        print("\n✅ ALL admin.py SECURITY TESTS PASSED!")
        print("🛡️ Critical authentication bypass vulnerability has been FIXED!")
        print("🔒 admin.py endpoints are now properly secured.")
    else:
        print("\n❌ admin.py SECURITY TESTS FAILED!")
        print("🚨 Critical authentication bypass vulnerability still exists!")
        print("⚠️  Immediate action required to prevent data breaches!")