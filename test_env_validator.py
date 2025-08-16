import os
import pytest
from unittest.mock import patch
from env_validator import EnvironmentValidator, validate_environment


class TestEnvironmentValidator:
    
    def setup_method(self):
        """Clear environment variables before each test."""
        env_vars = [
            'DATABASE_URL', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME',
            'SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'SENDER_EMAIL',
            'FRONTEND_BASE_URL', 'ADMIN_PASSWORD'
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def test_database_config_with_database_url(self):
        """Test database validation with DATABASE_URL."""
        os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/db'
        validator = EnvironmentValidator()
        errors = validator.validate_database_config()
        assert errors == []
    
    def test_database_config_with_individual_vars(self):
        """Test database validation with individual DB_* variables."""
        os.environ.update({
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'testdb'
        })
        validator = EnvironmentValidator()
        errors = validator.validate_database_config()
        assert errors == []
    
    def test_database_config_missing_vars(self):
        """Test database validation with missing variables."""
        os.environ.update({
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass'
            # Missing DB_HOST, DB_PORT, DB_NAME
        })
        validator = EnvironmentValidator()
        errors = validator.validate_database_config()
        assert len(errors) == 1
        assert 'DB_HOST, DB_PORT, DB_NAME' in errors[0]
    
    def test_smtp_config_valid(self):
        """Test SMTP validation with all required variables."""
        os.environ.update({
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'test@gmail.com',
            'SMTP_PASSWORD': 'password'
        })
        validator = EnvironmentValidator()
        errors = validator.validate_smtp_config()
        assert errors == []
    
    def test_smtp_config_missing_vars(self):
        """Test SMTP validation with missing variables."""
        os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
        # Missing SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
        validator = EnvironmentValidator()
        errors = validator.validate_smtp_config()
        assert len(errors) == 1
        assert 'SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD' in errors[0]
    
    def test_smtp_port_invalid(self):
        """Test SMTP port validation with invalid port."""
        os.environ.update({
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_PORT': 'invalid',
            'SMTP_USERNAME': 'test@gmail.com',
            'SMTP_PASSWORD': 'password'
        })
        validator = EnvironmentValidator()
        errors = validator.validate_smtp_config()
        assert any('valid integer' in error for error in errors)
    
    def test_smtp_port_out_of_range(self):
        """Test SMTP port validation with out of range port."""
        os.environ.update({
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_PORT': '70000',
            'SMTP_USERNAME': 'test@gmail.com',
            'SMTP_PASSWORD': 'password'
        })
        validator = EnvironmentValidator()
        errors = validator.validate_smtp_config()
        assert any('valid port number' in error for error in errors)
    
    @patch('sys.exit')
    def test_validate_all_fail_fast(self, mock_exit):
        """Test validate_all with fail_fast=True."""
        # No environment variables set
        validator = EnvironmentValidator()
        result = validator.validate_all(fail_fast=True)
        mock_exit.assert_called_once_with(1)
    
    def test_validate_all_no_fail_fast(self):
        """Test validate_all with fail_fast=False."""
        # No environment variables set
        validator = EnvironmentValidator()
        result = validator.validate_all(fail_fast=False)
        assert result is False
    
    def test_validate_all_success(self):
        """Test validate_all with all required variables."""
        os.environ.update({
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db',
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'test@gmail.com',
            'SMTP_PASSWORD': 'password'
        })
        validator = EnvironmentValidator()
        result = validator.validate_all(fail_fast=False)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])