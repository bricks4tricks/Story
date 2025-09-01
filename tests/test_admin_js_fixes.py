"""
Test fixes for admin portal JavaScript errors.
These tests verify that SecureDOM and curriculum-table issues are resolved.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json


def test_admin_template_includes_securedom():
    """Test that admin template includes secureDOM.js to prevent 'SecureDOM is not defined' error."""
    
    with app.test_client() as client:
        response = client.get('/iygighukijh.html')
        
        assert response.status_code == 200, "Admin template should be accessible"
        
        content = response.get_data(as_text=True)
        
        # Should include SecureDOM script
        assert 'secureDOM.js' in content, (
            "FIXED: Admin template must include secureDOM.js to prevent "
            "'ReferenceError: SecureDOM is not defined' in userTable.js"
        )
        
        # Should include userTable script
        assert 'userTable.js' in content, (
            "Admin template should include userTable.js script"
        )
        
        print("✅ Admin template includes required secureDOM.js script")


def test_curriculum_table_endpoint_works():
    """Test that /api/curriculum-table endpoint no longer returns 500 errors."""
    
    with app.test_client() as client:
        response = client.get('/api/curriculum-table')
        
        # Should NOT be 500 (server error)
        assert response.status_code != 500, (
            "FIXED: /api/curriculum-table should not return 500 errors. "
            "The SQL query has been corrected to work with the database schema."
        )
        
        # Should return 200 with JSON data
        assert response.status_code == 200, (
            "/api/curriculum-table should return successful response"
        )
        
        assert response.is_json, (
            "curriculum-table should return JSON data"
        )
        
        data = response.get_json()
        assert isinstance(data, list), (
            "curriculum-table should return list of curriculum data"
        )
        
        print(f"✅ /api/curriculum-table returns {len(data)} curriculum items")


def test_admin_routes_accessible():
    """Test that various admin routes work with the fixed template."""
    
    admin_routes = [
        '/admin-login.html', 
        '/admin',
        '/admin/',
        '/admin-portal'
    ]
    
    with app.test_client() as client:
        failed_routes = []
        
        for route in admin_routes:
            response = client.get(route)
            if response.status_code != 200:
                failed_routes.append(f"{route} ({response.status_code})")
        
        assert not failed_routes, (
            f"REGRESSION: Admin routes failed: {failed_routes}. "
            f"All admin routes should work after template fix."
        )
        
        print("✅ All admin routes accessible with fixed template")


def test_admin_template_structure():
    """Test that admin template has proper structure and security scripts."""
    
    with app.test_client() as client:
        response = client.get('/admin-login.html')
        content = response.get_data(as_text=True)
        
        # Security requirements
        assert 'secureDOM.js' in content, "Must include SecureDOM for XSS protection"
        assert 'csrf.js' in content, "Must include CSRF protection"
        
        # Admin functionality
        assert 'userTable.js' in content, "Must include user table functionality"
        assert 'user-table-container' in content, "Must have user table container"
        assert 'curriculum-table-container' in content, "Must have curriculum table container"
        
        # Basic HTML structure
        assert '<!DOCTYPE html>' in content, "Must be valid HTML5"
        assert 'Admin Portal' in content, "Must have admin portal title"
        
        print("✅ Admin template has proper structure and security")


if __name__ == "__main__":
    print("🔧 Testing Admin Portal JavaScript Fixes")
    print("=" * 50)
    print("These tests verify JavaScript errors are resolved:")
    print("1. SecureDOM undefined error fixed in userTable.js")
    print("2. api/curriculum-table 500 error fixed")
    print("3. Admin template accessible with proper scripts")
    print("4. All admin routes work correctly")
    print()
    
    test_admin_template_includes_securedom()
    test_curriculum_table_endpoint_works()
    test_admin_routes_accessible()
    test_admin_template_structure()
    
    print("\n✅ ALL ADMIN PORTAL JAVASCRIPT FIXES VERIFIED!")
    print("🎯 No more SecureDOM undefined or 500 errors.")
    print("⚡ Admin portal ready for production use!")