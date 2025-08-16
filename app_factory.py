"""
Application factory for LogicAndStories.

This module creates and configures the Flask application with all
necessary extensions, blueprints, and error handlers.
"""

import os
import re
from flask import Flask, request
from flask_cors import CORS

from config import get_config
from error_handlers import register_error_handlers
from extensions import bcrypt
from security_utils import csrf_protection, add_security_headers


def create_app(config_name=None):
    """Create and configure the Flask application."""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Initialize extensions
    bcrypt.init_app(app)
    csrf_protection.init_app(app)
    
    # Configure CORS
    CORS(app, 
         origins=app.config.get('CORS_ORIGINS', []),
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         headers=["Content-Type", "Authorization", "X-CSRF-Token"])
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register middleware
    register_middleware(app)
    
    # Initialize app with config
    config_class.init_app(app)
    
    return app


def register_blueprints(app):
    """Register all Flask blueprints."""
    
    # Authentication routes
    from auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Admin routes
    from admin import admin_bp
    app.register_blueprint(admin_bp)
    
    # Quiz routes
    from quiz import quiz_bp
    app.register_blueprint(quiz_bp)
    
    # Core routes
    from routes.core import core_bp
    app.register_blueprint(core_bp)
    
    # Admin user management routes
    from routes.admin_users import admin_users_bp
    app.register_blueprint(admin_users_bp)
    
    # Curriculum management routes
    from routes.curriculum import curriculum_bp
    app.register_blueprint(curriculum_bp)


def register_middleware(app):
    """Register middleware and request handlers."""
    
    @app.after_request
    def inject_security_and_preferences(response):
        """Add security headers and preferences script to responses."""
        # Add security headers
        response = add_security_headers(response)
        
        if response.direct_passthrough:
            return response

        content_type = response.headers.get('Content-Type', '').lower()
        if content_type.startswith('text/html'):
            script_tag = "<script src='/static/js/preferences.js'></script>"
            data = response.get_data(as_text=True)
            if script_tag not in data:
                new_data, count = re.subn(r'</body>', f'{script_tag}</body>', data, flags=re.IGNORECASE)
                if count:
                    response.set_data(new_data)
        return response
    
    @app.before_request
    def log_request_info():
        """Log request information for debugging."""
        if app.config.get('DEBUG'):
            app.logger.debug(f"Request: {request.method} {request.path}")
    
    return app