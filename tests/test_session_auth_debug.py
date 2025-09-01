"""
Debug the session authentication issue causing 401 errors.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json

def test_session_persistence_debug():
    """Test that session persists between signin and API calls."""
    
    print("🔍 DEBUGGING SESSION PERSISTENCE ISSUE")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test the signin flow
        signin_data = {
            "username": "admin",  # Try with common admin username
            "password": "admin123"  # Common admin password
        }
        
        print(f"1. Attempting signin with {signin_data['username']}")
        signin_response = client.post('/api/signin',
                                    data=json.dumps(signin_data),
                                    content_type='application/json')
        
        print(f"   Signin status: {signin_response.status_code}")
        if signin_response.is_json:
            signin_data_response = signin_response.get_json()
            print(f"   Signin response: {signin_data_response}")
        
        # Check if session was set (we can see if cookies were set)
        print(f"   Response headers: {dict(signin_response.headers)}")
        
        # Now try to access preferences endpoint immediately after signin
        print("\n2. Testing preferences endpoint after signin")
        prefs_response = client.get('/api/preferences/current')
        
        print(f"   Preferences status: {prefs_response.status_code}")
        if prefs_response.is_json:
            prefs_data = prefs_response.get_json()
            print(f"   Preferences response: {prefs_data}")
        
        # Test with Authorization header as well
        print("\n3. Testing with Authorization header")
        if signin_response.is_json and signin_response.get_json().get('token'):
            token = signin_response.get_json()['token']
            auth_prefs_response = client.get('/api/preferences/current', 
                                           headers={'Authorization': f'Bearer {token}'})
            print(f"   With Bearer token status: {auth_prefs_response.status_code}")
            if auth_prefs_response.is_json:
                auth_prefs_data = auth_prefs_response.get_json()
                print(f"   With Bearer token response: {auth_prefs_data}")
        
        print("\n✅ SESSION DEBUG TEST COMPLETE")
        print("Issue identified: Session authentication flow needs investigation")

if __name__ == "__main__":
    test_session_persistence_debug()