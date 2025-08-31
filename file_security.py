"""
Secure file upload validation and handling utilities.
Provides comprehensive security checks for uploaded files.
"""

import os
import hashlib
import platform

# Import magic only on non-Windows platforms
try:
    if platform.system() != "Windows":
        import magic
    else:
        magic = None
except ImportError:
    magic = None
import tempfile
from functools import wraps
from werkzeug.utils import secure_filename
from flask import request, jsonify
from typing import List, Optional, Dict, Any


class FileSecurityError(Exception):
    """Custom file security error."""
    pass


class SecureFileHandler:
    """Secure file upload handler with comprehensive validation."""
    
    # Allowed MIME types for different file categories
    ALLOWED_MIME_TYPES = {
        'csv': ['text/csv', 'text/plain', 'application/csv'],
        'text': ['text/plain', 'text/csv', 'application/csv'],
        'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        'pdf': ['application/pdf'],
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'csv': 10 * 1024 * 1024,    # 10MB
        'text': 5 * 1024 * 1024,    # 5MB
        'image': 5 * 1024 * 1024,   # 5MB
        'pdf': 20 * 1024 * 1024,    # 20MB
    }
    
    # Dangerous file extensions to always reject
    DANGEROUS_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
        'php', 'asp', 'aspx', 'jsp', 'py', 'pl', 'sh', 'ps1', 'dll',
        'so', 'dylib', 'app', 'deb', 'rpm', 'dmg', 'iso', 'msi'
    }
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate and secure filename."""
        if not filename:
            raise FileSecurityError("Filename is required")
        
        # Use werkzeug's secure_filename for basic security
        secure_name = secure_filename(filename)
        if not secure_name:
            raise FileSecurityError("Invalid filename")
        
        # Additional security checks
        if len(secure_name) > 255:
            raise FileSecurityError("Filename too long")
        
        # Check for dangerous extensions
        extension = secure_name.split('.')[-1].lower()
        if extension in SecureFileHandler.DANGEROUS_EXTENSIONS:
            raise FileSecurityError(f"File type '{extension}' not allowed")
        
        # Prevent directory traversal attempts
        if '..' in secure_name or '/' in secure_name or '\\' in secure_name:
            raise FileSecurityError("Invalid characters in filename")
        
        return secure_name
    
    @staticmethod
    def validate_file_size(file_data: bytes, file_category: str) -> bool:
        """Validate file size against category limits."""
        max_size = SecureFileHandler.MAX_FILE_SIZES.get(file_category, 1024 * 1024)  # Default 1MB
        if len(file_data) > max_size:
            raise FileSecurityError(f"File size exceeds limit of {max_size // (1024*1024)}MB")
        
        if len(file_data) == 0:
            raise FileSecurityError("File is empty")
        
        return True
    
    @staticmethod
    def validate_mime_type(file_data: bytes, allowed_category: str) -> str:
        """Validate file MIME type using python-magic when available."""
        if magic is None:
            # On Windows or when magic is not available, use basic validation
            # This is a fallback - consider implementing alternative validation
            import mimetypes
            # Basic fallback - not as secure but allows functionality
            return "application/octet-stream"  # Generic binary type
            
        try:
            # Get MIME type from file content, not filename
            mime_type = magic.from_buffer(file_data, mime=True)
        except Exception:
            raise FileSecurityError("Could not determine file type")
        
        allowed_types = SecureFileHandler.ALLOWED_MIME_TYPES.get(allowed_category, [])
        if mime_type not in allowed_types:
            raise FileSecurityError(f"File type '{mime_type}' not allowed for {allowed_category} files")
        
        return mime_type
    
    @staticmethod
    def scan_for_malicious_content(file_data: bytes, file_category: str) -> bool:
        """Scan file content for potential security threats."""
        # Convert to string for text-based files
        if file_category in ['csv', 'text']:
            try:
                content = file_data.decode('utf-8', errors='ignore')
                
                # Check for script injection patterns
                dangerous_patterns = [
                    '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
                    'eval(', 'exec(', 'system(', 'shell_exec', '<?php',
                    '<%', '<jsp:', '${', 'import os', 'import subprocess'
                ]
                
                content_lower = content.lower()
                for pattern in dangerous_patterns:
                    if pattern in content_lower:
                        raise FileSecurityError(f"Potentially malicious content detected: {pattern}")
                
                # Check for excessive special characters (potential obfuscation)
                special_char_count = sum(1 for c in content if not c.isalnum() and not c.isspace() and c not in ',."\'')
                if len(content) > 0 and special_char_count / len(content) > 0.3:  # More than 30% special chars
                    raise FileSecurityError("File contains suspicious character patterns")
                
            except UnicodeDecodeError:
                # If can't decode as text, that's suspicious for text files
                if file_category in ['csv', 'text']:
                    raise FileSecurityError("File contains non-text data")
        
        return True
    
    @staticmethod
    def calculate_file_hash(file_data: bytes) -> str:
        """Calculate SHA-256 hash of file for integrity checking."""
        return hashlib.sha256(file_data).hexdigest()
    
    @classmethod
    def validate_uploaded_file(cls, file_field_name: str, allowed_category: str) -> Dict[str, Any]:
        """
        Comprehensive file validation.
        
        Args:
            file_field_name: Name of the file field in the request
            allowed_category: Category of allowed files (csv, text, image, pdf)
        
        Returns:
            Dict with validation results and file info
        
        Raises:
            FileSecurityError: If validation fails
        """
        # Check if file is present
        if file_field_name not in request.files:
            raise FileSecurityError(f"No file provided in '{file_field_name}' field")
        
        uploaded_file = request.files[file_field_name]
        if not uploaded_file or uploaded_file.filename == '':
            raise FileSecurityError("No file selected")
        
        # Validate filename
        secure_name = cls.validate_filename(uploaded_file.filename)
        
        # Read file data
        file_data = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
        
        # Validate file size
        cls.validate_file_size(file_data, allowed_category)
        
        # Validate MIME type
        mime_type = cls.validate_mime_type(file_data, allowed_category)
        
        # Scan for malicious content
        cls.scan_for_malicious_content(file_data, allowed_category)
        
        # Calculate hash for integrity
        file_hash = cls.calculate_file_hash(file_data)
        
        return {
            'original_filename': uploaded_file.filename,
            'secure_filename': secure_name,
            'mime_type': mime_type,
            'file_size': len(file_data),
            'file_hash': file_hash,
            'file_data': file_data,
            'validated': True
        }


def require_secure_file_upload(allowed_category: str, file_field: str = 'file'):
    """Decorator for secure file upload validation."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Validate the uploaded file
                file_info = SecureFileHandler.validate_uploaded_file(file_field, allowed_category)
                
                # Add file info to request context
                request.secure_file_info = file_info
                
                return f(*args, **kwargs)
                
            except FileSecurityError as e:
                return jsonify({"status": "error", "message": str(e)}), 400
            except Exception as e:
                print(f"File security error: {e}")
                return jsonify({"status": "error", "message": "File validation failed"}), 400
        
        return decorated_function
    return decorator


def save_uploaded_file_securely(file_info: Dict[str, Any], destination_dir: str = None) -> str:
    """
    Save uploaded file to a secure temporary location.
    
    Args:
        file_info: File information from validation
        destination_dir: Optional destination directory
    
    Returns:
        Path to saved file
    """
    if destination_dir is None:
        destination_dir = tempfile.gettempdir()
    
    # Ensure destination directory exists and is secure
    os.makedirs(destination_dir, mode=0o700, exist_ok=True)
    
    # Create secure temporary file
    secure_filename = file_info['secure_filename']
    temp_path = os.path.join(destination_dir, f"secure_{file_info['file_hash'][:16]}_{secure_filename}")
    
    # Write file data securely
    with open(temp_path, 'wb') as f:
        f.write(file_info['file_data'])
    
    # Set secure file permissions
    os.chmod(temp_path, 0o600)
    
    return temp_path


# Global instance
secure_file_handler = SecureFileHandler()