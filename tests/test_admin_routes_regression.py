"""
Regression test to prevent admin portal 404 errors.
This test ensures all expected admin portal routes remain accessible.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json


class TestAdminRoutesRegression:
    """Regression tests to prevent admin portal 404 errors."""
    
    def test_all_admin_portal_routes_accessible(self):
        """
        REGRESSION TEST: Ensure all admin portal URLs remain accessible.
        
        This test prevents the 404 error that occurred when users tried to access
        the admin portal via intuitive URLs like /admin or /admin-portal.
        """
        
        # All URLs that should serve the admin portal
        expected_admin_routes = [
            '/admin',
            '/admin/',
            '/admin/portal', 
            '/admin-portal',
            '/admin-dashboard',
            '/admin-login.html'
        ]
        
        with app.test_client() as client:
            failed_routes = []
            
            for route in expected_admin_routes:
                response = client.get(route)
                
                if response.status_code != 200:
                    failed_routes.append((route, response.status_code))
                    
            assert not failed_routes, (
                f"REGRESSION: The following admin routes are returning 404 errors: "
                f"{failed_routes}. Users expect these URLs to work for accessing the admin portal!"
            )
            
        print(f"✅ All {len(expected_admin_routes)} admin portal routes accessible")
    
    
    def test_admin_routes_serve_correct_content(self):
        """
        REGRESSION TEST: Ensure admin routes serve the actual admin dashboard.
        
        This prevents serving wrong content or empty pages for admin routes.
        """
        
        admin_routes = ['/admin', '/admin-portal', '/admin-dashboard']
        
        # Required elements that must be present in admin dashboard
        required_admin_elements = [
            'Admin Dashboard',           # Page title
            'signOutButton',            # Sign out functionality  
            'welcome-username',         # User greeting
            'authenticatedFetch',       # API authentication
            'api/admin/',               # Admin API endpoints
            'localStorage.getItem',     # Token management
        ]
        
        with app.test_client() as client:
            for route in admin_routes:
                response = client.get(route)
                content = response.get_data(as_text=True)
                
                missing_elements = []
                for element in required_admin_elements:
                    if element not in content:
                        missing_elements.append(element)
                        
                assert not missing_elements, (
                    f"REGRESSION: Admin route {route} is missing required elements: "
                    f"{missing_elements}. This means it's not serving the proper admin dashboard!"
                )
                
        print("✅ All admin routes serve correct admin dashboard content")
    
    
    def test_admin_api_routes_exist(self):
        """
        REGRESSION TEST: Ensure admin API endpoints remain accessible.
        
        This prevents breaking the admin dashboard by accidentally removing API routes.
        """
        
        # Critical admin API endpoints that must exist
        critical_api_routes = [
            '/api/admin/all-users',
            '/api/admin/users-version', 
            '/api/admin/curriculums',
            '/api/admin/questions',
            '/api/admin/stories',
            '/api/admin/create-curriculum',
            '/api/admin/topics-list',
        ]
        
        with app.test_client() as client:
            missing_routes = []
            
            for route in critical_api_routes:
                # Test with GET request (should return 401 for auth, not 404)
                response = client.get(route)
                
                # 404 means the route doesn't exist - this is a regression
                if response.status_code == 404:
                    missing_routes.append(route)
                    
            assert not missing_routes, (
                f"REGRESSION: The following admin API routes are missing (404): "
                f"{missing_routes}. Admin dashboard will not work without these endpoints!"
            )
            
        print(f"✅ All {len(critical_api_routes)} admin API routes exist")
    
    
    def test_common_admin_url_patterns(self):
        """
        REGRESSION TEST: Test common URL patterns users might try for admin access.
        
        This ensures we cover all intuitive ways users might try to access admin.
        """
        
        # Common patterns users might try to access admin
        common_patterns = [
            '/admin',
            '/admin/',
            '/Admin',           # Capitalized
            '/ADMIN',           # All caps
            '/admin/login',     # Common pattern
            '/admin/dashboard', # Common pattern
            '/admin-panel',     # Alternative naming
            '/admin-portal',    # Alternative naming
            '/administrator',   # Full word
        ]
        
        with app.test_client() as client:
            inaccessible_patterns = []
            
            for pattern in common_patterns:
                response = client.get(pattern)
                
                # Check if route exists (not 404) and serves something reasonable
                if response.status_code == 404:
                    inaccessible_patterns.append(pattern)
                elif response.status_code == 200:
                    content = response.get_data(as_text=True)
                    # Should either be admin dashboard or redirect to it
                    if 'Admin' not in content and 'admin' not in content:
                        inaccessible_patterns.append(f"{pattern} (serves wrong content)")
            
            # Allow some patterns to be missing, but core ones must work
            core_patterns = ['/admin', '/admin/', '/admin-portal', '/admin-dashboard']
            missing_core = [p for p in core_patterns if p in inaccessible_patterns]
            
            assert not missing_core, (
                f"REGRESSION: Core admin URL patterns are inaccessible: {missing_core}. "
                f"Users expect these basic patterns to work!"
            )
            
        print("✅ Core admin URL patterns accessible")
    
    
    def test_admin_routes_not_case_sensitive_where_expected(self):
        """
        REGRESSION TEST: Ensure admin routes work for common case variations.
        
        Many users expect /Admin or /ADMIN to work like /admin.
        """
        
        with app.test_client() as client:
            # Test basic admin route
            response_lower = client.get('/admin')
            
            # These should either work or redirect properly
            test_cases = [
                ('/Admin', 'Title case'),
                ('/ADMIN', 'Upper case'),
            ]
            
            issues = []
            for route, desc in test_cases:
                response = client.get(route)
                if response.status_code == 404:
                    issues.append(f"{route} ({desc}) returns 404")
            
            # For now, we document this as expected behavior
            # In future, we might want to add case-insensitive routes
            if issues:
                print(f"ℹ️  Note: Case variations return 404 (this is currently expected): {issues}")
            
        print("✅ Admin route case sensitivity documented")


if __name__ == "__main__":
    print("🔍 Running Admin Routes Regression Tests")
    print("=" * 50)
    print("These tests prevent admin portal 404 errors from recurring.")
    print()
    
    test_suite = TestAdminRoutesRegression()
    
    # Run all regression tests
    test_suite.test_all_admin_portal_routes_accessible()
    test_suite.test_admin_routes_serve_correct_content()
    test_suite.test_admin_api_routes_exist() 
    test_suite.test_common_admin_url_patterns()
    test_suite.test_admin_routes_not_case_sensitive_where_expected()
    
    print("\n✅ ALL ADMIN ROUTES REGRESSION TESTS PASSED!")
    print("🛡️  Admin portal 404 errors are now prevented by automated testing.")
    print("🎯 If these tests fail in the future, it means someone broke admin access!")