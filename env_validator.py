import os
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv, find_dotenv

# Load .env file if present
load_dotenv(find_dotenv())


class EnvironmentValidator:
    """Validates required environment variables on application startup."""
    
    def __init__(self):
        self.required_vars = {
            # Database configuration (either DATABASE_URL or individual DB_* vars)
            'database': {
                'DATABASE_URL': {'required': False, 'description': 'Full database connection string'},
                'DB_USER': {'required': False, 'description': 'Database username'},
                'DB_PASSWORD': {'required': False, 'description': 'Database password'},
                'DB_HOST': {'required': False, 'description': 'Database host'},
                'DB_PORT': {'required': False, 'description': 'Database port'},
                'DB_NAME': {'required': False, 'description': 'Database name'},
            },
            # SMTP configuration (all required for email functionality)
            'smtp': {
                'SMTP_SERVER': {'required': True, 'description': 'SMTP server hostname'},
                'SMTP_PORT': {'required': True, 'description': 'SMTP server port'},
                'SMTP_USERNAME': {'required': True, 'description': 'SMTP username'},
                'SMTP_PASSWORD': {'required': True, 'description': 'SMTP password'},
                'SENDER_EMAIL': {'required': False, 'description': 'Email sender address (optional, defaults to SMTP_USERNAME)'},
            },
            # Application configuration
            'app': {
                'FRONTEND_BASE_URL': {'required': False, 'description': 'Frontend base URL (defaults to https://logicandstories.com)'},
                'ADMIN_PASSWORD': {'required': False, 'description': 'Admin password (optional, has default)'},
            }
        }
    
    def validate_database_config(self) -> List[str]:
        """Validate database configuration. Either DATABASE_URL or all DB_* vars must be present."""
        errors = []
        
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            return errors  # DATABASE_URL is sufficient
        
        # Check individual DB_* variables
        required_db_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
        missing_db_vars = [var for var in required_db_vars if not os.environ.get(var)]
        
        if missing_db_vars:
            errors.append(
                f"Database configuration incomplete. Either provide DATABASE_URL or all of: {', '.join(missing_db_vars)}"
            )
        
        return errors
    
    def validate_smtp_config(self) -> List[str]:
        """Validate SMTP configuration for email functionality."""
        errors = []
        smtp_vars = self.required_vars['smtp']
        
        missing_smtp = []
        for var, config in smtp_vars.items():
            if config['required'] and not os.environ.get(var):
                missing_smtp.append(var)
        
        if missing_smtp:
            errors.append(
                f"SMTP configuration incomplete. Missing required variables: {', '.join(missing_smtp)}"
            )
        
        # Validate SMTP_PORT is a valid integer
        smtp_port = os.environ.get('SMTP_PORT')
        if smtp_port:
            try:
                port_int = int(smtp_port)
                if port_int <= 0 or port_int > 65535:
                    errors.append("SMTP_PORT must be a valid port number (1-65535)")
            except (ValueError, TypeError):
                errors.append("SMTP_PORT must be a valid integer")
        
        return errors
    
    def validate_all(self, fail_fast: bool = True) -> bool:
        """
        Validate all environment variables.
        
        Args:
            fail_fast: If True, exit the application on validation failure
            
        Returns:
            True if all validations pass, False otherwise
        """
        errors = []
        
        # Validate database configuration
        errors.extend(self.validate_database_config())
        
        # Validate SMTP configuration
        errors.extend(self.validate_smtp_config())
        
        if errors:
            print("Environment Variable Validation Failed:")
            print("=" * 50)
            for error in errors:
                print(f"❌ {error}")
            
            print("\nRequired Environment Variables:")
            self._print_help()
            
            if fail_fast:
                print("\nApplication startup aborted due to configuration errors.")
                sys.exit(1)
            
            return False
        
        print("✅ Environment variable validation passed")
        return True
    
    def _print_help(self):
        """Print help information about required environment variables."""
        print("\nDatabase Configuration (choose one):")
        print("  Option 1: DATABASE_URL - Full connection string")
        print("  Option 2: Individual variables - DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME")
        
        print("\nSMTP Configuration (all required):")
        for var, config in self.required_vars['smtp'].items():
            required_text = "REQUIRED" if config['required'] else "OPTIONAL"
            print(f"  {var} - {config['description']} ({required_text})")
        
        print("\nApplication Configuration (optional):")
        for var, config in self.required_vars['app'].items():
            print(f"  {var} - {config['description']}")
        
        print("\nCreate a .env file in the project root with these variables for local development.")


def validate_environment(fail_fast: bool = True) -> bool:
    """Convenience function to validate environment variables."""
    validator = EnvironmentValidator()
    return validator.validate_all(fail_fast=fail_fast)


if __name__ == "__main__":
    validate_environment()