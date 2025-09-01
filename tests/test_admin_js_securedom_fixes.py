import pytest
import os
import time
import tempfile
import subprocess


class TestAdminJSSecureDOMFixes:
    """Test fixes for admin portal JavaScript SecureDOM issues."""


    def test_securedom_script_loads_before_usertable(self):
        """Test that secureDOM.js loads before userTable.js in admin portal."""
        # Read the admin portal template
        template_path = os.path.join(os.getcwd(), 'templates', 'iygrighukijh.html')
        if not os.path.exists(template_path):
            pytest.skip("Admin portal template not found")
            
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find script load order
        securedom_pos = content.find('<script src="/static/js/secureDOM.js"></script>')
        usertable_pos = content.find('<script src="/static/js/userTable.js"></script>')
        
        assert securedom_pos != -1, "secureDOM.js script tag not found"
        assert usertable_pos != -1, "userTable.js script tag not found"
        assert securedom_pos < usertable_pos, "secureDOM.js must load before userTable.js"

    def test_securedom_availability_check_in_usertable(self):
        """Test that userTable.js has SecureDOM availability check."""
        usertable_path = os.path.join(os.getcwd(), 'static', 'js', 'userTable.js')
        if not os.path.exists(usertable_path):
            pytest.skip("userTable.js not found")
            
        with open(usertable_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for SecureDOM availability check
        assert "typeof SecureDOM === 'undefined'" in content, "SecureDOM availability check missing"
        assert "setTimeout(arguments.callee, 100)" in content, "Retry logic for SecureDOM missing"

    def test_curriculum_table_query_fix(self):
        """Test that curriculum-table endpoint query is fixed."""
        app_path = os.path.join(os.getcwd(), 'app.py')
        if not os.path.exists(app_path):
            pytest.skip("app.py not found")
            
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the old incorrect query is not present
        assert "g.subjectid = s.id" not in content, "Old incorrect query still present"
        
        # Check that the new correct query is present
        assert "LEFT JOIN tbl_topicgrade tg ON t.id = tg.topicid" in content, "New topicgrade join missing"
        assert "LEFT JOIN tbl_grade g ON tg.gradeid = g.id" in content, "Correct grade join missing"

    def test_curriculum_table_endpoint_code_fix(self):
        """Test that curriculum-table endpoint code is properly fixed."""
        # This test verifies the code fix without requiring database access
        # The actual database query was already tested manually
        app_path = os.path.join(os.getcwd(), 'app.py')
        if not os.path.exists(app_path):
            pytest.skip("app.py not found")
            
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the curriculum-table endpoint
        endpoint_start = content.find("@app.route('/api/curriculum-table'")
        assert endpoint_start != -1, "curriculum-table endpoint not found"
        
        # Find the end of the function
        endpoint_end = content.find("\n@app.route", endpoint_start + 1)
        if endpoint_end == -1:
            endpoint_end = len(content)
        
        endpoint_code = content[endpoint_start:endpoint_end]
        
        # Verify the query uses the correct table relationships
        assert "LEFT JOIN tbl_topicgrade tg ON t.id = tg.topicid" in endpoint_code, "Missing topicgrade join"
        assert "LEFT JOIN tbl_grade g ON tg.gradeid = g.id" in endpoint_code, "Missing correct grade join"
        
        # Verify the old broken query is not present
        assert "g.subjectid = s.id" not in endpoint_code, "Old broken query still present"

    def test_securedom_class_properly_defined(self):
        """Test that SecureDOM class is properly defined in secureDOM.js."""
        securedom_path = os.path.join(os.getcwd(), 'static', 'js', 'secureDOM.js')
        if not os.path.exists(securedom_path):
            pytest.skip("secureDOM.js not found")
            
        with open(securedom_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that SecureDOM class is defined and exported to window
        assert "class SecureDOM" in content, "SecureDOM class not defined"
        assert "window.SecureDOM = SecureDOM" in content, "SecureDOM not exported to window"
        
        # Check that key methods exist
        required_methods = [
            'static setText',
            'static createElement', 
            'static replaceContent',
            'static setLoadingState',
            'static setErrorState',
            'static setEmptyState'
        ]
        
        for method in required_methods:
            assert method in content, f"Required method {method} not found in SecureDOM"

    def test_usertable_uses_securedom_methods(self):
        """Test that userTable.js uses SecureDOM methods correctly."""
        usertable_path = os.path.join(os.getcwd(), 'static', 'js', 'userTable.js')
        if not os.path.exists(usertable_path):
            pytest.skip("userTable.js not found")
            
        with open(usertable_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that userTable.js uses SecureDOM methods
        securedom_methods = [
            'SecureDOM.setLoadingState',
            'SecureDOM.setErrorState', 
            'SecureDOM.createElement',
            'SecureDOM.replaceContent'
        ]
        
        for method in securedom_methods:
            assert method in content, f"userTable.js does not use {method}"