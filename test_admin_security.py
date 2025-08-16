"""
Test script to verify that admin endpoints are properly secured.
Tests that unauthorized users cannot access admin functionality.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

from app import app
import json


def test_admin_endpoints_require_authentication():
    """Test that admin endpoints reject unauthenticated requests."""
    
    admin_endpoints = [
        ('/api/admin/edit-user/1', 'PUT', {'username': 'hacker', 'email': 'hack@evil.com', 'userType': 'Admin'}),
        ('/api/admin/delete-user/1', 'DELETE', {}),
        ('/api/admin/topics-list', 'GET', {}),
        ('/api/admin/add-question', 'POST', {'topicId': 1, 'questionText': 'hack', 'questionType': 'Multiple'}),
        ('/api/admin/questions', 'GET', {}),
        ('/api/admin/stories', 'GET', {}),
        ('/api/admin/delete-story/1', 'DELETE', {}),
        ('/api/admin/save-story', 'POST', {'topicId': 1, 'content': 'malicious content'}),
        ('/api/admin/add-video', 'POST', {'topicId': 1, 'youtubeUrl': 'https://evil.com'}),
        ('/api/admin/curriculums', 'GET', {}),
        ('/api/admin/create-curriculum', 'POST', {'name': 'Evil Curriculum'}),
        ('/api/admin/delete-curriculum/1', 'DELETE', {}),
    ]
    
    with app.test_client() as client:
        failed_endpoints = []
        protected_count = 0
        
        for endpoint, method, data in admin_endpoints:
            print(f"Testing {method} {endpoint}...")
            
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'POST':
                response = client.post(endpoint, json=data, headers={'Content-Type': 'application/json'})
            elif method == 'PUT':
                response = client.put(endpoint, json=data, headers={'Content-Type': 'application/json'})
            elif method == 'DELETE':
                response = client.delete(endpoint, json=data, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 401:
                print(f"✅ {endpoint} properly protected")
                protected_count += 1
            else:
                print(f"❌ {endpoint} SECURITY BREACH! Status: {response.status_code}")
                failed_endpoints.append((endpoint, response.status_code))
        
        print(f"\n🔒 Security Test Results:")
        print(f"✅ Protected endpoints: {protected_count}")
        print(f"❌ Vulnerable endpoints: {len(failed_endpoints)}")
        
        if failed_endpoints:
            print("\n🚨 CRITICAL SECURITY VULNERABILITIES:")
            for endpoint, status in failed_endpoints:
                print(f"   - {endpoint} (HTTP {status})")
            return False
        else:
            print("\n🛡️ All admin endpoints properly secured!")
            return True


def test_admin_with_invalid_token():
    """Test that invalid admin tokens are rejected."""
    
    with app.test_client() as client:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer fake_admin_token_123'
        }
        
        response = client.delete('/api/admin/delete-user/999', headers=headers)
        
        print(f"Invalid admin token test: {response.status_code}")
        if response.status_code == 401:
            print("✅ Invalid admin token properly rejected")
            return True
        else:
            print("❌ Invalid admin token was accepted!")
            return False


if __name__ == "__main__":
    print("🔒 Testing Admin Security Fixes")
    print("=" * 50)
    
    print("\n1. Testing admin endpoint authentication...")
    auth_test = test_admin_endpoints_require_authentication()
    
    print("\n2. Testing invalid admin token rejection...")
    token_test = test_admin_with_invalid_token()
    
    if auth_test and token_test:
        print("\n✅ ALL ADMIN SECURITY TESTS PASSED!")
        print("🛡️ Admin endpoints are now properly secured against unauthorized access.")
    else:
        print("\n❌ SECURITY TESTS FAILED!")
        print("🚨 Admin endpoints still have vulnerabilities!")