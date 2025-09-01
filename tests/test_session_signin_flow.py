"""
Test the full signin flow to identify session persistence issues.
This simulates what happens when a user signs in and then navigates to dashboard.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json


def test_signin_flow_session_persistence():
    """Test that session persists after signin for preferences access."""
    
    with app.test_client() as client:
        print("🔧 Testing Complete Signin Flow")
        print("=" * 40)
        
        # Step 1: Simulate a successful signin by manually setting session
        # (since we don't have test user in DB)
        print("1. Simulating successful signin...")
        with client.session_transaction() as sess:
            sess['user_id'] = 999  # Test user ID
            sess['user_type'] = 'student'
            sess['session_token'] = 'test_token_123'
        
        # Step 2: Test preferences endpoint (this is what fails in production)
        print("2. Testing preferences endpoint after signin...")
        response = client.get('/api/preferences/current')
        
        print(f"   Status: {response.status_code}")
        if response.is_json:
            data = response.get_json()
            print(f"   Response: {data}")
            
            if response.status_code == 401:
                print("   ❌ ISSUE: Getting 401 even with session set!")
                if 'debug' in data:
                    print(f"   Debug info: {data['debug']}")
            else:
                print("   ✅ Success: Session working correctly")
        
        # Step 3: Test what happens if we navigate to another page (like dashboard)
        print("3. Testing dashboard access (simulates navigation)...")
        dashboard_response = client.get('/dashboard.html')
        print(f"   Dashboard status: {dashboard_response.status_code}")
        
        # Step 4: Test preferences again after navigation
        print("4. Testing preferences after page navigation...")
        response2 = client.get('/api/preferences/current')
        print(f"   Status after navigation: {response2.status_code}")
        
        if response.status_code != response2.status_code:
            print("   ❌ ISSUE: Session lost during navigation!")
        else:
            print("   ✅ Session persisted through navigation")


def test_signin_endpoint_sets_session():
    """Test if the signin endpoint properly sets session when credentials are valid."""
    
    print("\n🔧 Testing Signin Endpoint Session Setting")
    print("=" * 40)
    
    with app.test_client() as client:
        # Try signin with test credentials (will fail but we can see session behavior)
        signin_data = {
            "username": "nonexistent_user", 
            "password": "test123456"
        }
        
        print("1. Attempting signin...")
        response = client.post('/api/signin',
                             data=json.dumps(signin_data),
                             content_type='application/json')
        
        print(f"   Signin status: {response.status_code}")
        print(f"   Signin response: {response.get_json()}")
        
        # Check session state after signin attempt
        print("2. Checking session after signin attempt...")
        with client.session_transaction() as sess:
            print(f"   Session keys: {list(sess.keys())}")
            print(f"   Has user_id: {'user_id' in sess}")
            print(f"   Has session_token: {'session_token' in sess}")


def test_session_configuration_issue():
    """Test for common session configuration issues."""
    
    print("\n🔧 Testing Session Configuration Issues")
    print("=" * 40)
    
    config = app.config
    issues = []
    
    # Check SECRET_KEY
    if not config.get('SECRET_KEY'):
        issues.append("No SECRET_KEY set")
    
    # Check session settings that might cause issues
    if config.get('SESSION_COOKIE_SECURE') and not app.debug:
        issues.append("SESSION_COOKIE_SECURE=True but not using HTTPS")
    
    # Check if sessions are working at all
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['test'] = 'value'
        
        with client.session_transaction() as sess:
            if sess.get('test') != 'value':
                issues.append("Basic session storage not working")
    
    if issues:
        print("   ❌ Session configuration issues found:")
        for issue in issues:
            print(f"      - {issue}")
    else:
        print("   ✅ Session configuration appears correct")
    
    return issues


if __name__ == "__main__":
    test_signin_flow_session_persistence()
    test_signin_endpoint_sets_session() 
    issues = test_session_configuration_issue()
    
    print(f"\n{'='*60}")
    print("💡 DIAGNOSIS:")
    if issues:
        print("   Session configuration problems detected - fix these first")
    else:
        print("   Session config OK - issue likely in signin flow or browser")
    print("\n   Common causes of session loss:")
    print("   1. Browser blocking cookies (especially in dev with HTTP)")
    print("   2. Session expires too quickly") 
    print("   3. Cross-origin issues between signin and dashboard")
    print("   4. Flask session not properly configured for environment")
    print(f"{'='*60}")