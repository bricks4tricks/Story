"""
LogicAndStories Flask Application.

Simplified main application file using the application factory pattern.
Most functionality has been moved to modular blueprints and utilities.
"""

import os
from app_factory import create_app
from env_validator import validate_environment

# Validate environment variables before application setup (skip during testing)
if not os.environ.get('PYTEST_CURRENT_TEST'):
    validate_environment(fail_fast=True)

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Development server configuration
    debug = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    # Use secure host binding - only bind to all interfaces in production with proper setup
    host = '127.0.0.1'  # Default to localhost for security
    if os.environ.get('FLASK_ENV') == 'production' and os.environ.get('ALLOW_EXTERNAL_ACCESS') == 'true':
        host = '0.0.0.0'  # Only bind to all interfaces if explicitly allowed in production
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )