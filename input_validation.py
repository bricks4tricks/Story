"""
Enhanced input validation utilities for secure API endpoints.
Provides decorators and validation functions to prevent injection attacks.
"""

import re
import json
from functools import wraps
from flask import request, jsonify
from security_utils import sanitizer
from typing import Dict, Any, Optional, List, Union


class ValidationError(Exception):
    """Custom validation error."""
    pass


class InputValidator:
    """Comprehensive input validation with security focus."""
    
    # Common patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
    PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\?]).{8,128}$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9\s]{1,100}$')
    
    @staticmethod
    def validate_json_input(data: Any) -> Dict[str, Any]:
        """Validate and sanitize JSON input."""
        if data is None:
            raise ValidationError("Invalid or missing JSON data")
        
        if not isinstance(data, dict):
            raise ValidationError("JSON data must be an object")
        
        # Prevent deep nesting attacks
        if len(json.dumps(data)) > 10000:  # 10KB limit
            raise ValidationError("JSON payload too large")
        
        return data
    
    @staticmethod
    def validate_string_field(value: Any, field_name: str, required: bool = True, 
                            max_length: int = 500, pattern: Optional[str] = None,
                            min_length: int = 0) -> Optional[str]:
        """Validate string field with comprehensive checks."""
        if value is None or (isinstance(value, str) and value.strip() == ''):
            if required:
                raise ValidationError(f"{field_name} is required")
            return None
        
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        # Length validation
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} exceeds maximum length of {max_length}")
        
        # Pattern validation
        if pattern and not re.match(pattern, value):
            raise ValidationError(f"{field_name} contains invalid characters")
        
        # XSS prevention
        sanitized_value = sanitizer.sanitize_html(value.strip())
        
        return sanitized_value
    
    @staticmethod
    def validate_email(email: Any) -> str:
        """Validate email address."""
        validated = InputValidator.validate_string_field(
            email, "email", required=True, max_length=254, 
            pattern=InputValidator.EMAIL_PATTERN.pattern
        )
        return validated.lower()
    
    @staticmethod
    def validate_username(username: Any) -> str:
        """Validate username."""
        return InputValidator.validate_string_field(
            username, "username", required=True, min_length=3, max_length=30,
            pattern=InputValidator.USERNAME_PATTERN.pattern
        )
    
    @staticmethod
    def validate_password(password: Any) -> str:
        """Validate password strength."""
        validated = InputValidator.validate_string_field(
            password, "password", required=True, min_length=8, max_length=128
        )
        
        if not InputValidator.PASSWORD_PATTERN.match(validated):
            raise ValidationError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )
        
        return validated
    
    @staticmethod
    def validate_integer(value: Any, field_name: str, required: bool = True,
                        min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
        """Validate integer field."""
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required")
            return None
        
        try:
            int_val = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer")
        
        if min_val is not None and int_val < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}")
        
        if max_val is not None and int_val > max_val:
            raise ValidationError(f"{field_name} must be at most {max_val}")
        
        return int_val
    
    @staticmethod
    def validate_choice(value: Any, field_name: str, choices: List[str], 
                       required: bool = True) -> Optional[str]:
        """Validate value against allowed choices."""
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required")
            return None
        
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        if value not in choices:
            raise ValidationError(f"{field_name} must be one of: {', '.join(choices)}")
        
        return value


def validate_json_input(required_fields: Optional[List[str]] = None,
                       optional_fields: Optional[List[str]] = None,
                       max_payload_size: int = 10000):
    """Decorator for JSON input validation."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Check content type
                if not request.is_json:
                    return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 400
                
                # Get and validate JSON data
                data = request.get_json(silent=True)
                data = InputValidator.validate_json_input(data)
                
                # Validate required fields
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return jsonify({
                            "status": "error", 
                            "message": f"Missing required fields: {', '.join(missing_fields)}"
                        }), 400
                
                # Remove unexpected fields for security
                allowed_fields = (required_fields or []) + (optional_fields or [])
                if allowed_fields:
                    data = {k: v for k, v in data.items() if k in allowed_fields}
                
                # Add validated data to request context
                request.validated_data = data
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({"status": "error", "message": str(e)}), 400
            except Exception as e:
                print(f"Input validation error: {e}")
                return jsonify({"status": "error", "message": "Invalid input data"}), 400
        
        return decorated_function
    return decorator


def validate_user_registration():
    """Decorator specifically for user registration validation."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = getattr(request, 'validated_data', request.get_json())
                
                # Validate username
                data['username'] = InputValidator.validate_username(data.get('username'))
                
                # Validate email
                data['email'] = InputValidator.validate_email(data.get('email'))
                
                # Validate password
                data['password'] = InputValidator.validate_password(data.get('password'))
                
                # Validate optional plan
                if 'plan' in data and data['plan']:
                    data['plan'] = InputValidator.validate_choice(
                        data['plan'], 'plan', ['Monthly', 'Yearly'], required=False
                    )
                
                request.validated_data = data
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({"status": "error", "message": str(e)}), 400
        
        return decorated_function
    return decorator


# Global validator instance
validator = InputValidator()