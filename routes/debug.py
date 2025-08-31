"""
Debug routes to help diagnose session issues.
Only available in development/testing environments.
"""

import os
from flask import Blueprint, jsonify, session, request
from datetime import datetime

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')


@debug_bp.route('/session-info', methods=['GET'])
def session_info():
    """Return current session information for debugging."""
    
    # Only allow in development/testing
    if not (os.environ.get('PYTEST_CURRENT_TEST') or 
            os.environ.get('FLASK_ENV') == 'development'):
        return jsonify({"error": "Not available in production"}), 403
    
    session_data = {
        "user_id": session.get('user_id'),
        "user_type": session.get('user_type'), 
        "session_token": session.get('session_token'),
        "session_keys": list(session.keys()),
        "timestamp": datetime.now().isoformat(),
        "request_headers": dict(request.headers),
        "cookies": request.cookies.to_dict()
    }
    
    return jsonify(session_data)