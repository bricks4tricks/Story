import os
import psycopg2
import traceback
from dotenv import load_dotenv

# Load variables from a .env file if present. This allows developers to
# configure database credentials without hardcoding them in the source.
load_dotenv()

# Centralized database configuration
# Environment variables provide credentials; defaults support local dev.
db_config = {
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Dragon@123'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': os.environ.get('DB_PORT', '5432'),
    'database': os.environ.get('DB_NAME', 'educational_platform_db')
}


def get_db_connection():
    """Return a new database connection with error logging."""
    try:
        return psycopg2.connect(**db_config)
    except Exception as e:
        print(f"Database connection error: {e}")
        traceback.print_exc()
        raise
