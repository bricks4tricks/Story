"""
Test production fixes for admin portal:
1. Tailwind CDN replaced with compiled CSS
2. Missing get_topics route added
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json


def test_admin_portal_uses_compiled_css_not_cdn():
    """
    PRODUCTION FIX: Ensure admin portal uses compiled CSS instead of Tailwind CDN.
    
    This prevents the production warning:
    "cdn.tailwindcss.com should not be used in production"
    """
    
    with app.test_client() as client:
        response = client.get('/admin')
        content = response.get_data(as_text=True)
        
        # Should NOT contain Tailwind CDN
        assert 'cdn.tailwindcss.com' not in content, (
            "PRODUCTION ISSUE: Admin portal still uses Tailwind CDN! "
            "This shows warning in production. Should use compiled CSS."
        )
        
        # Should contain compiled CSS reference
        assert '/static/css/styles.css' in content, (
            "PRODUCTION ISSUE: Admin portal missing compiled CSS reference! "
            "Without this, styling will be broken."
        )
        
        print("✅ Admin portal uses compiled CSS (not CDN)")


def test_get_topics_route_exists():
    """
    BUG FIX: Ensure /get_topics/<curriculum>/<unit> route exists.
    
    This fixes the 404 error when admin portal tries to load topics.
    """
    
    with app.test_client() as client:
        # Test the route exists (even if it returns empty data due to no DB)
        response = client.get('/get_topics/Math/Algebra')
        
        # Should NOT be 404 (route missing)
        assert response.status_code != 404, (
            "BUG: /get_topics/<curriculum>/<unit> route missing! "
            "This causes 404 errors in admin portal when loading topics."
        )
        
        # Should return JSON (even if empty)
        assert response.is_json, (
            "BUG: /get_topics route should return JSON data for admin portal"
        )
        
        print("✅ /get_topics route exists and returns JSON")


def test_admin_portal_api_endpoints_accessible():
    """
    REGRESSION TEST: Ensure admin portal API endpoints are accessible.
    
    Tests endpoints that the admin template JavaScript calls.
    """
    
    critical_endpoints = [
        '/get_curriculums',
        '/get_units/Math',
        '/get_topics/Math/Algebra',
    ]
    
    with app.test_client() as client:
        missing_endpoints = []
        
        for endpoint in critical_endpoints:
            response = client.get(endpoint)
            
            if response.status_code == 404:
                missing_endpoints.append(endpoint)
                
        assert not missing_endpoints, (
            f"ADMIN PORTAL BROKEN: Missing API endpoints {missing_endpoints}! "
            f"Admin portal JavaScript will fail without these."
        )
        
        print("✅ All admin portal API endpoints accessible")


def test_admin_template_has_no_obvious_issues():
    """
    QUALITY CHECK: Ensure admin template doesn't have obvious issues.
    """
    
    with app.test_client() as client:
        response = client.get('/admin')
        content = response.get_data(as_text=True)
        
        # Check for common issues
        issues = []
        
        if 'cdn.tailwindcss.com' in content:
            issues.append("Uses Tailwind CDN (production warning)")
            
        if '/static/css/styles.css' not in content:
            issues.append("Missing compiled CSS reference")
            
        if 'Admin Dashboard' not in content:
            issues.append("Missing admin dashboard title")
            
        if 'authenticatedFetch' not in content:
            issues.append("Missing authentication functions")
            
        assert not issues, (
            f"ADMIN PORTAL ISSUES: {issues}. "
            f"These will cause problems in production."
        )
        
        print("✅ Admin template quality checks passed")


if __name__ == "__main__":
    print("🔧 Testing Admin Portal Production Fixes")
    print("=" * 50)
    print("These tests verify production issues are resolved:")
    print("1. Tailwind CDN warning fixed")  
    print("2. Missing route 404 error fixed")
    print()
    
    test_admin_portal_uses_compiled_css_not_cdn()
    test_get_topics_route_exists()
    test_admin_portal_api_endpoints_accessible()
    test_admin_template_has_no_obvious_issues()
    
    print("\n✅ ALL ADMIN PORTAL PRODUCTION FIXES VERIFIED!")
    print("🎯 Admin portal ready for production deployment.")
    print("⚡ No more Tailwind CDN warnings or 404 errors!")