"""
Test admin portal access routes.
Ensures admin portal is accessible via multiple URL patterns.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json


def test_admin_portal_routes():
    """Test that various admin portal URLs return the admin dashboard."""
    
    admin_urls = [
        '/admin',
        '/admin/',
        '/admin/portal',
        '/admin-portal',
        '/admin-dashboard',
        '/admin-login.html'
    ]
    
    with app.test_client() as client:
        for url in admin_urls:
            print(f"Testing admin portal access: {url}")
            response = client.get(url)
            
            assert response.status_code == 200, f"Admin portal URL {url} should return 200, got {response.status_code}"
            assert 'Admin Dashboard' in response.get_data(as_text=True), f"Admin portal URL {url} should contain 'Admin Dashboard'"
            
        print("✅ All admin portal URLs accessible!")


def test_admin_portal_contains_required_elements():
    """Test that the admin portal contains required dashboard elements."""
    
    with app.test_client() as client:
        response = client.get('/admin')
        content = response.get_data(as_text=True)
        
        # Check for key admin dashboard elements
        required_elements = [
            'Admin Dashboard',
            'signOutButton',
            'welcome-username',
            'authenticatedFetch'
        ]
        
        for element in required_elements:
            assert element in content, f"Admin portal missing required element: {element}"
            
        print("✅ Admin portal contains all required elements!")


if __name__ == "__main__":
    print("🔧 Testing Admin Portal Access")
    print("=" * 40)
    
    test_admin_portal_routes()
    test_admin_portal_contains_required_elements()
    
    print("\n✅ ALL ADMIN PORTAL ACCESS TESTS PASSED!")
    print("🎯 Admin portal is now accessible via multiple URLs.")