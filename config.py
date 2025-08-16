"""
Configuration management for LogicAndStories application.

Handles environment-specific settings for development, staging, and production.
Optimized for Render deployment with PostgreSQL.
"""

import os
import secrets
from datetime import timedelta
from typing import Dict, Any


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Session configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Database configuration for Render PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Render uses postgres://, but psycopg2 expects postgresql://
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Ensure SSL for managed PostgreSQL (Render requirement)
    if DATABASE_URL and 'sslmode' not in DATABASE_URL:
        connector = '&' if '?' in DATABASE_URL else '?'
        DATABASE_URL += f'{connector}sslmode=require'
    
    # Individual DB components (fallback)
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD') 
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME')
    
    # Email configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
    
    # Frontend URL
    FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', 'https://logicandstories.com')
    
    # CORS origins for Render deployment
    CORS_ORIGINS = [
        'https://logicandstories.com',
        'https://www.logicandstories.com'
    ]
    
    # Rate limiting settings
    RATE_LIMIT_STORAGE_URL = os.environ.get('REDIS_URL')  # Optional Redis for rate limiting
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Security settings
    CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY') or secrets.token_hex(32)
    
    @staticmethod
    def init_app(app):
        """Initialize app with this configuration."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    
    # Less restrictive CORS for development
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5000',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5000',
        'https://logicandstories.com',
        'https://www.logicandstories.com'
    ]
    
    # Database connection pool settings for development
    DB_POOL_MIN = 1
    DB_POOL_MAX = 5


class ProductionConfig(Config):
    """Production configuration for Render deployment."""
    
    DEBUG = False
    
    # Render-specific settings
    PORT = int(os.environ.get('PORT', 10000))  # Render uses PORT env var
    
    # Database connection pool settings for production
    DB_POOL_MIN = 2
    DB_POOL_MAX = 20
    
    # Enhanced security headers for production
    FORCE_HTTPS = True
    
    # Logging configuration for production
    LOG_TO_STDOUT = True
    
    @staticmethod
    def init_app(app):
        """Initialize production app."""
        Config.init_app(app)
        
        # Log to stdout for Render
        import logging
        from logging import StreamHandler
        
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    SESSION_COOKIE_SECURE = False
    
    # Use in-memory SQLite for testing
    DATABASE_URL = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])


def get_database_config() -> Dict[str, Any]:
    """Get database configuration optimized for Render PostgreSQL."""
    config_obj = get_config()
    
    # Prefer DATABASE_URL (Render standard)
    if config_obj.DATABASE_URL:
        return {
            'dsn': config_obj.DATABASE_URL,
            'pool_min': getattr(config_obj, 'DB_POOL_MIN', 2),
            'pool_max': getattr(config_obj, 'DB_POOL_MAX', 20)
        }
    
    # Fallback to individual components
    return {
        'user': config_obj.DB_USER,
        'password': config_obj.DB_PASSWORD,
        'host': config_obj.DB_HOST,
        'port': config_obj.DB_PORT,
        'database': config_obj.DB_NAME,
        'sslmode': 'require',  # Required for managed PostgreSQL
        'pool_min': getattr(config_obj, 'DB_POOL_MIN', 2),
        'pool_max': getattr(config_obj, 'DB_POOL_MAX', 20)
    }