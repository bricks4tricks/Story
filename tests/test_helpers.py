"""
Common test helpers and dummy classes for LogicAndStories tests.
"""

import os
from unittest.mock import Mock


class DummyCursor:
    def __init__(self, rows=None, single_row=None, rowcount=1, question_count=0):
        self.rows = rows or []
        self.single_row = single_row
        self.rowcount = rowcount
        self.question_count = question_count
        self.query = ""
        self.params = None
        self.queries = []  # Track all executed queries
        self.executed = []  # Track (query, params) tuples
        
    def execute(self, query, params=None):
        self.query = str(query)
        self.params = params
        self.queries.append(str(query))
        self.executed.append((str(query), params))
        
    def fetchall(self):
        return self.rows
        
    def fetchone(self):
        if self.single_row is not None:
            return self.single_row
        if self.question_count is not None:
            return (self.question_count,)
        return None
        
    def close(self):
        pass


class DummyConnection:
    def __init__(self, rows=None, single_row=None, rowcount=1, user_exists=True, 
                 delete_rowcount=None, active=True, usertype="Student", parent_id=1,
                 has_subscription=True, question_count=0, curriculum_exists=True,
                 grade_exists=True):
        # Handle different initialization patterns from various test files
        if isinstance(rows, str):
            # For video/story tests that pass a URL string
            single_row = (rows,)
            rows = None
        elif hasattr(rows, '__iter__') and not isinstance(rows, (str, dict)):
            # Already a list/tuple of rows
            pass
        elif rows is not None:
            # Single row or dict
            single_row = rows
            rows = None
            
        self.cursor_obj = DummyCursor(
            rows=rows, 
            single_row=single_row,
            rowcount=delete_rowcount if delete_rowcount is not None else rowcount,
            question_count=question_count
        )
        
        # Properties for various test scenarios
        self.user_exists = user_exists
        self.active = active
        self.usertype = usertype
        self.parent_id = parent_id
        self.has_subscription = has_subscription
        self.curriculum_exists = curriculum_exists
        self.grade_exists = grade_exists
        self.autocommit = True
        
    def cursor(self, cursor_factory=None):
        return self.cursor_obj
        
    def commit(self):
        pass
        
    def rollback(self):
        pass
        
    def close(self):
        pass


# Mock authentication helpers
def mock_admin_auth():
    """Mock admin authentication for tests."""
    from unittest.mock import patch
    import os
    
    # Set environment variable to bypass auth
    def setup_mock():
        os.environ['MOCK_AUTH'] = 'true'
    
    def teardown_mock():
        if 'MOCK_AUTH' in os.environ:
            del os.environ['MOCK_AUTH']
    
    class MockAuthContext:
        def __enter__(self):
            setup_mock()
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            teardown_mock()
    
    return MockAuthContext()


def mock_student_auth():
    """Mock student authentication for tests.""" 
    from unittest.mock import patch
    return patch('auth_utils.require_auth', lambda allowed_types: lambda f: f)


def get_admin_headers():
    """Get headers for admin requests."""
    return {'Authorization': 'Bearer fake-admin-token'}


def get_student_headers():
    """Get headers for student requests."""
    return {'Authorization': 'Bearer fake-student-token'}


# Disable rate limiting for tests by setting environment variable
os.environ['TESTING'] = 'True'


def patch_db_connection(mock_connection):
    """Patch get_db_connection across multiple modules."""
    from unittest.mock import patch
    
    class MultiPatch:
        def __init__(self, connection):
            self.connection = connection
            self.patches = []
        
        def __enter__(self):
            # Patch all the different import paths where get_db_connection is used
            self.patches = [
                patch('app.get_db_connection', return_value=self.connection),
                patch('admin.get_db_connection', return_value=self.connection),
                patch('content.get_db_connection', return_value=self.connection),
                patch('db_utils.get_db_connection', return_value=self.connection)
            ]
            for p in self.patches:
                p.__enter__()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            for p in reversed(self.patches):
                p.__exit__(exc_type, exc_val, exc_tb)
    
    return MultiPatch(mock_connection)