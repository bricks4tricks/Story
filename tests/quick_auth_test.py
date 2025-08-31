#!/usr/bin/env python3
"""
Quick test to verify admin authentication is working
"""
import pytest
from unittest.mock import patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_auth_utils import mock_admin_auth, get_admin_headers
from app import app

def test_simple_auth():
    """Test that admin auth works with a simple endpoint."""
    
    with app.test_client() as client:
        with mock_admin_auth():
            # Test with proper headers
            headers = get_admin_headers()
            response = client.get('/api/admin/create-tables', headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.get_data()}")
            
            # Check if we get past authentication (should not be 401/403)
            assert response.status_code != 401, "Authentication should not fail"
            assert response.status_code != 403, "Authorization should not fail"

if __name__ == "__main__":
    test_simple_auth()
    print("✅ Basic auth test completed")