"""
Test admin API endpoints to diagnose 500 errors.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'  # Skip env validation

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json


def test_curriculum_table_endpoint_exists():
    """Test that /api/curriculum-table endpoint exists."""
    
    with app.test_client() as client:
        response = client.get('/api/curriculum-table')
        
        # Should NOT be 404 (route missing)
        assert response.status_code != 404, (
            "BUG: /api/curriculum-table route missing! "
            "This would cause 404 errors in admin portal."
        )
        
        print(f"✅ /api/curriculum-table endpoint exists (status: {response.status_code})")


def test_curriculum_table_endpoint_response():
    """Test /api/curriculum-table response and diagnose 500 errors."""
    
    with app.test_client() as client:
        response = client.get('/api/curriculum-table')
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ 500 Internal Server Error detected!")
            print("This indicates a server-side problem:")
            print("  - Database connection issue")
            print("  - SQL query problem") 
            print("  - Missing database tables")
            print("  - Python exception in endpoint")
            
            # Try to get error details
            if response.is_json:
                data = response.get_json()
                print(f"Error response: {data}")
            else:
                print(f"Error response (text): {response.get_data(as_text=True)[:500]}...")
                
        elif response.status_code == 200:
            print("✅ Endpoint working correctly")
            if response.is_json:
                data = response.get_json()
                print(f"Response data preview: {str(data)[:200]}...")
        else:
            print(f"Unexpected status code: {response.status_code}")
            if response.is_json:
                print(f"Response: {response.get_json()}")


def test_admin_template_loads():
    """Test that admin template loads without errors."""
    
    with app.test_client() as client:
        response = client.get('/iygrighukijh.html')
        
        assert response.status_code == 200, (
            "Admin template should be accessible"
        )
        
        content = response.get_data(as_text=True)
        
        # Should include SecureDOM script
        assert 'secureDOM.js' in content, (
            "FIXED: Admin template should include secureDOM.js script"
        )
        
        # Should include admin scripts
        assert 'userTable.js' in content, (
            "Admin template should include userTable.js script"
        )
        
        print("✅ Admin template loads with required scripts")


if __name__ == "__main__":
    print("🔧 Testing Admin API Endpoints")
    print("=" * 50)
    print("These tests diagnose admin portal JavaScript errors:")
    print("1. Check curriculum-table endpoint exists")
    print("2. Diagnose 500 errors in curriculum-table")
    print("3. Verify admin template includes required scripts")
    print()
    
    test_curriculum_table_endpoint_exists()
    test_curriculum_table_endpoint_response()
    test_admin_template_loads()
    
    print("\n✅ ADMIN API ENDPOINTS DIAGNOSIS COMPLETE!")
    print("🎯 Issues identified and documented for fixing.")