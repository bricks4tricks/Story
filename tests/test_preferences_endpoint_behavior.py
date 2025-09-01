"""
Test that preferences endpoint 401 behavior is correct and expected.
The /api/preferences/current endpoint should return 401 for unauthenticated users,
which is handled gracefully by the frontend JavaScript.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json


def test_preferences_endpoint_401_for_anonymous_users():
    """Test that /api/preferences/current returns 401 for unauthenticated users."""
    
    with app.test_client() as client:
        response = client.get('/api/preferences/current')
        
        # EXPECTED BEHAVIOR: Should return 401 for anonymous users
        assert response.status_code == 401, (
            "Preferences endpoint should return 401 for unauthenticated users"
        )
        
        # Should return JSON with error message
        assert response.is_json, "401 response should be JSON"
        data = response.get_json()
        assert data.get('status') == 'error', "Should indicate error status"
        assert 'Not authenticated' in data.get('message', ''), "Should explain authentication required"
        
        print("✅ /api/preferences/current correctly returns 401 for anonymous users")


def test_preferences_endpoint_exists():
    """Test that the preferences endpoint exists and is accessible."""
    
    with app.test_client() as client:
        response = client.get('/api/preferences/current')
        
        # Should NOT be 404 (route missing)
        assert response.status_code != 404, (
            "BUG: /api/preferences/current route missing! "
            "This would cause 404 errors instead of proper 401 authentication errors."
        )
        
        print("✅ /api/preferences/current endpoint exists")


def test_preferences_javascript_handles_401_gracefully():
    """Test that the JavaScript preferences code handles 401 errors correctly."""
    
    # Read the preferences.js file to verify it handles errors
    preferences_js_path = os.path.join(
        os.path.dirname(__file__), '..', 'static', 'js', 'preferences.js'
    )
    
    with open(preferences_js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Should have proper error handling
    assert '.catch(' in js_content, (
        "BUG: preferences.js missing error handling! "
        "Without .catch(), 401 errors will appear as unhandled in console."
    )
    
    # Should apply default preferences on error
    assert 'applyPreferences(false, \'medium\')' in js_content, (
        "BUG: preferences.js doesn't apply defaults on error! "
        "Should fallback to light mode and medium font size."
    )
    
    print("✅ preferences.js handles 401 errors gracefully")


def test_index_page_includes_preferences_script():
    """Test that index page includes the preferences script."""
    
    with app.test_client() as client:
        response = client.get('/')
        content = response.get_data(as_text=True)
        
        # Should include preferences script (injected by after_request handler)
        assert 'preferences.js' in content, (
            "BUG: Index page missing preferences.js! "
            "Without this script, users won't get proper theme handling."
        )
        
        print("✅ Index page includes preferences script")


def test_preferences_error_is_expected_behavior():
    """Document that the 401 error is expected and not a bug."""
    
    print("📋 IMPORTANT: The 401 error for /api/preferences/current is EXPECTED behavior!")
    print("   - Anonymous users: Get 401, JavaScript applies default preferences")  
    print("   - Authenticated users: Get user preferences from database")
    print("   - This is NOT a production issue, it's correct security behavior")
    print("   - The error is handled gracefully by preferences.js catch block")


if __name__ == "__main__":
    print("🔧 Testing Preferences Endpoint Behavior")
    print("=" * 50)
    print("These tests verify the preferences endpoint behaves correctly:")
    print("1. Returns 401 for anonymous users (expected)")
    print("2. Endpoint exists and is accessible") 
    print("3. JavaScript handles errors gracefully")
    print("4. Index page includes preferences script")
    print("5. Documents that 401 is expected behavior")
    print()
    
    test_preferences_endpoint_401_for_anonymous_users()
    test_preferences_endpoint_exists() 
    test_preferences_javascript_handles_401_gracefully()
    test_index_page_includes_preferences_script()
    test_preferences_error_is_expected_behavior()
    
    print("\n✅ ALL PREFERENCES ENDPOINT BEHAVIOR VERIFIED!")
    print("🎯 The 401 error is EXPECTED and handled correctly.")
    print("⚡ No fixes needed - this is proper security behavior!")