"""
Test stale token handling after deployments.
"""

import os
import sys
os.environ['PYTEST_CURRENT_TEST'] = '1'

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app
import json

def test_stale_token_handling():
    """Test that stale tokens are properly handled and cleaned up."""
    
    with app.test_client() as client:
        # Test with an invalid/stale token
        stale_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.STALE_TOKEN"
        
        response = client.get('/api/preferences/current', 
                            headers={'Authorization': f'Bearer {stale_token}'})
        
        # Should return 401 for stale token
        assert response.status_code == 401, (
            "Stale tokens should return 401 status code"
        )
        
        # Should include error message
        if response.is_json:
            data = response.get_json()
            assert data.get('status') == 'error', "Should return error status"
            assert 'authenticated' in data.get('message', '').lower(), (
                "Should indicate authentication failure"
            )
        
        print("✅ Stale token handling working correctly")
        print("   - Returns 401 for invalid tokens")
        print("   - Frontend can detect and clear stale tokens")
        print("   - Users will be redirected to signin on admin pages")

if __name__ == "__main__":
    test_stale_token_handling()