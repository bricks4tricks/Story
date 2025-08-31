"""
Debug session handling for authenticated users.
This helps diagnose why authenticated users get 401 on preferences endpoint.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json


def test_session_persistence_after_signin():
    """Test if session persists after signin and preferences endpoint works."""
    
    with app.test_client() as client:
        # Simulate signin (this would normally set session)
        with client.session_transaction() as sess:
            sess['user_id'] = 123  # Simulate logged in user
            sess['user_type'] = 'student'
        
        # Now try to access preferences
        response = client.get('/api/preferences/current')
        
        print(f"Response status: {response.status_code}")
        if response.is_json:
            print(f"Response data: {response.get_json()}")
        
        # Should NOT be 401 since we have session
        if response.status_code == 401:
            print("❌ ISSUE: Still getting 401 even with session set!")
            print("This suggests session handling is not working properly")
        else:
            print("✅ Session handling works - preferences accessible")


def test_actual_signin_flow():
    """Test the actual signin flow to see if session gets set properly."""
    
    with app.test_client() as client:
        # Try the actual signin endpoint (will fail without valid user but we can see session behavior)
        signin_data = {
            "username": "test_user",  # Non-existent user
            "password": "test_password"
        }
        
        response = client.post('/api/signin', 
                             data=json.dumps(signin_data),
                             content_type='application/json')
        
        print(f"Signin response status: {response.status_code}")
        if response.is_json:
            print(f"Signin response: {response.get_json()}")
        
        # Check if we can see any session cookies (compatible with newer Werkzeug)
        try:
            cookies = [cookie for cookie in client.cookie_jar]
        except AttributeError:
            # Newer Werkzeug versions don't expose cookie_jar directly
            # We can still check response headers for Set-Cookie
            cookies = []
            set_cookie_headers = response.headers.getlist('Set-Cookie')
            for cookie_header in set_cookie_headers:
                cookies.append(cookie_header)
        print(f"Cookies after signin attempt: {cookies}")


def test_session_configuration():
    """Test Flask session configuration."""
    
    print("Flask session configuration:")
    print(f"SECRET_KEY set: {'yes' if app.config.get('SECRET_KEY') else 'no'}")
    print(f"SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE')}")
    print(f"SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY')}")
    print(f"SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE')}")
    print(f"PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME')}")


if __name__ == "__main__":
    print("🔧 Debugging Session Handling")
    print("=" * 50)
    print()
    
    test_session_configuration()
    print()
    
    test_session_persistence_after_signin()
    print()
    
    test_actual_signin_flow()
    print()
    
    print("💡 If session persistence fails, the issue might be:")
    print("   1. SESSION_COOKIE_SECURE=True but running on HTTP")
    print("   2. Session storage/configuration issue")
    print("   3. Cookie domain/path problems")
    print("   4. Browser security blocking cookies")