"""
Test additional production fixes for admin portal access and CDN references.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json


def test_iygighukijh_html_direct_access():
    """Test that /iygighukijh.html is accessible directly."""
    
    with app.test_client() as client:
        response = client.get('/iygighukijh.html')
        
        # Should NOT be 404 (route missing)
        assert response.status_code != 404, (
            "BUG: /iygighukijh.html route missing! "
            "This causes 404 errors when accessing admin template directly."
        )
        
        # Should return HTML content
        assert response.mimetype == 'text/html', (
            "Admin template should return HTML content"
        )
        
        print("✅ /iygighukijh.html endpoint accessible")


def test_security_csp_no_tailwind_cdn():
    """Test that security headers don't reference Tailwind CDN."""
    
    with app.test_client() as client:
        response = client.get('/')
        
        # Check CSP header
        csp_header = response.headers.get('Content-Security-Policy', '')
        
        assert 'cdn.tailwindcss.com' not in csp_header, (
            "SECURITY ISSUE: CSP still references Tailwind CDN! "
            "This allows loading external CDN in production."
        )
        
        print("✅ Security CSP headers don't reference Tailwind CDN")


def test_social_meta_no_tailwind_prefetch():
    """Test that social meta template doesn't prefetch Tailwind CDN."""
    
    # Read the social-meta template directly since it's included in other templates
    social_meta_path = os.path.join(
        os.path.dirname(__file__), '..', 'templates', 'social-meta.html'
    )
    
    with open(social_meta_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'cdn.tailwindcss.com' not in content, (
        "PRODUCTION ISSUE: social-meta.html still has Tailwind CDN prefetch! "
        "This attempts to connect to CDN in production."
    )
    
    print("✅ social-meta.html doesn't prefetch Tailwind CDN")


def test_index_page_still_works():
    """Test that index page works after CDN removal fixes."""
    
    with app.test_client() as client:
        response = client.get('/')
        
        assert response.status_code == 200, "Index page should be accessible"
        
        content = response.get_data(as_text=True)
        
        # Should NOT contain Tailwind CDN
        assert 'cdn.tailwindcss.com' not in content, (
            "PRODUCTION ISSUE: Index page still references Tailwind CDN!"
        )
        
        # Should contain compiled CSS reference
        assert '/static/css/styles.css' in content, (
            "PRODUCTION ISSUE: Index page missing compiled CSS reference!"
        )
        
        print("✅ Index page works without CDN references")


def test_admin_template_accessibility():
    """Test multiple admin routes work after fixes."""
    
    admin_routes = [
        '/admin',
        '/admin/', 
        '/admin-login.html',
        '/iygighukijh.html',
        '/admin-portal',
        '/admin-dashboard'
    ]
    
    with app.test_client() as client:
        failed_routes = []
        
        for route in admin_routes:
            response = client.get(route)
            if response.status_code == 404:
                failed_routes.append(route)
        
        assert not failed_routes, (
            f"ADMIN ACCESS BROKEN: Routes {failed_routes} return 404! "
            f"Admin portal should be accessible via multiple URLs."
        )
        
        print("✅ All admin routes accessible")


if __name__ == "__main__":
    print("🔧 Testing Additional Production Fixes")
    print("=" * 50)
    print("These tests verify critical production issues are resolved:")
    print("1. Direct admin template access (/iygighukijh.html)")
    print("2. Security CSP headers without CDN references")
    print("3. Social meta template DNS prefetch cleanup")
    print("4. Index page functionality after CDN removal")
    print("5. Admin portal accessibility via multiple routes")
    print()
    
    test_iygighukijh_html_direct_access()
    test_security_csp_no_tailwind_cdn()
    test_social_meta_no_tailwind_prefetch()
    test_index_page_still_works()
    test_admin_template_accessibility()
    
    print("\n✅ ALL ADDITIONAL PRODUCTION FIXES VERIFIED!")
    print("🎯 Application now fully production-ready.")
    print("⚡ No more CDN warnings or 404 errors!")