"""
Centralized error handling for LogicAndStories application.

This module provides custom exception classes and error handlers
to improve error handling consistency and security.
"""

import traceback
import logging
from typing import Dict, Any, Optional, Tuple
from flask import jsonify, request
from werkzeug.exceptions import HTTPException


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LogicAndStoriesError(Exception):
    """Base exception class for application errors."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ValidationError(LogicAndStoriesError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message, 400, details)
        self.field = field


class AuthenticationError(LogicAndStoriesError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class AuthorizationError(LogicAndStoriesError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, 403)


class NotFoundError(LogicAndStoriesError):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found", resource_type: Optional[str] = None):
        super().__init__(message, 404)
        self.resource_type = resource_type


class RateLimitError(LogicAndStoriesError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429)


class DatabaseError(LogicAndStoriesError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed", operation: Optional[str] = None):
        super().__init__(message, 500)
        self.operation = operation


def safe_error_response(error: Exception, include_details: bool = False) -> Tuple[Dict[str, Any], int]:
    """Generate a safe error response that doesn't leak sensitive information."""
    
    # Determine if we're in development mode
    is_development = request.environ.get('FLASK_ENV') == 'development'
    
    if isinstance(error, LogicAndStoriesError):
        response = {
            "status": "error",
            "message": error.message,
            "error_type": error.__class__.__name__
        }
        
        # Include details only in development or if explicitly requested
        if (is_development or include_details) and error.details:
            response["details"] = error.details
        
        # Log the error for debugging
        logger.warning(f"{error.__class__.__name__}: {error.message}", extra={
            "status_code": error.status_code,
            "details": error.details,
            "request_path": request.path if request else None
        })
        
        return response, error.status_code
    
    elif isinstance(error, HTTPException):
        response = {
            "status": "error",
            "message": error.description or "HTTP error occurred",
            "error_type": "HTTPException"
        }
        
        logger.warning(f"HTTP {error.code}: {error.description}", extra={
            "status_code": error.code,
            "request_path": request.path if request else None
        })
        
        return response, error.code
    
    else:
        # Generic error - don't expose internal details
        response = {
            "status": "error",
            "message": "An unexpected error occurred",
            "error_type": "InternalError"
        }
        
        # Log the full error details for debugging
        logger.error(f"Unhandled exception: {str(error)}", extra={
            "exception_type": error.__class__.__name__,
            "traceback": traceback.format_exc() if is_development else None,
            "request_path": request.path if request else None
        })
        
        # In development, include more details
        if is_development:
            response["details"] = {
                "exception_type": error.__class__.__name__,
                "exception_message": str(error)
            }
        
        return response, 500


def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    @app.errorhandler(LogicAndStoriesError)
    def handle_app_error(error):
        response, status_code = safe_error_response(error)
        return jsonify(response), status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        response, status_code = safe_error_response(error, include_details=True)
        if error.field:
            response["field"] = error.field
        return jsonify(response), status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        response, status_code = safe_error_response(error)
        return jsonify(response), status_code
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        response, status_code = safe_error_response(error)
        return jsonify(response), status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            "status": "error",
            "message": "Page not found",
            "error_type": "NotFound"
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "error_type": "InternalError"
        }), 500


# Validation helper functions
def validate_required_fields(data: Dict, required_fields: list) -> None:
    """Validate that all required fields are present and not empty."""
    missing = []
    empty = []
    
    for field in required_fields:
        if field not in data:
            missing.append(field)
        elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            empty.append(field)
    
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")
    
    if empty:
        raise ValidationError(f"Empty required fields: {', '.join(empty)}")


def validate_integer_range(value: Any, field_name: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """Validate that a value is an integer within the specified range."""
    try:
        int_val = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid integer", field=field_name)
    
    if min_val is not None and int_val < min_val:
        raise ValidationError(f"{field_name} must be at least {min_val}", field=field_name)
    
    if max_val is not None and int_val > max_val:
        raise ValidationError(f"{field_name} must be at most {max_val}", field=field_name)
    
    return int_val


def validate_string_length(value: str, field_name: str, min_len: int = 0, max_len: int = 1000) -> str:
    """Validate string length constraints."""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field=field_name)
    
    if len(value) < min_len:
        raise ValidationError(f"{field_name} must be at least {min_len} characters", field=field_name)
    
    if len(value) > max_len:
        raise ValidationError(f"{field_name} must be at most {max_len} characters", field=field_name)
    
    return value


def validate_choice(value: Any, field_name: str, choices: list) -> Any:
    """Validate that a value is one of the allowed choices."""
    if value not in choices:
        raise ValidationError(f"{field_name} must be one of: {', '.join(map(str, choices))}", field=field_name)
    
    return value