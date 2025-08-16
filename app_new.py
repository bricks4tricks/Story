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
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )