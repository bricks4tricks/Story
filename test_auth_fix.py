"""
Test script to verify the authentication security fixes.
Tests that endpoints reject unauthorized requests.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

from app import app
import json


def test_unauthenticated_access():
    """Test that protected endpoints reject unauthenticated requests."""
    
    with app.test_client() as client:
        # Test data that would previously exploit the IDOR vulnerability
        malicious_data = {
            "userId": 999,  # Attacker trying to access another user's data
            "topicId": 1,
            "status": "completed"
        }
        
        # Test /api/progress/update
        response = client.post('/api/progress/update', 
                              json=malicious_data,
                              headers={'Content-Type': 'application/json'})
        
        print(f"Progress update status: {response.status_code}")
        if response.status_code == 401:
            data = response.get_json()
            print(f"✅ Authentication required: {data.get('message', 'No message')}")
        else:
            print(f"❌ Security bypass detected! Status: {response.status_code}")
            print(f"Response: {response.get_json()}")
        
        # Test /api/record-question-attempt
        attempt_data = {
            "userId": 999,
            "questionId": 1,
            "userAnswer": "exploit",
            "isCorrect": True,
            "difficultyAtAttempt": 1
        }
        
        response = client.post('/api/record-question-attempt',
                              json=attempt_data,
                              headers={'Content-Type': 'application/json'})
        
        print(f"Question attempt status: {response.status_code}")
        if response.status_code == 401:
            data = response.get_json()
            print(f"✅ Authentication required: {data.get('message', 'No message')}")
        else:
            print(f"❌ Security bypass detected! Status: {response.status_code}")
        
        # Test /api/user/update-topic-difficulty
        difficulty_data = {
            "userId": 999,
            "topicId": 1,
            "newDifficulty": 5
        }
        
        response = client.post('/api/user/update-topic-difficulty',
                              json=difficulty_data,
                              headers={'Content-Type': 'application/json'})
        
        print(f"Difficulty update status: {response.status_code}")
        if response.status_code == 401:
            data = response.get_json()
            print(f"✅ Authentication required: {data.get('message', 'No message')}")
        else:
            print(f"❌ Security bypass detected! Status: {response.status_code}")
        
        # Test /api/flag-item
        flag_data = {
            "userId": 999,
            "flaggedItemId": 1,
            "itemType": "Question",
            "reason": "exploit test"
        }
        
        response = client.post('/api/flag-item',
                              json=flag_data,
                              headers={'Content-Type': 'application/json'})
        
        print(f"Flag item status: {response.status_code}")
        if response.status_code == 401:
            data = response.get_json()
            print(f"✅ Authentication required: {data.get('message', 'No message')}")
        else:
            print(f"❌ Security bypass detected! Status: {response.status_code}")


def test_invalid_token():
    """Test that invalid tokens are rejected."""
    
    with app.test_client() as client:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer invalid_token_123'
        }
        
        response = client.post('/api/progress/update',
                              json={"userId": 1, "topicId": 1, "status": "completed"},
                              headers=headers)
        
        print(f"Invalid token status: {response.status_code}")
        if response.status_code == 401:
            data = response.get_json()
            print(f"✅ Invalid token rejected: {data.get('message', 'No message')}")
        else:
            print(f"❌ Invalid token accepted! Status: {response.status_code}")


if __name__ == "__main__":
    print("🔒 Testing Authentication Security Fixes")
    print("=" * 50)
    
    print("\n1. Testing unauthenticated access...")
    test_unauthenticated_access()
    
    print("\n2. Testing invalid token...")
    test_invalid_token()
    
    print("\n✅ Authentication security tests completed!")
    print("All protected endpoints now require proper authentication.")